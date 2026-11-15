import asyncio

import httpx
import pytest

from fanbox_api import FanboxAPI, FanboxBlocked, FanboxError, FanboxNotFound
from fanbox_core import (
    advance_state,
    format_post_text,
    format_ts,
    initial_state,
    parse_creator_id,
    parse_posts,
    parse_start_time,
    parse_timestamp,
    select_new_posts,
    start_floor,
    subscribed_at,
)


def raw_post(pid, ts, fee=0, adult=False, excerpt="", tags=None, cid="creator-a"):
    return {
        "id": str(pid),
        "creatorId": cid,
        "title": f"post {pid}",
        "feeRequired": fee,
        "isRestricted": fee > 0,
        "hasAdultContent": adult,
        "excerpt": excerpt,
        "cover": {
            "type": "cover_image",
            "url": f"https://pixiv.pximg.net/c/{pid}.jpeg",
        },
        "tags": tags or [],
        "publishedDatetime": ts,
        "isPinned": False,
        "user": {"name": "サンプル作者", "userId": "1", "iconUrl": ""},
    }


@pytest.mark.parametrize(
    "text,expected",
    [
        ("creator-a", "creator-a"),
        ("@Creator-A", "creator-a"),
        ("https://creator-a.fanbox.cc", "creator-a"),
        ("https://creator-a.fanbox.cc/posts/12927375", "creator-a"),
        ("creator-a.fanbox.cc/", "creator-a"),
        ("https://www.fanbox.cc/@another-creator/posts/1", "another-creator"),
        ("<https://www.fanbox.cc/@another-creator>", "another-creator"),
        ("https://www.fanbox.cc/", None),
        ("https://api.fanbox.cc/", None),
        ("", None),
        ("bad id!", None),
        ("https://evil.example/@x", None),
    ],
)
def test_parse_creator_id(text, expected):
    assert parse_creator_id(text) == expected


def test_parse_posts_skips_broken_items():
    posts = parse_posts(
        [raw_post(1, "2026-10-28T21:52:44+09:00"), {"id": "x"}, None, "s"]
    )
    assert [p.id for p in posts] == ["1"]
    p = posts[0]
    assert p.cover_url.endswith("1.jpeg")
    assert p.creator_name == "サンプル作者"
    assert p.url == "https://creator-a.fanbox.cc/posts/1"
    assert p.ts > 0


def ts(iso):
    return parse_timestamp(iso)


def posts_of(*items):
    return parse_posts([raw_post(pid, iso) for pid, iso in items])


OLD = (2, "2026-10-02T10:00:00+09:00"), (1, "2026-10-01T10:00:00+09:00")
NEW = (4, "2026-10-04T10:00:00+09:00"), (3, "2026-10-03T10:00:00+09:00")


def test_floor_blocks_posts_before_start_point():
    floor = ts("2026-10-02T12:00:00+09:00")  # 例如部署时间
    state = initial_state("サンプル作者", floor + 3600)
    assert state["seen"] == [] and state["subscribed_at"] == floor + 3600
    assert select_new_posts(posts_of(*OLD), state, floor) == []

    fresh = select_new_posts(posts_of(*NEW, *OLD), state, floor)
    assert [p.id for p in fresh] == ["3", "4"]  # 从旧到新

    state = advance_state(state, fresh)
    assert select_new_posts(posts_of(*NEW, *OLD), state, floor) == []
    assert state["seen"][:2] == ["4", "3"]


def test_deploy_mode_pushes_posts_between_deploy_and_subscribe():
    deployed = ts("2026-10-01T00:00:00+09:00")
    subscribed = ts("2026-10-05T00:00:00+09:00")
    state = initial_state("x", subscribed)
    deploy_floor = start_floor(
        "deploy", deployed_at=deployed, subscribed=subscribed, custom_ts=None
    )
    sub_floor = start_floor(
        "subscribe", deployed_at=deployed, subscribed=subscribed, custom_ts=None
    )
    everything = posts_of(*NEW, *OLD)
    assert [p.id for p in select_new_posts(everything, state, deploy_floor)] == [
        "1",
        "2",
        "3",
        "4",
    ]
    assert select_new_posts(everything, state, sub_floor) == []


def test_custom_floor_and_fallback():
    custom = ts("2026-10-03T00:00:00+09:00")
    kw = dict(deployed_at=1.0, subscribed=2.0)
    assert start_floor("custom", custom_ts=custom, **kw) == custom
    assert start_floor("custom", custom_ts=None, **kw) == 1.0  # 填错时退回部署时间
    assert start_floor("whatever", custom_ts=custom, **kw) == 1.0
    state = initial_state("x", 0)
    assert [p.id for p in select_new_posts(posts_of(*NEW, *OLD), state, custom)] == [
        "3",
        "4",
    ]


