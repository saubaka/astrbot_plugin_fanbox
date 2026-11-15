import pathlib

from fanbox_core import DEFAULT_TEMPLATE
from fanbox_settings import (
    INT_RANGES,
    build_settings,
    current_values,
    key_sections,
    load_schema,
    validate,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = load_schema()


def defaults():
    return current_values({}, SCHEMA)


def test_defaults_build_cleanly():
    s, warnings = build_settings(defaults())
    assert warnings == []
    assert s.poll_interval == 10 and s.push_style == "text" and s.start_from == "deploy"
    assert s.template == DEFAULT_TEMPLATE and s.template_is_default
    assert s.style.show_fee and s.style.offset_hours == 8


def test_current_values_reads_groups_and_legacy_flat_config():
    cfg = {"basic": {"poll_interval_minutes": 20}, "send_cover": False, "style": {}}
    vals = current_values(cfg, SCHEMA)
    assert vals["basic"]["poll_interval_minutes"] == 20
    assert vals["style"]["send_cover"] is False  # v0.1.0 的扁平配置
    assert vals["card"]["card_title_lines"] == 2  # 缺的用默认值


def test_validate_merges_only_known_items():
    merged, errors = validate(
        {
            "basic": {"poll_interval_minutes": 15},
            "style": {"push_style": "card", "send_cover": False},
        },
        SCHEMA,
        defaults(),
    )
    assert errors == []
    assert merged["basic"]["poll_interval_minutes"] == 15
    assert merged["style"]["push_style"] == "card"
    assert merged["content"] == defaults()["content"]


def test_validate_rejects_bad_values():
    cases = [
        ({"basic": {"poll_interval_minutes": 2}}, "不能小于 5"),
        ({"basic": {"poll_interval_minutes": True}}, "必须是整数"),
        ({"basic": {"poll_interval_minutes": "abc"}}, "必须是整数"),
        ({"style": {"push_style": "html"}}, "只能是"),
        ({"style": {"send_cover": "yes"}}, "开或关"),
        ({"content": {"timezone_offset_hours": 20}}, "不能大于 14"),
        ({"style": {"message_template": "x" * 5000}}, "太长"),
        ({"nope": {"a": 1}}, "未知的配置分组"),
        ({"basic": {"nope": 1}}, "未知的配置项"),
        ({"start": {"start_from": "custom", "start_time": "下周"}}, "自定义起点时间"),
        ("not a dict", "必须是"),
    ]
    for patch, needle in cases:
        _, errors = validate(patch, SCHEMA, defaults())
        assert any(needle in e for e in errors), (patch, errors)


def test_validate_accepts_numeric_strings_and_custom_start():
    merged, errors = validate(
        {
            "basic": {"poll_interval_minutes": "30"},
            "start": {"start_from": "custom", "start_time": "2026-11-15 08:00"},
        },
        SCHEMA,
        defaults(),
    )
    assert errors == [] and merged["basic"]["poll_interval_minutes"] == 30
    s, warnings = build_settings(merged)
    assert warnings == [] and s.custom_start_ts is not None


def test_build_settings_falls_back_with_warnings():
    vals = defaults()
    vals["style"]["push_style"] = "html"
    vals["style"]["message_template"] = "{oops} {title}"
    vals["start"]["start_from"] = "custom"
    vals["start"]["start_time"] = ""
    vals["basic"]["poll_interval_minutes"] = 1
    s, warnings = build_settings(vals)
    assert s.push_style == "text" and s.poll_interval == 5
    assert len(warnings) == 3


def test_every_int_item_has_a_range_and_ranges_match_schema():
    sections = key_sections(SCHEMA)
    ints = [
        k
        for g, body in SCHEMA.items()
        for k, item in body["items"].items()
        if item["type"] == "int"
    ]
    assert sorted(ints) == sorted(INT_RANGES)
    for k in INT_RANGES:
        assert k in sections


def test_readme_lists_every_setting():
    readme = (ROOT / "README.md").read_text("utf-8")
    for key in key_sections(SCHEMA):
        assert f"`{key}`" in readme, key


def test_page_files_exist():
    page = ROOT / "pages" / "dashboard"
    for name in ("index.html", "style.css", "app.js"):
        assert (page / name).is_file()
    html = (page / "index.html").read_text("utf-8")
    assert "./app.js" in html and "./style.css" in html
    # AstrBot 会把桥接脚本插到 </body> 前；必须自己在 app.js 之前引用，
    # 否则页面脚本运行时还没有 window.AstrBotPluginPage
    assert html.index("/api/plugin/page/bridge-sdk.js") < html.index("./app.js")
    css = (page / "style.css").read_text("utf-8")
    assert "@keyframes enterRvSafe" in css  # Safari 重影修复
    for lang in ("zh-CN", "en-US"):
        assert (ROOT / ".astrbot-plugin" / "i18n" / f"{lang}.json").is_file()
