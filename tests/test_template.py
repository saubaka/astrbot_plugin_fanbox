import json
import pathlib

from fanbox_core import (
    CARD_TEXT_MODES,
    DEFAULT_CARD_TEMPLATE,
    DEFAULT_TEMPLATE,
    IMAGE_VARIABLES,
    TEXT_VARIABLES,
    StyleOptions,
    build_variables,
    parse_post,
    card_messages,
    render_template,
    render_text_only,
    unknown_variables,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent


def make_post(**kw):
    raw = {
        "id": "100",
        "creatorId": "creator-a",
        "title": "テスト",
        "feeRequired": 500,
        "isRestricted": True,
        "hasAdultContent": False,
        "excerpt": "",
        "cover": {"type": "cover_image", "url": "https://pixiv.pximg.net/c/x.jpeg"},
        "tags": ["a", "b", "c"],
        "publishedDatetime": "2026-11-13T21:12:00+09:00",
        "updatedDatetime": "2026-11-14T09:00:00+09:00",
        "isPinned": False,
        "likeCount": 12,
        "commentCount": 3,
        "user": {
            "name": "サンプル作者",
            "userId": "1",
            "iconUrl": "https://pixiv.pximg.net/i.jpeg",
        },
    }
    raw.update(kw)
    return parse_post(raw)


def text_of(pieces):
    return "".join(v for k, v in pieces if k == "text")


def test_every_documented_variable_has_a_value_and_vice_versa():
    values = build_variables(make_post())
    assert set(values) == set(TEXT_VARIABLES)
    assert not set(values) & set(IMAGE_VARIABLES)


def test_default_template_paid_post():
    pieces = render_template(DEFAULT_TEMPLATE, build_variables(make_post()))
    assert pieces[-1] == ("image", "cover_image")
    assert text_of(pieces).splitlines() == [
        "【FANBOX】サンプル作者 发布了新帖",
        "《テスト》",
        "付费 · 500 日元及以上档位",
        "#a #b #c",
        "发布时间：2026-11-13 20:12（北京时间）",
        "https://creator-a.fanbox.cc/posts/100",
    ]


def test_show_fee_and_timezone_switches():
    post = make_post(hasAdultContent=True)
    opts = StyleOptions(show_fee=False, show_timezone=False, show_tags=False)
    values = build_variables(post, opts=opts)
    assert values["fee_text"] == values["fee_badge"] == ""
    assert values["fee"] == "500" and values["paid"] == "付费"
    assert values["labels"] == "R-18"
    assert values["published"] == "2026-11-13 20:12"
    assert values["timezone"] == "北京时间"
    assert values["tags"] == values["tags_plain"] == "" and values["tag_count"] == "0"
    lines = text_of(render_template(DEFAULT_TEMPLATE, values)).splitlines()
    assert "R-18" in lines and "发布时间：2026-11-13 20:12" in lines


def test_adult_mark_off_removes_label_line():
    values = build_variables(
        make_post(feeRequired=0, hasAdultContent=True),
        opts=StyleOptions(show_fee=False, show_adult_mark=False),
    )
    assert values["labels"] == ""
    assert "R-18" not in text_of(render_template(DEFAULT_TEMPLATE, values))


def test_custom_time_format_and_timezone():
    values = build_variables(
        make_post(), opts=StyleOptions(time_format="%m月%d日 %H:%M", offset_hours=9)
    )
    assert values["published"] == "11月13日 21:12（日本时间）"
    assert (
        values["published_date"] == "2026-11-13" and values["published_time"] == "21:12"
    )
    assert values["updated"].startswith("11月14日 09:00")
    assert (
        build_variables(make_post(), opts=StyleOptions(offset_hours=13))["timezone"]
        == "UTC+13"
    )


def test_conditional_line_and_auto_removed_lines():
    tpl = "A {title}\n?摘要：{excerpt}\n{excerpt}\n标签：{tags}\nB"
    pieces = render_template(tpl, build_variables(make_post(tags=[])))
    assert text_of(pieces) == "A テスト\n标签：\nB"


def test_escapes_and_unknown_variables():
    tpl = "{{title}} = {title} {nope} {{}}"
    assert (
        text_of(render_template(tpl, build_variables(make_post())))
        == "{title} = テスト {nope} {}"
    )
    assert unknown_variables(tpl + " {cover_image} {nope} {bad2}") == ["nope", "bad2"]
    assert unknown_variables(DEFAULT_TEMPLATE) == []


def test_images_keep_their_position():
    tpl = "{card_image}\n头：{avatar_image} {creator_name}\n{post_url}\n{cover_image}"
    pieces = render_template(tpl, build_variables(make_post()))
    assert [k for k, _ in pieces] == ["image", "text", "image", "text", "image"]
    assert pieces[1] == ("text", "头：")
    assert pieces[3][1].startswith(" サンプル作者\nhttps://")


def test_cover_url_hidden_when_not_allowed():
    assert build_variables(make_post(), cover_allowed=False)["cover_url"] == ""


def test_excerpt_variables():
    post = make_post(excerpt="一\n\n\n二" + "三" * 200)
    values = build_variables(post, opts=StyleOptions(excerpt_max=5))
    assert values["excerpt"] == "一\n二三三…"
    assert (
        values["excerpt_full"].startswith("一\n二")
        and len(values["excerpt_full"]) == 203
    )
    assert build_variables(post, opts=StyleOptions(excerpt_max=0))["excerpt"] == ""


def test_schema_template_and_readme_cover_every_variable():
    schema = json.loads((ROOT / "_conf_schema.json").read_text("utf-8"))
    tpl = schema["style"]["items"]["message_template"]
    assert tpl["type"] == "text"
    assert tpl["default"] == DEFAULT_TEMPLATE
    assert "README" in tpl["hint"] and len(tpl["hint"]) < 300  # 插件页里只列常用变量
    readme = (ROOT / "README.md").read_text("utf-8")
    for name in list(TEXT_VARIABLES) + list(IMAGE_VARIABLES):
        assert "| `{" + name + "}` |" in readme, name
    assert schema["style"]["items"]["push_style"]["options"] == ["text", "card"]
    assert schema["style"]["items"]["send_adult_cover"]["default"] is False
    start = schema["start"]["items"]
    assert start["start_from"]["default"] == "deploy"
    assert start["start_from"]["options"] == ["deploy", "subscribe", "custom"]
    assert start["max_post_age_hours"]["default"] == 0
    for section in schema.values():
        assert section["type"] == "object"
        for item in section["items"].values():
            assert "type" in item and "default" in item


def test_card_template_default_is_short_and_valid():
    assert unknown_variables(DEFAULT_CARD_TEMPLATE) == []
    text = render_text_only(DEFAULT_CARD_TEMPLATE, build_variables(make_post()))
    assert text.splitlines()[1] == "《テスト》"
    assert text.endswith("https://creator-a.fanbox.cc/posts/100")
    schema = json.loads((ROOT / "_conf_schema.json").read_text("utf-8"))
    items = schema["style"]["items"]
    assert items["card_template"]["default"] == DEFAULT_CARD_TEMPLATE
    assert items["card_template"]["type"] == "text"
    assert items["card_text"]["default"] == "merge"
    assert sorted(items["card_text"]["options"]) == sorted(CARD_TEXT_MODES)


def test_render_text_only_ignores_images():
    tpl = "{card_image}\n《{title}》 {cover_image}\n{avatar_image}\n{post_url}"
    text = render_text_only(tpl, build_variables(make_post()))
    assert text == "《テスト》\nhttps://creator-a.fanbox.cc/posts/100"


def test_card_messages_modes():
    card = b"JPEG"
    # 合成一条：文字在上、卡片图在下，同一条消息
    assert card_messages(card, "标题\n链接", "merge") == [
        [("text", "标题\n链接\n"), ("image", card)]
    ]
    # 分两条：先文字，再卡片图
    assert card_messages(card, "标题", "separate") == [
        [("text", "标题")],
        [("image", card)],
    ]
    # 只发卡片图；配文为空时也只发卡片图
    assert card_messages(card, "标题", "none") == [[("image", card)]]
    assert card_messages(card, "\n \n", "merge") == [[("image", card)]]
