import io

import pytest

PIL = pytest.importorskip("PIL")
from PIL import Image  # noqa: E402

import fanbox_card  # noqa: E402
from fanbox_card import CardOptions, FontSet, render_card, wrap  # noqa: E402
from fanbox_core import parse_post  # noqa: E402

REGULAR = fanbox_card._first_existing(fanbox_card.CJK_REGULAR)
pytestmark = pytest.mark.skipif(REGULAR is None, reason="没有 Noto Sans CJK 字体")


def make_post(**kw):
    raw = {
        "id": "100",
        "creatorId": "creator-a",
        "title": "#12 新作イラストとメイキング・グッズの案内など",
        "feeRequired": 500,
        "isRestricted": True,
        "hasAdultContent": False,
        "excerpt": "",
        "cover": {"type": "cover_image", "url": "https://pixiv.pximg.net/c/x.jpeg"},
        "tags": [],
        "publishedDatetime": "2026-11-13T21:12:00+09:00",
        "likeCount": 12,
        "user": {"name": "テスト作者", "userId": "1", "iconUrl": ""},
    }
    raw.update(kw)
    return parse_post(raw)


def jpeg(color, size):
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "JPEG")
    return buf.getvalue()


def decode(data):
    img = Image.open(io.BytesIO(data))
    assert img.format == "JPEG"
    return img


def test_render_basic_card_size_and_cover():
    data = render_card(
        make_post(), "", jpeg((200, 30, 30), (1200, 630)), jpeg((0, 0, 255), (160, 160))
    )
    img = decode(data).convert("RGB")
    assert img.width == 1430
    # 封面区域是封面颜色，页面背景是浅灰
    r, g, b = img.getpixel((715, 300))
    assert r > 150 and g < 80 and b < 80
    assert img.getpixel((3, 3)) == pytest.approx(fanbox_card.PAGE_BG, abs=3)


def test_excerpt_and_likes_change_height():
    base = decode(render_card(make_post(), "", None, None)).height
    with_excerpt = decode(
        render_card(make_post(excerpt="本文" * 200), "", None, None)
    ).height
    no_likes = decode(
        render_card(make_post(), "", None, None, CardOptions(show_likes=False))
    ).height
    assert with_excerpt > base > no_likes


def test_adult_cover_is_hidden():
    post = make_post(hasAdultContent=True)
    red = jpeg((220, 0, 0), (1200, 630))
    img = decode(
        render_card(post, "", red, None, CardOptions(hide_cover=True))
    ).convert("RGB")
    r, g, b = img.getpixel((200, 200))
    assert abs(r - g) < 20 and abs(g - b) < 20  # 灰色占位，不是红色封面


def test_bad_image_bytes_do_not_crash():
    data = render_card(make_post(), "", b"not an image", b"\x00\x01")
    assert decode(data).width == 1430


def test_wrap_truncates_with_ellipsis_and_drops_emoji():
    fs = FontSet(REGULAR, fanbox_card.FALLBACK_REGULAR, 28)
    lines = wrap("今年も無事冬コミ受かりました🎉" * 20, fs, 600, 2)
    assert len(lines) == 2
    assert lines[-1][-1][0] == "…"
    assert all(ch != "🎉" for line in lines for ch, _, _ in line)


def test_wrap_keeps_english_words_together():
    fs = FontSet(REGULAR, fanbox_card.FALLBACK_REGULAR, 28)
    lines = wrap("hello wonderful world " * 6, fs, 300, 10)
    for line in lines:
        text = "".join(ch for ch, _, _ in line)
        assert not text.startswith(("onderful", "orld", "ello"))