def test_max_age_hours():
    now = ts("2026-10-04T12:00:00+09:00")
    state = initial_state("x", 0)
    got = select_new_posts(posts_of(*NEW, *OLD), state, 0, now, max_age_hours=36)
    assert [p.id for p in got] == ["3", "4"]
    got = select_new_posts(posts_of(*NEW, *OLD), state, 0, now, max_age_hours=6)
    assert [p.id for p in got] == ["4"]


def test_old_v02_state_still_works():
    # v0.2.0 的订阅：没有 subscribed_at，last_ts 是订阅时的最新帖
    state = {"name": "x", "last_ts": ts(OLD[0][1]), "seen": ["2", "1"]}
    assert subscribed_at(state) == ts(OLD[0][1])
    got = select_new_posts(posts_of(*NEW, *OLD), state, subscribed_at(state))
    assert [p.id for p in got] == ["3", "4"]


@pytest.mark.parametrize(
    "text,offset,expected",
    [
        ("2026-11-15 08:00", 8, "2026-11-15T08:00:00+08:00"),
        ("2026-11-15 08:00:30", 9, "2026-11-15T08:00:30+09:00"),
        ("2026/11/15 08:00", 8, "2026-11-15T08:00:00+08:00"),
        ("2026-11-15", 8, "2026-11-15T00:00:00+08:00"),
        ("2026-11-15T08:00:00+09:00", 8, "2026-11-15T08:00:00+09:00"),
    ],
)
def test_parse_start_time(text, offset, expected):
    assert parse_start_time(text, offset) == ts(expected)


@pytest.mark.parametrize("text", ["", "   ", "明天", "2026-13-01", None])
def test_parse_start_time_invalid(text):
    assert parse_start_time(text, 8) is None


def test_deleted_post_does_not_resurface_old_ones():
    state = initial_state("x", 0)
    state = advance_state(
        state,
        posts_of((10, "2026-10-10T10:00:00+09:00"), (9, "2026-10-09T10:00:00+09:00")),
    )
    # 10 被删，更早的 8 挤进列表：不应当被当成新帖
    after_delete = posts_of(
        (9, "2026-10-09T10:00:00+09:00"), (8, "2026-10-08T10:00:00+09:00")
    )
    assert select_new_posts(after_delete, state) == []


def test_failed_send_keeps_post_for_retry():
    state = advance_state(initial_state("x", 0), posts_of(OLD[1]))
    assert advance_state(state, []) is state
    assert [p.id for p in select_new_posts(posts_of(*OLD), state)] == ["2"]


def test_same_timestamp_posts_are_both_sent_once():
    state = advance_state(initial_state("x", 0), posts_of(OLD[1]))
    now = posts_of((3, "2026-10-02T10:00:00+09:00"), (2, "2026-10-02T10:00:00+09:00"))
    fresh = select_new_posts(now, state)
    assert [p.id for p in fresh] == ["2", "3"]
    state = advance_state(state, fresh[:1])  # 只发出去了 2
    assert [p.id for p in select_new_posts(now, state)] == ["3"]


def test_format_ts():
    assert (
        format_ts(ts("2026-11-15T09:00:00+09:00"), 8) == "2026-11-15 08:00（北京时间）"
    )
    assert format_ts(0, 8) == "（未知）"


def test_seen_list_is_capped():
    posts = parse_posts(
        [raw_post(i, f"2026-10-01T10:{i % 60:02d}:00+09:00") for i in range(1, 80)]
    )
    state = advance_state({"last_ts": 0, "seen": []}, posts)
    assert len(state["seen"]) == 50


def test_format_free_post():
    p = parse_posts(
        [
            raw_post(
                5,
                "2026-11-06T16:00:00+09:00",
                excerpt="  第一行\n\n\n第二行 ",
                tags=["a", "b"],
            )
        ]
    )[0]
    text = format_post_text(p, "", excerpt_max=120, offset_hours=8)
    assert text.splitlines() == [
        "【FANBOX】サンプル作者 发布了新帖",
        "《post 5》",
        "免费公开",
        "第一行",
        "第二行",
        "#a #b",
        "发布时间：2026-11-06 15:00（北京时间）",
        "https://creator-a.fanbox.cc/posts/5",
    ]


