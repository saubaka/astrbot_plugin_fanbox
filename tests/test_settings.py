import pathlib

from fanbox_core import DEFAULT_CARD_TEMPLATE, DEFAULT_TEMPLATE
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
    assert s.card_text == "merge" and s.card_template == DEFAULT_CARD_TEMPLATE
    assert s.card_template_is_default
    assert s.creator_cover_fallback  # 没封面时默认用创作者主页封面


def test_card_text_settings():
    vals = defaults()
    vals["style"]["card_text"] = "separate"
    vals["style"]["card_template"] = "{title} {nope}\n{card_image}"
    s, warnings = build_settings(vals)
    assert (
        s.card_text == "separate" and s.card_template == "{title} {nope}\n{card_image}"
    )
    assert not s.card_template_is_default
    assert len(warnings) == 1 and "卡片图配文模板" in warnings[0]
    vals["style"]["card_text"] = "both"
    vals["style"]["card_template"] = ""
    s, warnings = build_settings(vals)
    assert s.card_text == "merge" and s.card_template == DEFAULT_CARD_TEMPLATE
    assert len(warnings) == 1 and "配文方式" in warnings[0]
    _, errors = validate({"style": {"card_text": "both"}}, SCHEMA, defaults())
    assert any("只能是" in e for e in errors)


def test_card_template_must_keep_one_card_element():
    for bad in ("{title}\n{post_url}", "{card_image}{card_image}"):
        _, errors = validate({"style": {"card_template": bad}}, SCHEMA, defaults())
        assert any("{card_image}" in e for e in errors), bad
    for ok in ("", "{card_image}\n{post_url}"):
        _, errors = validate({"style": {"card_template": ok}}, SCHEMA, defaults())
        assert errors == [], ok


def test_old_card_template_gets_card_element():
    # v0.6.0 存下来的配文模板没有 {card_image}：读出时补在末尾，卡片图仍在文字下方
    cfg = {"style": {"card_template": "{creator_name}\n发布了新的FANBOX文章：\n\n"}}
    vals = current_values(cfg, SCHEMA)
    assert (
        vals["style"]["card_template"]
        == "{creator_name}\n发布了新的FANBOX文章：\n{card_image}"
    )
    s, warnings = build_settings(vals)
    assert warnings == [] and s.card_template.endswith("{card_image}")
    # 读出来的值再提交其他修改，校验能通过
    _, errors = validate({"style": {"push_style": "card"}}, SCHEMA, vals)
    assert errors == []


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
    # v0.5.0：左上角分区切换、右侧章节栏、实时预览、推送记录卡片
    for tab in ("overview", "records", "subs", "style", "settings"):
        assert f'data-tab="{tab}"' in html and f'id="panel-{tab}"' in html
    for needed in (
        'id="chapters"',
        'id="pvUrl"',
        'id="previewDock"',
        'id="recordView"',
        'id="pvSend"',
    ):
        assert needed in html, needed
    js = (page / "app.js").read_text("utf-8")
    for needed in (
        "function rebuildChapters",
        "function runPreview",
        "function fbCard",
        "function updateStyleRows",
        "card_template",
        "res.messages",
        "把卡片图移到光标处",
        "keepFirstCard",
        "data-chapter",
    ):
        assert needed in js, needed
    for lang in ("zh-CN", "en-US"):
        assert (ROOT / ".astrbot-plugin" / "i18n" / f"{lang}.json").is_file()


def test_page_uses_only_the_light_palette():
    """插件页只用一种淡蓝 + 浅粉 + 暖浅灰（和 X 推送插件页、状态页统一），不能混进深蓝、深紫等深色。"""
    import re

    allowed = set(
        "#f8f6f7 #f2eff1 #fcfbfb #ffffff #faf8f9 #ece8ea #e1dcdf #ebe6e9 #5a5458 #8a8387 #a29ba0 "
        "#f6fafe #eaf4fc #d9ecfa #c1dff6 #a8d2f3 #8cc2ee #fef7fa #fdeef3 #fadbe5 #f6c3d4 #f0a0ba "
        "#e4dfe2 #968e93 #fad9e3 #f6b3c8 #fef4f7 #fdeaf0 #fff".split()
    )
    allowed_rgba = (
        "rgba(255,255,255",
        "rgba(150,130,140",
        "rgba(253,234,240",
        "rgba(var(--veil)",
    )
    page = ROOT / "pages" / "dashboard"
    bad = []
    for name in ("style.css", "app.js", "index.html"):
        for n, line in enumerate((page / name).read_text("utf-8").splitlines(), 1):
            for m in re.finditer(
                r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)|hsla?\([^)]*\)",
                line,
            ):
                v = m.group(0).lower().replace(" ", "")
                if v in allowed or v.startswith(allowed_rgba):
                    continue
                if v == "#000" and "mask" in line:  # 只用作遮罩
                    continue
                bad.append(f"{name}:{n} {v}")
            if re.search(r"--blue-[6-9]00", line):
                bad.append(f"{name}:{n} 深色蓝阶")
    assert not bad, bad
