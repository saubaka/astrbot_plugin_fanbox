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
    ensure_card_element,
    render_template,
    share_cover_url,
    unknown_variables,
    with_creator_cover,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
README_FILES = ("README.md", "README.zh-TW.md", "README.ja.md", "README.en.md")


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
    for readme_name in README_FILES:
        readme = (ROOT / readme_name).read_text("utf-8")
        for name in list(TEXT_VARIABLES) + list(IMAGE_VARIABLES):
            assert "| `{" + name + "}` |" in readme, (readme_name, name)
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


def card_msgs(template, mode="merge", card=b"JPEG"):
    pieces = render_template(template, build_variables(make_post()))
    return card_messages(pieces, card, mode)


def test_card_template_default_puts_text_above_the_card():
    assert unknown_variables(DEFAULT_CARD_TEMPLATE) == []
    assert DEFAULT_CARD_TEMPLATE.count("{card_image}") == 1
    schema = json.loads((ROOT / "_conf_schema.json").read_text("utf-8"))
    items = schema["style"]["items"]
    assert items["card_template"]["default"] == DEFAULT_CARD_TEMPLATE
    assert items["card_template"]["type"] == "text"
    assert items["card_text"]["default"] == "merge"
    assert sorted(items["card_text"]["options"]) == sorted(CARD_TEXT_MODES)
    # 默认：作者名和一句提示在卡片图上方，同一条消息
    [message] = card_msgs(DEFAULT_CARD_TEMPLATE)
    assert message == [
        ("text", "サンプル作者\n发布了新的FANBOX文章：\n"),
        ("image", b"JPEG"),
    ]


def test_ensure_card_element():
    assert ensure_card_element("") == ""  # 空 = 默认模板
    assert ensure_card_element("{title}\n{card_image}") == "{title}\n{card_image}"
    # 旧版（v0.6.0）没有卡片图元素：补在末尾，卡片图仍在文字下方
    assert (
        ensure_card_element("{creator_name}\n发布了新的FANBOX文章：\n\n")
        == "{creator_name}\n发布了新的FANBOX文章：\n{card_image}"
    )
    # 多了只留第一个
    assert (
        ensure_card_element("{card_image}\n{title}{card_image}")
        == "{card_image}\n{title}"
    )


def test_card_messages_modes():
    tpl = "上：{title}\n{card_image}\n下：{post_url}"
    card = b"JPEG"
    # 合成一条：上方文字 + 卡片图 + 下方文字，交界处补换行
    assert card_msgs(tpl, "merge") == [
        [
            ("text", "上：テスト\n"),
            ("image", card),
            ("text", "\n下：https://creator-a.fanbox.cc/posts/100"),
        ]
    ]
    # 拆开：上方文字、卡片图、下方文字各一条
    assert card_msgs(tpl, "separate") == [
        [("text", "上：テスト")],
        [("image", card)],
        [("text", "下：https://creator-a.fanbox.cc/posts/100")],
    ]
    # 只发卡片图
    assert card_msgs(tpl, "none") == [[("image", card)]]
    # 卡片图在最上面 / 最下面
    assert [k for k, _ in card_msgs("{card_image}\n{post_url}")[0]] == ["image", "text"]
    assert [k for k, _ in card_msgs("{title}\n{card_image}")[0]] == ["text", "image"]
    assert card_msgs("{card_image}", "separate") == [[("image", card)]]


def test_card_messages_ignores_other_images_and_keeps_card():
    # 其他图片变量忽略，行尾空格去掉
    [message] = card_msgs(
        "《{title}》 {cover_image}\n{card_image}\n{avatar_image}{post_url}"
    )
    assert message[0] == ("text", "《テスト》\n")
    assert message[2] == ("text", "\nhttps://creator-a.fanbox.cc/posts/100")
    # {card_image} 所在的条件行被删掉时，卡片图放在最后
    [message] = card_msgs("{title}\n?{card_image}{excerpt}")
    assert message == [("text", "テスト\n"), ("image", b"JPEG")]


CREATOR_COVER = "https://pixiv.pximg.net/c/1620x580_90_a2_g5/fanbox/public/images/creator/1/cover/abc.jpeg"


def test_share_cover_url_uses_the_1200x630_crop():
    assert (
        share_cover_url(CREATOR_COVER)
        == "https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public/images/creator/1/cover/abc.jpeg"
    )
    post_cover = "https://pixiv.pximg.net/c/1200x630_90_a2_g5/fanbox/public/images/post/1/cover/x.jpeg"
    assert share_cover_url(post_cover) == post_cover
    assert share_cover_url("https://example.com/a.jpeg") == "https://example.com/a.jpeg"
    assert share_cover_url("") == ""


def test_coverless_post_falls_back_to_creator_cover():
    # FANBOX 列表里没设封面的帖子 cover 是 null
    post = make_post(cover=None)
    assert post.cover_url == "" and not post.cover_from_creator
    fixed = with_creator_cover(post, CREATOR_COVER)
    assert fixed.cover_from_creator
    assert (
        "/c/1200x630_90_a2_g5/" in fixed.cover_url
        and "/creator/1/cover/" in fixed.cover_url
    )
    assert post.cover_url == ""  # 原对象不变
    # 模板里的 {cover_url} 也跟着用主页封面
    assert build_variables(fixed)["cover_url"] == fixed.cover_url
    # 拿不到主页封面：原样返回
    assert with_creator_cover(post, "") is post
    # 帖子自己有封面：不替换
    has_cover = make_post()
    assert with_creator_cover(has_cover, CREATOR_COVER) is has_cover
