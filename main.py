"""
AstrBot FANBOX 新帖推送插件

订阅 pixivFANBOX 创作者，有新帖时把标题、档位、摘要、封面和链接推到订阅的会话。
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
    DEFAULT_TEMPLATE,
    IMAGE_VARIABLES,
    START_MODE_LABELS,
    START_MODES,
    TEXT_VARIABLES,
    Post,
    StyleOptions,
    advance_state,
    build_variables,
    format_ts,
    initial_state,
    parse_creator_id,
    parse_posts,
    parse_start_time,
    render_template,
    select_new_posts,
    start_floor,
    subscribed_at,
    unknown_variables,
)

KV_SUBSCRIPTIONS = "fanbox_subscriptions_v1"
KV_DEPLOYED_AT = "fanbox_deployed_at"
LIST_LIMIT = 10
PUSH_STYLES = {"text", "card"}

# 每个配置项所在的分组；也兼容 v0.1.0 的扁平配置
CONFIG_SECTIONS = {
    "poll_interval_minutes": "basic",
    "max_new_posts_per_poll": "basic",
    "proxy": "basic",
    "start_from": "start",
    "start_time": "start",
    "max_post_age_hours": "start",
    "push_style": "style",
    "message_template": "style",
    "send_cover": "style",
    "send_adult_cover": "style",
    "show_fee": "content",
    "show_timezone": "content",
    "show_tags": "content",
    "show_adult_mark": "content",
    "excerpt_max_chars": "content",
    "max_tags": "content",
    "time_format": "content",
    "timezone_offset_hours": "content",
    "card_show_likes": "card",
    "card_excerpt_lines": "card",
    "card_title_lines": "card",
    "card_font_path": "card",
    "card_bold_font_path": "card",
}


class _Config:
    def __init__(self, config: Any):
        self._config = config if config is not None else {}

    def get(self, key: str, default: Any) -> Any:
        section = self._config.get(CONFIG_SECTIONS.get(key, ""), None)
        if isinstance(section, dict) and key in section:
            return section[key]
        return self._config.get(key, default)

    def int(self, key: str, default: int, minimum: int | None = None) -> int:
        try:
            value = int(self.get(key, default))
        except (TypeError, ValueError):
            value = default
        return value if minimum is None else max(minimum, value)

    def bool(self, key: str, default: bool) -> bool:
        value = self.get(key, default)
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)

    def str(self, key: str, default: str) -> str:
        value = self.get(key, default)
        return default if value is None else str(value)


class FanboxPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        cfg = _Config(config)
        self.poll_interval = cfg.int("poll_interval_minutes", 10, 5)
        self.max_new_per_poll = cfg.int("max_new_posts_per_poll", 3, 1)
        self.api = FanboxAPI(proxy=cfg.str("proxy", "").strip())

        self.push_style = cfg.str("push_style", "text").strip().lower()
        if self.push_style not in PUSH_STYLES:
            logger.warning(f"[FANBOX] 未知的推送样式 {self.push_style!r}，改用 text")
            self.push_style = "text"
        self.template = cfg.str("message_template", "") or DEFAULT_TEMPLATE
        bad = unknown_variables(self.template)
        if bad:
            logger.warning(
                "[FANBOX] 推送模板里有不认识的变量，会原样显示: "
                + "、".join("{" + b + "}" for b in bad)
            )
        self.send_cover = cfg.bool("send_cover", True)
        self.send_adult_cover = cfg.bool("send_adult_cover", False)

        self.style = StyleOptions(
            excerpt_max=cfg.int("excerpt_max_chars", 120, 0),
            offset_hours=cfg.int("timezone_offset_hours", 8),
            show_fee=cfg.bool("show_fee", True),
            show_timezone=cfg.bool("show_timezone", True),
            show_tags=cfg.bool("show_tags", True),
            show_adult_mark=cfg.bool("show_adult_mark", True),
            time_format=cfg.str("time_format", "%Y-%m-%d %H:%M") or "%Y-%m-%d %H:%M",
            max_tags=cfg.int("max_tags", 6, 0),
        )
        self.card_show_likes = cfg.bool("card_show_likes", True)
        self.card_excerpt_lines = cfg.int("card_excerpt_lines", 2, 0)
        self.card_title_lines = cfg.int("card_title_lines", 2, 1)
        self.card_font_path = cfg.str("card_font_path", "").strip()
        self.card_bold_font_path = cfg.str("card_bold_font_path", "").strip()

        self.start_from = cfg.str("start_from", "deploy").strip().lower()
        if self.start_from not in START_MODES:
            logger.warning(f"[FANBOX] 未知的推送起点 {self.start_from!r}，改用 deploy")
            self.start_from = "deploy"
        start_time_text = cfg.str("start_time", "").strip()
        self.custom_start_ts = parse_start_time(
            start_time_text, self.style.offset_hours
        )
        if self.start_from == "custom" and self.custom_start_ts is None:
            logger.warning(
                f"[FANBOX] 自定义起点时间 {start_time_text!r} 无法解析，"
                "改用插件部署时间作为起点"
            )
        self.max_post_age_hours = cfg.int("max_post_age_hours", 0, 0)
        # 真正的部署时间在 initialize() 里从 KV 读取（第一次启动时写入）
        self.deployed_at = time.time()

        self._lock = asyncio.Lock()
        self._running = False
        self._task: asyncio.Task | None = None

    # ---------- 生命周期 ----------

    async def initialize(self):
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
                f"{format_ts(self.deployed_at, self.style.offset_hours)}"
            )
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info(
            f"[FANBOX] 插件已启动，轮询间隔 {self.poll_interval} 分钟，"
            f"推送样式 {self.push_style}，推送起点 {self._describe_floor()}"
        )

    def _floor(self, state: dict[str, Any]) -> float:
        return start_floor(
            self.start_from,
            deployed_at=self.deployed_at,
            subscribed=subscribed_at(state),
            custom_ts=self.custom_start_ts,
        )

    def _describe_floor(self, state: dict[str, Any] | None = None) -> str:
        mode = self.start_from
        if mode == "custom" and self.custom_start_ts is None:
            mode = "deploy"
        label = START_MODE_LABELS[mode]
        if mode == "subscribe" and state is None:
            return label
        floor = self._floor(state or {})
        return f"{label} {format_ts(floor, self.style.offset_hours)}"

    async def terminate(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.api.close()
        logger.info("[FANBOX] 插件已停止")

    # ---------- 订阅存储 ----------

    async def _load(self) -> dict[str, dict[str, dict[str, Any]]]:
        data = await self.get_kv_data(KV_SUBSCRIPTIONS, {})
        return data if isinstance(data, dict) else {}

    async def _save(self, data: dict[str, dict[str, dict[str, Any]]]) -> None:
        await self.put_kv_data(KV_SUBSCRIPTIONS, data)

    # ---------- 轮询 ----------

    async def _poll_loop(self):
        # 等平台适配器连上，再错开一点时间，避免和其他插件同时发请求。
        await asyncio.sleep(random.uniform(30, 90))
        while self._running:
            try:
                await self._poll_once()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error(f"[FANBOX] 轮询出错: {exc}")
            await asyncio.sleep(self.poll_interval * 60)

    async def _poll_once(self) -> int:
        """检查全部订阅，返回这次推送出去的帖子数。"""
        total_sent = 0
        async with self._lock:
            subs = await self._load()
            creators = sorted({cid for per_umo in subs.values() for cid in per_umo})
            for cid in creators:
                try:
                    posts = parse_posts(await self.api.list_posts(cid, LIST_LIMIT))
                except FanboxBlocked as exc:
                    logger.warning(f"[FANBOX] {cid}: {exc}，本轮跳过")
                    continue
                except FanboxError as exc:
                    logger.warning(f"[FANBOX] 获取 {cid} 的帖子列表失败: {exc}")
                    continue

                changed = False
                for umo, per_umo in subs.items():
                    state = per_umo.get(cid)
                    if state is None:
                        continue
                    fresh = select_new_posts(
                        posts,
                        state,
                        self._floor(state),
                        time.time(),
                        self.max_post_age_hours,
                    )
                    if len(fresh) > self.max_new_per_poll:
                        logger.info(
                            f"[FANBOX] {cid} 有 {len(fresh)} 篇新帖，"
                            f"只推送最新的 {self.max_new_per_poll} 篇"
                        )
                        fresh = fresh[-self.max_new_per_poll :]
                    sent: list[Post] = []
                    for post in fresh:
                        if not await self._send_post(umo, post, state.get("name", "")):
                            break
                        sent.append(post)
                    if sent:
                        per_umo[cid] = advance_state(state, sent)
                        total_sent += len(sent)
                        changed = True
                if changed:
                    await self._save(subs)
                await asyncio.sleep(random.uniform(1.0, 3.0))
        return total_sent

    # ---------- 发送 ----------

    def _cover_allowed(self, post: Post) -> bool:
        return bool(post.cover_url) and (self.send_adult_cover or not post.adult)

    async def _download(self, url: str, cache: dict[str, bytes | None]) -> bytes | None:
        if not url:
            return None
        if url not in cache:
            try:
                cache[url] = await self.api.download_image(url)
            except FanboxError as exc:
                logger.warning(f"[FANBOX] 图片下载失败: {exc}")
                cache[url] = None
        return cache[url]

    async def _render_card(
        self, post: Post, name: str, cache: dict[str, bytes | None]
    ) -> bytes:
        hide_cover = post.adult and not self.send_adult_cover
        cover = None if hide_cover else await self._download(post.cover_url, cache)
        avatar = await self._download(post.creator_icon_url, cache)
        opts = CardOptions(
            show_fee=self.style.show_fee,
            show_timezone=self.style.show_timezone,
            show_adult_mark=self.style.show_adult_mark,
            show_likes=self.card_show_likes,
            excerpt_lines=self.card_excerpt_lines,
            title_lines=self.card_title_lines,
            offset_hours=self.style.offset_hours,
            hide_cover=hide_cover,
            font_path=self.card_font_path,
            bold_font_path=self.card_bold_font_path,
        )
        # Pillow 画图是 CPU 活，放到线程里，别卡住机器人
        return await asyncio.to_thread(render_card, post, name, cover, avatar, opts)

    async def _image_component(
        self, kind: str, post: Post, name: str, cache: dict[str, bytes | None]
    ):
        if kind == "cover_image":
            if not (self.send_cover and self._cover_allowed(post)):
                return None
            data = await self._download(post.cover_url, cache)
        elif kind == "avatar_image":
            data = await self._download(post.creator_icon_url, cache)
        elif kind == "card_image":
            try:
                data = await self._render_card(post, name, cache)
            except Exception as exc:
                logger.warning(f"[FANBOX] 帖子 {post.id} 卡片图渲染失败: {exc}")
                data = None
        else:
            data = None
        return Image.fromBytes(data) if data else None

    async def _build_chain(
        self, post: Post, name: str, headline: str = "发布了新帖"
    ) -> list:
        cache: dict[str, bytes | None] = {}
        name = name or post.creator_name or post.creator_id
        if self.push_style == "card":
            try:
                return [Image.fromBytes(await self._render_card(post, name, cache))]
            except Exception as exc:
                logger.warning(
                    f"[FANBOX] 帖子 {post.id} 卡片图渲染失败，改发文字模板: {exc}"
                )

        values = build_variables(
            post, name, self.style, headline, self._cover_allowed(post)
        )
        chain: list = []
        for kind, value in render_template(self.template, values):
            if kind == "text":
                chain.append(Plain(value))
                continue
            comp = await self._image_component(value, post, name, cache)
            if comp is not None:
                chain.append(comp)
        return chain or [Plain(post.url)]

    async def _send_post(self, umo: str, post: Post, name: str) -> bool:
        chain = await self._build_chain(post, name)
        try:
            ok = await self.context.send_message(umo, MessageChain(chain=chain))
        except Exception as exc:
            logger.warning(f"[FANBOX] 推送帖子 {post.id} 到 {umo} 失败: {exc}")
            return False
        if ok is False:
            logger.warning(f"[FANBOX] 推送帖子 {post.id} 到 {umo} 失败：找不到会话")
            return False
        logger.info(f"[FANBOX] 已推送 {post.creator_id}/{post.id} 到 {umo}")
        return True

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
        try:
            creator = await self.api.get_creator(cid)
            posts = parse_posts(await self.api.list_posts(cid, LIST_LIMIT))
        except FanboxNotFound:
            yield event.plain_result(f"没找到 FANBOX 创作者：{cid}")
            return
        except FanboxError as exc:
            logger.warning(f"[FANBOX] 订阅 {cid} 时请求失败: {exc}")
            yield event.plain_result(
                f"订阅 {cid} 失败：FANBOX 暂时访问不了，请稍后再试"
            )
            return

        user = creator.get("user") if isinstance(creator.get("user"), dict) else {}
        name = str(user.get("name") or cid)
        umo = event.unified_msg_origin
        now = time.time()
        state = initial_state(name, now)
        async with self._lock:
            subs = await self._load()
            per_umo = subs.setdefault(umo, {})
            already = cid in per_umo
            if not already:
                per_umo[cid] = state
                await self._save(subs)
        if already:
            yield event.plain_result(f"这里已经订阅了 {name}（{cid}）")
            return

        pending = select_new_posts(
            posts, state, self._floor(state), now, self.max_post_age_hours
        )
        lines = [f"已订阅 FANBOX：{name}（{cid}）"]
        lines.append(
            f"推送起点：{self._describe_floor(state)}，更早发布的帖子不会推送。"
        )
        if pending:
            n = min(len(pending), self.max_new_per_poll)
            lines.append(
                f"起点之后已经发布了 {len(pending)} 篇，下次检查时会推送其中 {n} 篇。"
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
        umo = event.unified_msg_origin
        async with self._lock:
            subs = await self._load()
            per_umo = subs.get(umo) or {}
            state = per_umo.pop(cid, None)
            if state is not None:
                if not per_umo:
                    subs.pop(umo, None)
                await self._save(subs)
        if state is None:
            yield event.plain_result(f"这里没有订阅 {cid}")
            return
        yield event.plain_result(f"已取消订阅 {state.get('name') or cid}（{cid}）")

    @filter.command("fanbox列表", alias={"fanbox_list"})
    async def list_subscriptions(self, event: AstrMessageEvent):
        """查看这里订阅了哪些 FANBOX 创作者"""
        subs = await self._load()
        per_umo = subs.get(event.unified_msg_origin) or {}
        if not per_umo:
            yield event.plain_result(
                "这里还没有订阅 FANBOX 创作者。用 /fanbox关注 <创作者ID> 添加。"
            )
            return
        lines = [f"这里订阅了 {len(per_umo)} 位 FANBOX 创作者："]
        for cid, state in sorted(per_umo.items()):
            lines.append(f"· {state.get('name') or cid}（{cid}）")
        if self.start_from == "subscribe":
            lines.append("推送起点：各自的订阅时间")
        else:
            lines.append(f"推送起点：{self._describe_floor({})}")
        if self.max_post_age_hours:
            lines.append(f"发布超过 {self.max_post_age_hours} 小时的帖子不推送")
        yield event.plain_result("\n".join(lines))

    @filter.command("fanbox最新", alias={"fanbox_latest"})
    async def latest(self, event: AstrMessageEvent, target: str = ""):
        """查看创作者最新一篇帖子（不影响订阅进度）：/fanbox最新 <创作者ID>"""
        cid = parse_creator_id(target)
        if not cid:
            yield event.plain_result("用法：/fanbox最新 <创作者ID或主页链接>")
            return
        try:
            posts = parse_posts(await self.api.list_posts(cid, LIST_LIMIT))
        except FanboxNotFound:
            yield event.plain_result(f"没找到 FANBOX 创作者：{cid}")
            return
        except FanboxError as exc:
            logger.warning(f"[FANBOX] 获取 {cid} 最新帖失败: {exc}")
            yield event.plain_result("FANBOX 暂时访问不了，请稍后再试")
            return
        if not posts:
            yield event.plain_result(f"{cid} 还没有发过帖子")
            return
        post = max(posts, key=lambda p: p.ts)
        yield event.chain_result(
            await self._build_chain(post, post.creator_name, "的最新帖子")
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("fanbox检查", alias={"fanbox_check"})
    async def check_now(self, event: AstrMessageEvent):
        """（管理员）立即检查一次全部订阅"""
        sent = await self._poll_once()
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
