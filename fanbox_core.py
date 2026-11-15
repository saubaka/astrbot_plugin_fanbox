"""FANBOX 新帖推送的纯逻辑部分。

包括：解析创作者 ID、整理帖子、判断新帖、生成模板变量、渲染消息模板。
这里只用标准库，可以脱离 AstrBot 单独测试。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

SEEN_LIMIT = 50

_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}")
_AT_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?fanbox\.cc/@([A-Za-z0-9_-]+)", re.IGNORECASE
)
_SUBDOMAIN_URL_RE = re.compile(
    r"(?:https?://)?([A-Za-z0-9_-]+)\.fanbox\.cc(?:[/?#]|$)", re.IGNORECASE
)
# 这些子域名是 FANBOX 自己的服务，不是创作者。
_RESERVED_SUBDOMAINS = {"www", "api", "downloads", "help", "s", "static"}

_TZ_LABELS = {8: "北京时间", 9: "日本时间", 0: "UTC"}


def parse_creator_id(text: str | None) -> str | None:
    """从 ID、@ID 或 FANBOX 链接里取出创作者 ID；认不出来返回 None。"""
    s = (text or "").strip().strip("<>").strip()
    if not s:
        return None

    m = _AT_URL_RE.match(s)
    if m:
        return m.group(1).lower()

    m = _SUBDOMAIN_URL_RE.match(s)
    if m:
        sub = m.group(1).lower()
        return None if sub in _RESERVED_SUBDOMAINS else sub

    s = s.lstrip("@")
    if _ID_RE.fullmatch(s):
        return s.lower()
    return None


def parse_timestamp(value: Any) -> float:
    """把 FANBOX 的 ISO 时间（带 +09:00）转成时间戳，失败返回 0。"""
    if not isinstance(value, str) or not value:
        return 0.0
    try:
        return datetime.fromisoformat(value).timestamp()
    except ValueError:
        return 0.0


def _to_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


@dataclass
class Post:
    id: str
    creator_id: str
    creator_name: str
    title: str
    fee: int
    restricted: bool
    adult: bool
    excerpt: str
    cover_url: str
    tags: list[str] = field(default_factory=list)
    published: str = ""
    ts: float = 0.0
    pinned: bool = False
    updated: str = ""
    like_count: int = 0
    comment_count: int = 0
    creator_icon_url: str = ""

    @property
    def url(self) -> str:
        return f"https://{self.creator_id}.fanbox.cc/posts/{self.id}"

    @property
    def creator_url(self) -> str:
        return f"https://{self.creator_id}.fanbox.cc"


def parse_post(raw: Any) -> Post | None:
    """把帖子列表里的一项转成 Post；缺少关键字段时返回 None。"""
    if not isinstance(raw, dict):
        return None
    post_id = str(raw.get("id") or "").strip()
    creator_id = str(raw.get("creatorId") or "").strip().lower()
    if not post_id.isdigit() or not creator_id:
        return None

    cover = raw.get("cover")
    cover_url = ""
    if isinstance(cover, dict) and isinstance(cover.get("url"), str):
        cover_url = cover["url"]
    elif isinstance(raw.get("coverImageUrl"), str):
        cover_url = raw["coverImageUrl"]

    user = raw.get("user") if isinstance(raw.get("user"), dict) else {}
    tags = [str(t) for t in (raw.get("tags") or []) if isinstance(t, str) and t]
    published = str(raw.get("publishedDatetime") or "")
    return Post(
        id=post_id,
        creator_id=creator_id,
        creator_name=str(user.get("name") or ""),
        title=str(raw.get("title") or ""),
        fee=_to_int(raw.get("feeRequired")),
        restricted=bool(raw.get("isRestricted")),
        adult=bool(raw.get("hasAdultContent")),
        excerpt=str(raw.get("excerpt") or ""),
        cover_url=cover_url,
        tags=tags,
        published=published,
        ts=parse_timestamp(published),
        pinned=bool(raw.get("isPinned")),
        updated=str(raw.get("updatedDatetime") or ""),
        like_count=_to_int(raw.get("likeCount")),
        comment_count=_to_int(raw.get("commentCount")),
        creator_icon_url=str(user.get("iconUrl") or ""),
    )


def parse_posts(raw_posts: Any) -> list[Post]:
    if not isinstance(raw_posts, list):
        return []
    return [p for p in (parse_post(r) for r in raw_posts) if p is not None]


# ---------- 新帖判断 ----------


START_MODES = ("deploy", "subscribe", "custom")
START_MODE_LABELS = {
    "deploy": "插件部署时间",
    "subscribe": "订阅时间",
    "custom": "自定义时间",
}


def initial_state(name: str = "", now: float = 0.0) -> dict[str, Any]:
    """新订阅的状态。从哪篇开始推送由"推送起点"决定（见 start_floor）。"""
    return {"name": name, "last_ts": 0.0, "seen": [], "subscribed_at": float(now)}


def subscribed_at(state: dict[str, Any]) -> float:
    # v0.2.0 及更早的订阅没有 subscribed_at，用当时记下的最新帖时间代替
    return float(state.get("subscribed_at") or state.get("last_ts") or 0.0)


def parse_start_time(text: str | None, offset_hours: int = 8) -> float | None:
    """解析"自定义起点时间"。没写时区的按 offset_hours 理解；解析不了返回 None。

    支持 2026-11-15 08:00、2026-11-15 08:00:00、2026-11-15、2026/11/15 08:00，
    以及带时区的 ISO 格式（例如 2026-11-15T08:00:00+09:00）。
    """
    s = (text or "").strip()
    if not s:
        return None
    tz = timezone(timedelta(hours=offset_hours))
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        dt = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(s.replace("/", "-"), fmt)
                break
            except ValueError:
                continue
        if dt is None:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    return dt.timestamp()


def start_floor(
    mode: str,
    *,
    deployed_at: float,
    subscribed: float,
    custom_ts: float | None,
) -> float:
    """推送起点：早于这个时间发布的帖子一律不推送。"""
    if mode == "subscribe":
        return subscribed
    if mode == "custom" and custom_ts is not None:
        return custom_ts
    return deployed_at


def select_new_posts(
    posts: list[Post],
    state: dict[str, Any],
    floor: float = 0.0,
    now: float = 0.0,
    max_age_hours: int = 0,
) -> list[Post]:
    """找出该推送的帖子，按发布时间从旧到新排列。

    条件（全部满足）：
    - 发布时间不早于推送起点 floor；
    - 发布时间不早于上次推送过的最新一篇（帖子被删后，更早的旧帖会挤进列表，
      这个条件能挡住它们）；
    - ID 没推送过（同一时间发布的多篇只发出去一部分时，剩下的下次还会推送，
      而且不会重复）；
    - 设置了 max_age_hours 时，发布不超过这么多小时。
    """
    min_ts = max(float(state.get("last_ts") or 0.0), float(floor or 0.0))
    if max_age_hours > 0 and now:
        min_ts = max(min_ts, now - max_age_hours * 3600)
    seen = set(state.get("seen") or [])
    fresh = [p for p in posts if p.ts and p.ts >= min_ts and p.id not in seen]
    return sorted(fresh, key=lambda p: (p.ts, p.id))


def advance_state(state: dict[str, Any], sent: list[Post]) -> dict[str, Any]:
    """推送成功后更新状态。只记已经发出去的帖子，没发成功的下次会重试。"""
    if not sent:
        return state
    last_ts = max([float(state.get("last_ts") or 0.0)] + [p.ts for p in sent])
    seen = [p.id for p in sorted(sent, key=lambda p: p.ts, reverse=True)]
    for pid in state.get("seen") or []:
        if pid not in seen:
            seen.append(pid)
    new_state = dict(state)
    new_state["last_ts"] = last_ts
    new_state["seen"] = seen[:SEEN_LIMIT]
    return new_state


# ---------- 文字整理 ----------


def clean_excerpt(text: str, limit: int) -> str:
    """压缩多余空白和空行，超过 limit 个字截断并加"…"；limit<=0 返回空。"""
    if limit <= 0:
        return ""
    text = re.sub(r"[ \t　]+", " ", text or "")
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    if len(text) > limit:
        text = text[:limit].rstrip() + "…"
    return text


def tz_label(offset_hours: int) -> str:
    return _TZ_LABELS.get(offset_hours) or f"UTC{offset_hours:+d}"


def _local_dt(iso: str, offset_hours: int) -> datetime | None:
    ts = parse_timestamp(iso)
    if not ts:
        return None
    return datetime.fromtimestamp(ts, timezone(timedelta(hours=offset_hours)))


def format_time(
    published: str,
    offset_hours: int = 8,
    show_timezone: bool = True,
    fmt: str = "%Y-%m-%d %H:%M",
) -> str:
    dt = _local_dt(published, offset_hours)
    if dt is None:
        return ""
    try:
        text = dt.strftime(fmt or "%Y-%m-%d %H:%M")
    except ValueError:
        text = dt.strftime("%Y-%m-%d %H:%M")
    return text + (f"（{tz_label(offset_hours)}）" if show_timezone else "")


def format_ts(ts: float, offset_hours: int = 8) -> str:
    """把时间戳写成"2026-11-15 08:00（北京时间）"，用在指令回复里。"""
    if not ts:
        return "（未知）"
    dt = datetime.fromtimestamp(ts, timezone(timedelta(hours=offset_hours)))
    return dt.strftime("%Y-%m-%d %H:%M") + f"（{tz_label(offset_hours)}）"


def format_card_time(
    published: str, offset_hours: int = 8, show_timezone: bool = True
) -> str:
    """卡片上的日期，和 FANBOX 网页一样写成"2026年11月14日 01:12"。"""
    dt = _local_dt(published, offset_hours)
    if dt is None:
        return ""
    text = f"{dt.year}年{dt.month}月{dt.day}日 {dt:%H:%M}"
    return text + (f"（{tz_label(offset_hours)}）" if show_timezone else "")


# ---------- 模板 ----------


@dataclass
class StyleOptions:
    excerpt_max: int = 120
    offset_hours: int = 8
    show_fee: bool = True
    show_timezone: bool = True
    show_tags: bool = True
    show_adult_mark: bool = True
    time_format: str = "%Y-%m-%d %H:%M"
    max_tags: int = 6


DEFAULT_TEMPLATE = """【FANBOX】{creator_name} {headline}
《{title}》
{labels}
{excerpt}
{tags}
?发布时间：{published}
{post_url}
{cover_image}"""

# 模板里能用的全部变量。顺序就是文档里的顺序。
TEXT_VARIABLES: dict[str, str] = {
    "headline": "推送时是“发布了新帖”，/fanbox最新 时是“的最新帖子”",
    "creator_name": "创作者昵称",
    "creator_id": "创作者 ID，也就是主页 https://<ID>.fanbox.cc 里的 <ID>",
    "creator_url": "创作者主页链接",
    "creator_icon_url": "创作者头像图片链接",
    "title": "帖子标题（没有标题时是“（无标题）”）",
    "post_id": "帖子 ID",
    "post_url": "帖子链接",
    "excerpt": "摘要，按“摘要最多显示多少字”截断；付费帖未登录时通常为空",
    "excerpt_full": "完整摘要（只整理空行，不截断）",
    "fee": "档位金额数字，免费帖是 0（不受“显示付费档位”影响）",
    "fee_text": "“付费 · 500 日元及以上档位”或“免费公开”；关闭“显示付费档位”时为空",
    "fee_badge": "“500日元”或“免费”；关闭“显示付费档位”时为空",
    "paid": "“付费”或“免费”（不受“显示付费档位”影响）",
    "adult": "R-18 帖子是“R-18”，否则为空；关闭“显示 R-18 标记”时为空",
    "labels": "档位和 R-18 用“ · ”连起来，例如“付费 · 500 日元及以上档位 · R-18”",
    "restricted": "未登录看不了正文时是“需赞助”，否则为空",
    "tags": "标签，写成“#标签1 #标签2”；关闭“显示标签”时为空",
    "tags_plain": "标签，用顿号连接“标签1、标签2”；关闭“显示标签”时为空",
    "tag_count": "标签个数",
    "published": "发布时间，按“时间格式”和时区；开启“显示时区”时后面带“（北京时间）”",
    "published_date": "发布日期，例如 2026-11-13",
    "published_time": "发布时刻，例如 20:12",
    "published_iso": "FANBOX 原始发布时间（日本时间 ISO 格式）",
    "updated": "最后更新时间，格式同 published",
    "timezone": "时区名称，例如“北京时间”（不受“显示时区”影响）",
    "like_count": "点赞数",
    "comment_count": "评论数",
    "cover_url": "封面图链接（R-18 帖子在不允许发封面时为空）",
    "pinned": "置顶帖是“置顶”，否则为空",
}

IMAGE_VARIABLES: dict[str, str] = {
    "cover_image": "封面图（关闭“附带封面图”，或 R-18 帖子不允许发封面时不发）",
    "card_image": "仿 FANBOX 网页样式的卡片图",
    "avatar_image": "创作者头像",
}

_TOKEN_RE = re.compile(r"\{\{|\}\}|\{([A-Za-z_][A-Za-z0-9_]*)\}")


def build_variables(
    post: Post,
    creator_name: str = "",
    opts: StyleOptions | None = None,
    headline: str = "发布了新帖",
    cover_allowed: bool = True,
) -> dict[str, str]:
    """生成模板里 {变量} 的取值。全部是字符串。"""
    o = opts or StyleOptions()
    name = creator_name or post.creator_name or post.creator_id
    paid = post.fee > 0
    fee_text = (
        (f"付费 · {post.fee} 日元及以上档位" if paid else "免费公开")
        if o.show_fee
        else ""
    )
    fee_badge = (f"{post.fee}日元" if paid else "免费") if o.show_fee else ""
    adult = "R-18" if (post.adult and o.show_adult_mark) else ""
    tags = post.tags[: max(0, o.max_tags)] if o.show_tags else []
    dt = _local_dt(post.published, o.offset_hours)
    return {
        "headline": headline,
        "creator_name": name,
        "creator_id": post.creator_id,
        "creator_url": post.creator_url,
        "creator_icon_url": post.creator_icon_url,
        "title": post.title or "（无标题）",
        "post_id": post.id,
        "post_url": post.url,
        "excerpt": clean_excerpt(post.excerpt, o.excerpt_max),
        "excerpt_full": clean_excerpt(post.excerpt, 1_000_000),
        "fee": str(post.fee),
        "fee_text": fee_text,
        "fee_badge": fee_badge,
        "paid": "付费" if paid else "免费",
        "adult": adult,
        "labels": " · ".join(x for x in (fee_text, adult) if x),
        "restricted": "需赞助" if post.restricted else "",
        "tags": " ".join(f"#{t}" for t in tags),
        "tags_plain": "、".join(tags),
        "tag_count": str(len(tags)),
        "published": format_time(
            post.published, o.offset_hours, o.show_timezone, o.time_format
        ),
        "published_date": dt.strftime("%Y-%m-%d") if dt else "",
        "published_time": dt.strftime("%H:%M") if dt else "",
        "published_iso": post.published,
        "updated": format_time(
            post.updated, o.offset_hours, o.show_timezone, o.time_format
        ),
        "timezone": tz_label(o.offset_hours),
        "like_count": str(post.like_count),
        "comment_count": str(post.comment_count),
        "cover_url": post.cover_url if cover_allowed else "",
        "pinned": "置顶" if post.pinned else "",
    }


def unknown_variables(template: str) -> list[str]:
    """模板里写错的变量名（既不是文字变量也不是图片变量）。"""
    names = []
    for m in _TOKEN_RE.finditer(template or ""):
        name = m.group(1)
        if name and name not in TEXT_VARIABLES and name not in IMAGE_VARIABLES:
            if name not in names:
                names.append(name)
    return names


def render_template(template: str, values: dict[str, str]) -> list[tuple[str, str]]:
    """把模板渲染成片段列表：("text", 文字) 或 ("image", 图片变量名)。

    规则：
    - {变量} 换成取值；{{ 和 }} 表示字面的花括号；不认识的 {xxx} 原样保留。
    - 一行里用了变量、替换后却没有任何文字，这一行整行删掉（但行里的图片保留）。
    - 以 ? 开头的行是条件行：行里任何一个文字变量为空，就整行删掉；? 本身不显示。
    """
    pieces: list[tuple[str, str]] = []
    for raw_line in (template or "").split("\n"):
        conditional = raw_line.startswith("?")
        line = raw_line[1:] if conditional else raw_line
        parts: list[tuple[str, str]] = []
        used_var = False
        any_empty = False
        pos = 0
        for m in _TOKEN_RE.finditer(line):
            parts.append(("text", line[pos : m.start()]))
            pos = m.end()
            tok = m.group(0)
            if tok == "{{":
                parts.append(("text", "{"))
                continue
            if tok == "}}":
                parts.append(("text", "}"))
                continue
            name = m.group(1)
            if name in IMAGE_VARIABLES:
                parts.append(("image", name))
                used_var = True
            elif name in values:
                val = values[name]
                parts.append(("text", val))
                used_var = True
                any_empty = any_empty or not val.strip()
            else:
                parts.append(("text", tok))
        parts.append(("text", line[pos:]))

        visible = "".join(s for k, s in parts if k == "text")
        images = [p for p in parts if p[0] == "image"]
        if conditional and any_empty:
            continue
        if used_var and not visible.strip():
            pieces.extend(images)
            continue
        pieces.extend(parts)
        pieces.append(("text", "\n"))

    # 合并相邻文字，去掉图片两边和首尾多余的换行
    merged: list[tuple[str, str]] = []
    for kind, val in pieces:
        if kind == "text" and merged and merged[-1][0] == "text":
            merged[-1] = ("text", merged[-1][1] + val)
        else:
            merged.append((kind, val))
    out: list[tuple[str, str]] = []
    for kind, val in merged:
        if kind == "text":
            val = val.strip("\n")
            if not val.strip():
                continue
        out.append((kind, val))
    return out


def format_post_text(
    post: Post,
    creator_name: str = "",
    excerpt_max: int = 120,
    offset_hours: int = 8,
    headline: str = "发布了新帖",
) -> str:
    """用默认模板生成纯文字（不含图片），给测试和简单场景用。"""
    opts = StyleOptions(excerpt_max=excerpt_max, offset_hours=offset_hours)
    values = build_variables(post, creator_name, opts, headline)
    return "\n".join(
        v for k, v in render_template(DEFAULT_TEMPLATE, values) if k == "text"
    )
