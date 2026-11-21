"""
AstrBot FANBOX 新帖推送插件

订阅 pixivFANBOX 创作者，有新帖时推送到订阅的会话。
只读取 FANBOX 公开的帖子列表，不登录，也不转发付费内容。
"""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, MessageChain, filter
from astrbot.api.message_components import Image, Plain
from astrbot.api.star import Context, Star

from .fanbox_api import FanboxAPI, FanboxBlocked, FanboxError, FanboxNotFound
from .fanbox_card import CardOptions, render_card
from .fanbox_core import (
    IMAGE_VARIABLES,
    START_MODE_LABELS,
    TEXT_VARIABLES,
    Post,
    advance_state,
    build_variables,
    card_messages,
    ensure_card_element,
    format_ts,
    initial_state,
    parse_creator_id,
    parse_posts,
    render_template,
    select_new_posts,
    start_floor,
    subscribed_at,
    with_creator_cover,
)
from .fanbox_settings import (
    Settings,
    build_settings,
    current_values,
    load_schema,
    validate,
)
from .fanbox_stats import Stats

try:
    from .fanbox_webui import FanboxWebUI
except ModuleNotFoundError as exc:  # 旧版 AstrBot 没有 astrbot.api.web
    if exc.name != "astrbot.api.web":
        raise
    FanboxWebUI = None

PLUGIN_NAME = "astrbot_plugin_fanbox"
KV_SUBSCRIPTIONS = "fanbox_subscriptions_v1"
KV_DEPLOYED_AT = "fanbox_deployed_at"
KV_STATS = "fanbox_stats_v1"
LIST_LIMIT = 10

Piece = tuple[str, Any]  # ("text", str) 或 ("image", bytes)


def _style_tag(s: Settings) -> str:
    """推送记录里的样式标记：text / card / card_merge / card_separate。"""
    if s.push_style != "card" or s.card_text == "none":
        return s.push_style
    return "card_" + s.card_text


def _post_brief(post: Post) -> dict[str, Any]:
    return {
        "id": post.id,
        "title": post.title,
        "published": post.published,
        "fee": post.fee,
        "adult": post.adult,
        "url": post.url,
        "cover_url": post.cover_url,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
    }


def _card_info(post: Post) -> dict[str, Any]:
    """推送记录里画 FANBOX 卡片用的信息。"""
    return {
        "cover_url": post.cover_url,
        "icon_url": post.creator_icon_url,
        "fee": post.fee,
        "adult": post.adult,
        "excerpt": post.excerpt,
        "like_count": post.like_count,
        "comment_count": post.comment_count,
        "published": post.published,
        "tags": post.tags,
    }


IMAGE_CACHE_TTL = 30 * 60
IMAGE_CACHE_MAX = 60
POST_CACHE_TTL = 5 * 60
CREATOR_COVER_TTL = 6 * 3600  # 创作者主页封面很少换，缓存 6 小时
CREATOR_COVER_FAIL_TTL = 10 * 60
MAX_PAGES_TO_SEARCH = 30


class FanboxPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.schema = load_schema()
        self.s, warnings = build_settings(current_values(config, self.schema))
        self.settings_warnings = warnings
        for w in warnings:
            logger.warning(f"[FANBOX] {w}")
        self.api = FanboxAPI(proxy=self.s.proxy)
        self.stats = Stats()

        # 真正的部署时间在 initialize() 里从 KV 读取（第一次启动时写入）
        self.deployed_at = time.time()
        self.last_poll_at = 0.0
        self.next_poll_at = 0.0
        self.last_poll_sent = 0
        # 图片和帖子的短期缓存：实时预览频繁重画时不用每次都去 FANBOX 下载
        self._image_cache: dict[str, tuple[float, bytes]] = {}
        self._creator_cover_cache: dict[str, tuple[float, str]] = {}
        self._post_cache: dict[tuple[str, str], tuple[float, Post]] = {}

        self._lock = asyncio.Lock()
        self._config_lock = asyncio.Lock()
        self._reschedule = asyncio.Event()
        self._running = False
        self._task: asyncio.Task | None = None

        self._webui = None
        if FanboxWebUI is not None and callable(
            getattr(context, "register_web_api", None)
        ):
            try:
                self._webui = FanboxWebUI(self, context)
            except Exception as exc:
                logger.warning(f"[FANBOX] 插件页接口注册失败: {exc}")

    # ---------- 生命周期 ----------

    async def initialize(self):
        await self._migrate_card_template()
        stored = await self.get_kv_data(KV_DEPLOYED_AT, None)
        try:
            stored = float(stored) if stored else 0.0
        except (TypeError, ValueError):
            stored = 0.0
        if stored > 0:
            self.deployed_at = stored
        else:
            await self.put_kv_data(KV_DEPLOYED_AT, self.deployed_at)
            logger.info(
                "[FANBOX] 首次启动，记下部署时间 "
                f"{format_ts(self.deployed_at, self.s.style.offset_hours)}"
            )
        try:
            self.stats = Stats(await self.get_kv_data(KV_STATS, {}))
        except Exception as exc:
            logger.warning(f"[FANBOX] 读取统计数据失败，从零开始: {exc}")
            self.stats = Stats()

        self._running = True
        # 第一次检查放在 30~90 秒后：等平台适配器连上，也和其他插件错开
        self.last_poll_at = (
            time.time() - self.s.poll_interval * 60 + random.uniform(30, 90)
        )
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(
            f"[FANBOX] 插件已启动，轮询间隔 {self.s.poll_interval} 分钟，"
            f"推送样式 {self.s.push_style}，推送起点 {self.describe_floor()}"
        )

    async def terminate(self):
        self._running = False
        self._reschedule.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self._save_stats()
        await self.api.close()
        logger.info("[FANBOX] 插件已停止")

    # ---------- 设置 ----------

    async def _migrate_card_template(self) -> None:
        """v0.6.0 的卡片图配文模板里没有 {card_image}：补在末尾（卡片图仍在文字下方）并写回配置。"""
        section = self.config.get("style") if hasattr(self.config, "get") else None
        if not isinstance(section, dict):
            return
        raw = section.get("card_template")
        if not isinstance(raw, str) or not raw:
            return
        fixed = ensure_card_element(raw)
        if fixed == raw:
            return
        section["card_template"] = fixed
        try:
            result = self.config.save_config()
            if asyncio.iscoroutine(result):
                await result
            logger.info("[FANBOX] 卡片图配文模板里补上了 {card_image}（卡片图元素）")
        except Exception as exc:
            logger.warning(f"[FANBOX] 写回卡片图配文模板失败（不影响推送）: {exc}")

    def setting_values(self) -> dict[str, dict[str, Any]]:
        return current_values(self.config, self.schema)

    async def save_settings(self, patch: Any) -> tuple[bool, list[str], list[str]]:
        """校验并保存设置，立即生效。返回 (是否保存, 错误, 提示)。"""
        async with self._config_lock:
            merged, errors = validate(patch, self.schema, self.setting_values())
            if errors:
                return False, errors, []
            previous = {g: dict(v) for g, v in self.setting_values().items()}
            for group, values in merged.items():
                section = self.config.get(group)
                if not isinstance(section, dict):
                    section = {}
                    self.config[group] = section
                section.update(values)
            try:
                result = self.config.save_config()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as exc:
                for group, values in previous.items():
                    self.config[group] = values
                logger.error(f"[FANBOX] 保存设置失败: {exc}")
                return False, ["保存失败，原设置已恢复"], []

            old = self.s
            self.s, warnings = build_settings(merged)
            self.settings_warnings = warnings
            if self.s.proxy != old.proxy:
                old_api, self.api = self.api, FanboxAPI(proxy=self.s.proxy)
                await old_api.close()
            if self.s.poll_interval != old.poll_interval:
                self._reschedule.set()
            logger.info("[FANBOX] 设置已从插件页保存并生效")
            return True, [], warnings

    def preview_settings(self, patch: Any) -> tuple[Settings | None, list[str]]:
        """用页面上还没保存的设置生成一份临时 Settings，只给预览用。"""
        merged, errors = validate(patch or {}, self.schema, self.setting_values())
        if errors:
            return None, errors
        s, _ = build_settings(merged)
        return s, []

    # ---------- 推送起点 ----------

    def floor(self, state: dict[str, Any], s: Settings | None = None) -> float:
        s = s or self.s
        return start_floor(
            s.start_from,
            deployed_at=self.deployed_at,
            subscribed=subscribed_at(state),
            custom_ts=s.custom_start_ts,
        )

    def describe_floor(self, state: dict[str, Any] | None = None) -> str:
        mode = self.s.start_from
        if mode == "custom" and self.s.custom_start_ts is None:
            mode = "deploy"
        label = START_MODE_LABELS[mode]
        if mode == "subscribe" and state is None:
            return label
        return (
            f"{label} {format_ts(self.floor(state or {}), self.s.style.offset_hours)}"
        )

    # ---------- 订阅存储 ----------

    async def load_subscriptions(self) -> dict[str, dict[str, dict[str, Any]]]:
        data = await self.get_kv_data(KV_SUBSCRIPTIONS, {})
        return data if isinstance(data, dict) else {}

    async def _save_subscriptions(
        self, data: dict[str, dict[str, dict[str, Any]]]
    ) -> None:
        await self.put_kv_data(KV_SUBSCRIPTIONS, data)

    async def _save_stats(self) -> None:
        try:
            self.stats.prune()
            await self.put_kv_data(KV_STATS, self.stats.to_dict())
        except Exception as exc:
            logger.warning(f"[FANBOX] 保存统计数据失败: {exc}")

    async def add_subscription(self, umo: str, cid: str) -> dict[str, Any]:
        """订阅（指令和插件页共用）。"""
        try:
            creator = await self.api.get_creator(cid)
            posts = parse_posts(await self.api.list_posts(cid, LIST_LIMIT))
        except FanboxNotFound:
            return {"ok": False, "reason": "not_found", "creator": cid}
        except FanboxError as exc:
            logger.warning(f"[FANBOX] 订阅 {cid} 时请求失败: {exc}")
            return {"ok": False, "reason": "unavailable", "creator": cid}

        user = creator.get("user") if isinstance(creator.get("user"), dict) else {}
        name = str(user.get("name") or cid)
        now = time.time()
        state = initial_state(name, now)
        async with self._lock:
            subs = await self.load_subscriptions()
            per_umo = subs.setdefault(umo, {})
            if cid in per_umo:
                return {"ok": False, "reason": "exists", "creator": cid, "name": name}
            per_umo[cid] = state
            await self._save_subscriptions(subs)
        c = self.stats._creator(cid)
        c["name"] = name
        if user.get("iconUrl"):
            c["icon_url"] = str(user["iconUrl"])
        if posts:
            c["latest"] = _post_brief(max(posts, key=lambda p: p.ts))
            c["post_count"] = len(posts)
        await self._save_stats()

        pending = select_new_posts(
            posts, state, self.floor(state), now, self.s.max_post_age_hours
        )
        return {
            "ok": True,
            "creator": cid,
            "name": name,
            "floor": self.describe_floor(state),
            "pending": len(pending),
            "will_push": min(len(pending), self.s.max_new_per_poll),
        }

    async def remove_subscription(self, umo: str, cid: str) -> dict[str, Any] | None:
        async with self._lock:
            subs = await self.load_subscriptions()
            per_umo = subs.get(umo) or {}
            state = per_umo.pop(cid, None)
            if state is None:
                return None
            if not per_umo:
                subs.pop(umo, None)
            await self._save_subscriptions(subs)
            still_used = any(cid in m for m in subs.values())
        if not still_used:
            self.stats.forget_creator(cid)
            await self._save_stats()
        return state

    # ---------- 轮询 ----------

    async def _sleep_until_next_poll(self) -> None:
        """等到下一次检查；插件页改了轮询间隔会立刻按新间隔重新计时。"""
        while self._running:
            self._reschedule.clear()
            remaining = self.last_poll_at + self.s.poll_interval * 60 - time.time()
            self.next_poll_at = time.time() + max(0.0, remaining)
            if remaining <= 0:
                return
            try:
                await asyncio.wait_for(self._reschedule.wait(), timeout=remaining)
            except asyncio.TimeoutError:
                return

    async def _poll_loop(self):
        while self._running:
            await self._sleep_until_next_poll()
            if not self._running:
                return
            try:
                await self.poll_once()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error(f"[FANBOX] 轮询出错: {exc}")
                self.last_poll_at = time.time()

    async def poll_once(self) -> int:
        """检查全部订阅，返回这次推送出去的帖子数。"""
        total_sent = 0
        s = self.s
        async with self._lock:
            subs = await self.load_subscriptions()
            creators = sorted({cid for per_umo in subs.values() for cid in per_umo})
            for cid in creators:
                t0 = time.monotonic()
                try:
                    posts = parse_posts(await self.api.list_posts(cid, LIST_LIMIT))
                except FanboxBlocked as exc:
                    ms = int((time.monotonic() - t0) * 1000)
                    logger.warning(f"[FANBOX] {cid}: {exc}，本轮跳过")
                    self.stats.record_check(cid, "blocked", ms, message=str(exc))
                    self.stats.record_error("blocked", str(exc), creator=cid)
                    continue
                except FanboxNotFound as exc:
                    ms = int((time.monotonic() - t0) * 1000)
                    logger.warning(f"[FANBOX] {cid}: 创作者不存在或已删除（{exc}）")
                    self.stats.record_check(cid, "not_found", ms, message=str(exc))
                    self.stats.record_error("not_found", str(exc), creator=cid)
                    continue
                except FanboxError as exc:
                    ms = int((time.monotonic() - t0) * 1000)
                    logger.warning(f"[FANBOX] 获取 {cid} 的帖子列表失败: {exc}")
                    self.stats.record_check(cid, "error", ms, message=str(exc))
                    self.stats.record_error("list_failed", str(exc), creator=cid)
                    continue
                ms = int((time.monotonic() - t0) * 1000)
                latest = max(posts, key=lambda p: p.ts) if posts else None
                self.stats.record_check(
                    cid,
                    "ok",
                    ms,
                    name=latest.creator_name if latest else "",
                    icon_url=latest.creator_icon_url if latest else "",
                    latest=_post_brief(latest) if latest else None,
                    post_count=len(posts),
                )

                changed = False
                for umo, per_umo in subs.items():
                    state = per_umo.get(cid)
                    if state is None:
                        continue
                    fresh = select_new_posts(
                        posts,
                        state,
                        self.floor(state, s),
                        time.time(),
                        s.max_post_age_hours,
                    )
                    if len(fresh) > s.max_new_per_poll:
                        logger.info(
                            f"[FANBOX] {cid} 有 {len(fresh)} 篇新帖，"
                            f"只推送最新的 {s.max_new_per_poll} 篇"
                        )
                        fresh = fresh[-s.max_new_per_poll :]
                    sent: list[Post] = []
                    for post in fresh:
                        if not await self._send_post(
                            umo, post, state.get("name", ""), s
                        ):
                            break
                        sent.append(post)
                    if sent:
                        per_umo[cid] = advance_state(state, sent)
                        total_sent += len(sent)
                        changed = True
                if changed:
                    await self._save_subscriptions(subs)
                await asyncio.sleep(random.uniform(1.0, 3.0))
        self.last_poll_at = time.time()
        self.last_poll_sent = total_sent
        await self._save_stats()
        return total_sent

    async def check_now(self) -> int:
        """立即检查一次（指令和插件页共用），之后按间隔重新计时。"""
        sent = await self.poll_once()
        self._reschedule.set()
        return sent

    # ---------- 生成消息 ----------

    async def _creator_cover(self, cid: str) -> str:
        """创作者主页的封面图地址（带缓存）。拿不到时返回空字符串。"""
        hit = self._creator_cover_cache.get(cid)
        if hit:
            ttl = CREATOR_COVER_TTL if hit[1] else CREATOR_COVER_FAIL_TTL
            if time.time() - hit[0] < ttl:
                return hit[1]
        url = ""
        try:
            body = await self.api.get_creator(cid)
            raw = body.get("coverImageUrl")
            url = raw if isinstance(raw, str) else ""
        except FanboxError as exc:
            logger.warning(f"[FANBOX] 读取 {cid} 的主页封面失败: {exc}")
        self._creator_cover_cache[cid] = (time.time(), url)
        return url

    async def _with_cover(self, post: Post, s: Settings) -> Post:
        """帖子没有封面时按设置改用创作者主页封面。"""
        if post.cover_url or not s.creator_cover_fallback:
            return post
        fixed = with_creator_cover(post, await self._creator_cover(post.creator_id))
        if fixed.cover_from_creator:
            logger.info(f"[FANBOX] 帖子 {post.id} 没有封面，改用创作者主页封面")
        return fixed

    def _cover_allowed(self, post: Post, s: Settings) -> bool:
        return bool(post.cover_url) and (s.send_adult_cover or not post.adult)

    async def _download(
        self, url: str, cache: dict[str, bytes | None], creator: str = ""
    ) -> bytes | None:
        if not url:
            return None
        if url not in cache:
            hit = self._image_cache.get(url)
            if hit and time.time() - hit[0] < IMAGE_CACHE_TTL:
                cache[url] = hit[1]
                return hit[1]
            try:
                data = await self.api.download_image(url)
                cache[url] = data
                self._image_cache[url] = (time.time(), data)
                if len(self._image_cache) > IMAGE_CACHE_MAX:
                    oldest = min(
                        self._image_cache, key=lambda k: self._image_cache[k][0]
                    )
                    self._image_cache.pop(oldest, None)
            except FanboxError as exc:
                logger.warning(f"[FANBOX] 图片下载失败: {exc}")
                self.stats.record_error("image_failed", str(exc), creator=creator)
                cache[url] = None
        return cache[url]

    async def _render_card(
        self, post: Post, name: str, cache: dict[str, bytes | None], s: Settings
    ) -> bytes:
        hide_cover = post.adult and not s.send_adult_cover
        cover = (
            None
            if hide_cover
            else await self._download(post.cover_url, cache, post.creator_id)
        )
        avatar = await self._download(post.creator_icon_url, cache, post.creator_id)
        opts = CardOptions(
            show_fee=s.style.show_fee,
            show_timezone=s.style.show_timezone,
            show_adult_mark=s.style.show_adult_mark,
            show_likes=s.card_show_likes,
            excerpt_lines=s.card_excerpt_lines,
            title_lines=s.card_title_lines,
            offset_hours=s.style.offset_hours,
            hide_cover=hide_cover,
            font_path=s.card_font_path,
            bold_font_path=s.card_bold_font_path,
        )
        t0 = time.monotonic()
        try:
            # Pillow 画图是 CPU 活，放到线程里，别卡住机器人
            data = await asyncio.to_thread(render_card, post, name, cover, avatar, opts)
        except Exception as exc:
            self.stats.record_card(False, 0)
            self.stats.record_error(
                "card_failed", str(exc), creator=post.creator_id, post_id=post.id
            )
            raise
        self.stats.record_card(True, int((time.monotonic() - t0) * 1000))
        return data

    async def build_messages(
        self,
        post: Post,
        name: str,
        headline: str = "发布了新帖",
        s: Settings | None = None,
    ) -> list[list[Piece]]:
        """按推送样式生成要发的消息：每条消息是一组片段 ("text", 文字) 或 ("image", 图片字节)。

        同一条消息里的文字和图片由 QQ 原生合成一条发送（不是合并转发）。
        """
        s = s or self.s
        cache: dict[str, bytes | None] = {}
        name = name or post.creator_name or post.creator_id
        post = await self._with_cover(post, s)
        if s.push_style == "card":
            try:
                card = await self._render_card(post, name, cache, s)
            except Exception as exc:
                logger.warning(
                    f"[FANBOX] 帖子 {post.id} 卡片图渲染失败，改发文字模板: {exc}"
                )
            else:
                pieces: list[tuple[str, str]] = []
                if s.card_text != "none":
                    values = build_variables(
                        post, name, s.style, headline, self._cover_allowed(post, s)
                    )
                    pieces = render_template(s.card_template, values)
                return card_messages(pieces, card, s.card_text)
        return [await self._template_pieces(post, name, headline, s, cache)]

    async def build_pieces(
        self,
        post: Post,
        name: str,
        headline: str = "发布了新帖",
        s: Settings | None = None,
    ) -> list[Piece]:
        """全部消息的片段按顺序摊平（兼容旧调用）。"""
        messages = await self.build_messages(post, name, headline, s)
        return [piece for message in messages for piece in message]

    async def _template_pieces(
        self,
        post: Post,
        name: str,
        headline: str,
        s: Settings,
        cache: dict[str, bytes | None],
    ) -> list[Piece]:
        """按“推送模板”生成一条消息的片段。"""
        values = build_variables(
            post, name, s.style, headline, self._cover_allowed(post, s)
        )
        pieces: list[Piece] = []
        for kind, value in render_template(s.template, values):
            if kind == "text":
                pieces.append(("text", value))
                continue
            data: bytes | None = None
            if value == "cover_image":
                if s.send_cover and self._cover_allowed(post, s):
                    data = await self._download(post.cover_url, cache, post.creator_id)
            elif value == "avatar_image":
                data = await self._download(
                    post.creator_icon_url, cache, post.creator_id
                )
            elif value == "card_image":
                try:
                    data = await self._render_card(post, name, cache, s)
                except Exception as exc:
                    logger.warning(f"[FANBOX] 帖子 {post.id} 卡片图渲染失败: {exc}")
            if data:
                pieces.append(("image", data))
        return pieces or [("text", post.url)]

    @staticmethod
    def _to_chain(pieces: list[Piece]) -> list:
        return [
            Plain(value) if kind == "text" else Image.fromBytes(value)
            for kind, value in pieces
        ]

    async def _send_messages(self, umo: str, messages: list[list[Piece]]) -> str:
        """按顺序把每条消息发到会话。返回错误说明，全部成功返回空字符串。"""
        for pieces in messages:
            try:
                ok = await self.context.send_message(
                    umo, MessageChain(chain=self._to_chain(pieces))
                )
                if ok is False:
                    return "找不到会话"
            except Exception as exc:
                return str(exc) or exc.__class__.__name__
        return ""

    async def send_test(self, umo: str, post: Post, s: Settings) -> str:
        """插件页"测试推送"：按给定样式把一篇帖子发到指定会话。返回错误说明，成功返回空字符串。

        只记进推送记录（标成测试），不改订阅进度，也不计入推送统计。
        """
        name = post.creator_name or post.creator_id
        post = await self._with_cover(post, s)
        error = await self._send_messages(
            umo, await self.build_messages(post, name, s=s)
        )
        self.stats.record_push(
            post.creator_id,
            name=name,
            post_id=post.id,
            title=post.title,
            post_url=post.url,
            umo=umo,
            style=_style_tag(s),
            ok=not error,
            error=error,
            card=_card_info(post),
            test=True,
        )
        await self._save_stats()
        if error:
            logger.warning(f"[FANBOX] 测试推送 {post.id} 到 {umo} 失败: {error}")
        else:
            logger.info(f"[FANBOX] 测试推送 {post.creator_id}/{post.id} 到 {umo}")
        return error

    async def _send_post(self, umo: str, post: Post, name: str, s: Settings) -> bool:
        name = name or post.creator_name or post.creator_id
        post = await self._with_cover(post, s)
        error = await self._send_messages(
            umo, await self.build_messages(post, name, s=s)
        )
        info = dict(
            name=name,
            post_id=post.id,
            title=post.title,
            post_url=post.url,
            umo=umo,
            style=_style_tag(s),
            card=_card_info(post),
        )
        if error:
            logger.warning(f"[FANBOX] 推送帖子 {post.id} 到 {umo} 失败: {error}")
            self.stats.record_push(post.creator_id, ok=False, error=error, **info)
            self.stats.record_error(
                "send_failed", error, creator=post.creator_id, umo=umo, post_id=post.id
            )
            return False
        logger.info(f"[FANBOX] 已推送 {post.creator_id}/{post.id} 到 {umo}")
        self.stats.record_push(post.creator_id, ok=True, **info)
        return True

    async def latest_post(self, cid: str) -> Post | None:
        posts = parse_posts(await self.api.list_posts(cid, LIST_LIMIT))
        return max(posts, key=lambda p: p.ts) if posts else None

    def _cached_post(self, key: tuple[str, str]) -> Post | None:
        hit = self._post_cache.get(key)
        if hit and time.time() - hit[0] < POST_CACHE_TTL:
            return hit[1]
        return None

    def _remember_post(self, key: tuple[str, str], post: Post) -> None:
        self._post_cache[key] = (time.time(), post)
        if len(self._post_cache) > 100:
            oldest = min(self._post_cache, key=lambda k: self._post_cache[k][0])
            self._post_cache.pop(oldest, None)

    async def find_post(self, cid: str, post_id: str | None) -> Post | None:
        """按帖子 ID 找帖子；没给 ID 就取最新一篇。

        服务器上 post.info 会被 FANBOX 拦，所以从公开的帖子列表里找：
        先看最新 10 篇，找不到再按 post.paginateCreator 给的分页地址往前翻（最多 30 页）。
        结果缓存 5 分钟，实时预览反复重画时不用重复请求。
        """
        key = (cid, post_id or "")
        cached = self._cached_post(key)
        if cached is not None:
            return cached
        posts = parse_posts(await self.api.list_posts(cid, LIST_LIMIT))
        found: Post | None = None
        if post_id is None:
            found = max(posts, key=lambda p: p.ts) if posts else None
        else:
            found = next((p for p in posts if p.id == post_id), None)
            if found is None:
                urls = await self.api.page_urls(cid)
                for url in urls[1 : MAX_PAGES_TO_SEARCH + 1]:
                    page = parse_posts(await self.api.list_posts_page(url))
                    found = next((p for p in page if p.id == post_id), None)
                    if found is not None or not page:
                        break
                    # 这一页最旧的帖子 ID 已经比要找的小，就不用再往后翻了
                    if post_id.isdigit() and all(
                        int(p.id) < int(post_id) for p in page
                    ):
                        break
        if found is not None:
            self._remember_post(key, found)
        return found

    # ---------- 指令 ----------

    @filter.command("fanbox关注", alias={"fanbox_follow"})
    async def follow(self, event: AstrMessageEvent, target: str = ""):
        """订阅 FANBOX 创作者：/fanbox关注 <创作者ID或主页链接>"""
        cid = parse_creator_id(target)
        if not cid:
            yield event.plain_result(
                "用法：/fanbox关注 <创作者ID或主页链接>\n"
                "例如：/fanbox关注 official 或 /fanbox关注 https://official.fanbox.cc"
            )
            return
        result = await self.add_subscription(event.unified_msg_origin, cid)
        reason = result.get("reason")
        if reason == "not_found":
            yield event.plain_result(f"没找到 FANBOX 创作者：{cid}")
            return
        if reason == "unavailable":
            yield event.plain_result(
                f"订阅 {cid} 失败：FANBOX 暂时访问不了，请稍后再试"
            )
            return
        if reason == "exists":
            yield event.plain_result(f"这里已经订阅了 {result['name']}（{cid}）")
            return
        lines = [f"已订阅 FANBOX：{result['name']}（{cid}）"]
        lines.append(f"推送起点：{result['floor']}，更早发布的帖子不会推送。")
        if result["pending"]:
            lines.append(
                f"起点之后已经发布了 {result['pending']} 篇，"
                f"下次检查时会推送其中 {result['will_push']} 篇。"
            )
        lines.append("之后有新帖会推送到这里。")
        yield event.plain_result("\n".join(lines))

    @filter.command("fanbox取关", alias={"fanbox_unfollow"})
    async def unfollow(self, event: AstrMessageEvent, target: str = ""):
        """取消订阅：/fanbox取关 <创作者ID>"""
        cid = parse_creator_id(target)
        if not cid:
            yield event.plain_result("用法：/fanbox取关 <创作者ID>")
            return
        state = await self.remove_subscription(event.unified_msg_origin, cid)
        if state is None:
            yield event.plain_result(f"这里没有订阅 {cid}")
            return
        yield event.plain_result(f"已取消订阅 {state.get('name') or cid}（{cid}）")

    @filter.command("fanbox列表", alias={"fanbox_list"})
    async def list_subscriptions(self, event: AstrMessageEvent):
        """查看这里订阅了哪些 FANBOX 创作者"""
        subs = await self.load_subscriptions()
        per_umo = subs.get(event.unified_msg_origin) or {}
        if not per_umo:
            yield event.plain_result(
                "这里还没有订阅 FANBOX 创作者。用 /fanbox关注 <创作者ID> 添加。"
            )
            return
        lines = [f"这里订阅了 {len(per_umo)} 位 FANBOX 创作者："]
        for cid, state in sorted(per_umo.items()):
            lines.append(f"· {state.get('name') or cid}（{cid}）")
        if self.s.start_from == "subscribe":
            lines.append("推送起点：各自的订阅时间")
        else:
            lines.append(f"推送起点：{self.describe_floor({})}")
        if self.s.max_post_age_hours:
            lines.append(f"发布超过 {self.s.max_post_age_hours} 小时的帖子不推送")
        yield event.plain_result("\n".join(lines))

    @filter.command("fanbox最新", alias={"fanbox_latest"})
    async def latest(self, event: AstrMessageEvent, target: str = ""):
        """查看创作者最新一篇帖子（不影响订阅进度）：/fanbox最新 <创作者ID>"""
        cid = parse_creator_id(target)
        if not cid:
            yield event.plain_result("用法：/fanbox最新 <创作者ID或主页链接>")
            return
        try:
            post = await self.latest_post(cid)
        except FanboxNotFound:
            yield event.plain_result(f"没找到 FANBOX 创作者：{cid}")
            return
        except FanboxError as exc:
            logger.warning(f"[FANBOX] 获取 {cid} 最新帖失败: {exc}")
            yield event.plain_result("FANBOX 暂时访问不了，请稍后再试")
            return
        if post is None:
            yield event.plain_result(f"{cid} 还没有发过帖子")
            return
        for pieces in await self.build_messages(post, post.creator_name, "的最新帖子"):
            yield event.chain_result(self._to_chain(pieces))

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("fanbox检查", alias={"fanbox_check"})
    async def check_command(self, event: AstrMessageEvent):
        """（管理员）立即检查一次全部订阅"""
        sent = await self.check_now()
        yield event.plain_result(f"检查完成，推送了 {sent} 篇新帖")

    @filter.command("fanbox变量", alias={"fanbox_vars"})
    async def list_variables(self, event: AstrMessageEvent):
        """列出推送模板里能用的全部 {变量}"""
        lines = ["推送模板可用的变量（在插件配置的“推送模板”里使用）：", "", "文字："]
        lines += [f"{{{k}}}  {v}" for k, v in TEXT_VARIABLES.items()]
        lines += ["", "图片（放在模板里哪儿，图片就出现在哪儿）："]
        lines += [f"{{{k}}}  {v}" for k, v in IMAGE_VARIABLES.items()]
        lines += [
            "",
            "规则：",
            "· {{ 和 }} 表示花括号本身",
            "· 一行里的变量全为空、这一行又没有其他文字时，整行自动删掉",
            "· 以 ? 开头的行：只要行里有一个变量为空，整行就删掉",
        ]
        yield event.plain_result("\n".join(lines))