def test_format_paid_adult_post_and_excerpt_limit():
    p = parse_posts(
        [
            raw_post(
                6, "2026-11-06T16:00:00+09:00", fee=500, adult=True, excerpt="あ" * 30
            )
        ]
    )[0]
    text = format_post_text(p, "テスト作者", excerpt_max=10, offset_hours=9)
    lines = text.splitlines()
    assert lines[0] == "【FANBOX】テスト作者 发布了新帖"
    assert lines[2] == "付费 · 500 日元及以上档位 · R-18"
    assert lines[3] == "あ" * 10 + "…"
    assert "（日本时间）" in text
    assert "あ" not in format_post_text(p, excerpt_max=0)


# ---------- HTTP 客户端 ----------


def make_api(handler):
    return FanboxAPI(transport=httpx.MockTransport(handler))


def run(coro):
    return asyncio.run(coro)


def test_api_sends_origin_and_parses_posts():
    seen = {}

    def handler(request):
        seen["origin"] = request.headers.get("origin")
        seen["cookie"] = request.headers.get("cookie")
        seen["params"] = dict(request.url.params)
        body = {"body": {"posts": [raw_post(1, "2026-10-01T10:00:00+09:00")]}}
        return httpx.Response(200, json=body)

    async def go():
        api = make_api(handler)
        try:
            return await api.list_posts("creator-a", 10)
        finally:
            await api.close()

    posts = run(go())
    assert len(posts) == 1
    assert seen["origin"] == "https://www.fanbox.cc"
    assert seen["cookie"] is None  # 不带登录
    assert seen["params"] == {"creatorId": "creator-a", "limit": "10"}


@pytest.mark.parametrize(
    "status,exc",
    [
        (400, FanboxNotFound),
        (404, FanboxNotFound),
        (403, FanboxBlocked),
        (500, FanboxError),
    ],
)
def test_api_error_mapping(status, exc):
    async def go():
        api = make_api(lambda r: httpx.Response(status, text="x"))
        try:
            await api.get_creator("zz")
        finally:
            await api.close()

    with pytest.raises(exc):
        run(go())


def test_api_rejects_non_json():
    async def go():
        api = make_api(lambda r: httpx.Response(200, text="<html>"))
        try:
            await api.list_posts("zz")
        finally:
            await api.close()

    with pytest.raises(FanboxError):
        run(go())


def test_download_image_only_pximg():
    calls = []

    def handler(request):
        calls.append(str(request.url))
        return httpx.Response(200, content=b"\xff\xd8jpeg")

    async def go(url):
        api = make_api(handler)
        try:
            return await api.download_image(url)
        finally:
            await api.close()

    assert run(go("https://pixiv.pximg.net/c/a.jpeg")) == b"\xff\xd8jpeg"
    for bad in [
        "http://pixiv.pximg.net/a.jpeg",
        "https://downloads.fanbox.cc/a.jpeg",
        "https://pximg.net.evil.com/a",
    ]:
        with pytest.raises(FanboxError):
            run(go(bad))
    assert len(calls) == 1


@pytest.mark.parametrize(
    "text,expected",
    [
        ("https://creator-a.fanbox.cc/posts/12345", ("creator-a", "12345")),
        ("https://www.fanbox.cc/@creator-a/posts/12345?utm=1", ("creator-a", "12345")),
        ("creator-a.fanbox.cc/posts/12345/", ("creator-a", "12345")),
        ("https://creator-a.fanbox.cc", ("creator-a", None)),
        ("@Creator-A", ("creator-a", None)),
        ("https://creator-a.fanbox.cc/posts/abc", ("creator-a", None)),
        ("https://www.fanbox.cc/", (None, None)),
        ("", (None, None)),
        ("bad id!", (None, None)),
    ],
)
def test_parse_post_ref(text, expected):
    from fanbox_core import parse_post_ref

    assert parse_post_ref(text) == expected


def test_api_page_urls_and_page_fetch_are_restricted():
    page = "https://api.fanbox.cc/post.listCreator?creatorId=x&firstPublishedDatetime=2026-01-01&firstId=1&sort=newest&limit=10"
    calls = []

    def handler(request):
        calls.append(str(request.url))
        if request.url.path == "/post.paginateCreator":
            return httpx.Response(
                200, json={"body": {"pageUrls": [page, "https://evil.example/x", 3]}}
            )
        return httpx.Response(
            200, json={"body": {"posts": [raw_post(7, "2026-01-01T00:00:00+09:00")]}}
        )

    async def go():
        api = make_api(handler)
        try:
            urls = await api.page_urls("x")
            posts = await api.list_posts_page(urls[0])
            with pytest.raises(FanboxError):
                await api.list_posts_page("https://evil.example/post.listCreator?x=1")
            return urls, posts
        finally:
            await api.close()

    urls, posts = run(go())
    assert urls == [page]
    assert len(posts) == 1
    assert len(calls) == 2  # 不允许的地址根本没有发出请求
