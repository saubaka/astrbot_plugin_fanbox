"""FANBOX 插件页（AstrBot Plugin Pages）的后端接口。"""

from __future__ import annotations

import asyncio
import base64
import re
import time
from typing import Any

from astrbot.api import logger
from astrbot.api.web import error_response, json_response, request

from .fanbox_api import FanboxError, FanboxNotFound
from .fanbox_core import (
    DEFAULT_TEMPLATE,
    IMAGE_VARIABLES,
    START_MODE_LABELS,
    TEXT_VARIABLES,
    format_ts,
    parse_creator_id,
    subscribed_at,
)

PLUGIN_NAME = "astrbot_plugin_fanbox"
MESSAGE_TYPES = {"GroupMessage", "FriendMessage", "OtherMessage"}
GROUP_LIST_TIMEOUT_SECONDS = 6
QQ_RE = re.compile(r"^\d{5,12}$")


def _ms(ts: float | None) -> int | None:
    return int(ts * 1000) if ts else None


def parse_umo(value: Any) -> tuple[str, str, str] | None:
    if not isinstance(value, str) or not value or len(value) > 512:
        return None
    if any(ord(ch) < 32 for ch in value):
        return None
    parts = value.split(":", 2)
    if len(parts) != 3 or not all(parts):
        return None
    if parts[1] not in MESSAGE_TYPES:
        return None
    return parts[0], parts[1], parts[2]


class FanboxWebUI:
    def __init__(self, plugin: Any, context: Any):
        self.plugin = plugin
        self.context = context
        self._group_cache: tuple[float, list[dict]] | None = None
        routes = (
            ("overview", self.overview, ["GET"], "FANBOX 面板数据"),
            ("sessions", self.sessions, ["GET"], "可推送的会话（QQ 群列表）"),
            ("settings/save", self.save_settings, ["POST"], "保存 FANBOX 插件设置"),
            ("subscriptions/add", self.add_subscription, ["POST"], "新增 FANBOX 订阅"),
            (
                "subscriptions/remove",
                self.remove_subscription,
                ["POST"],
                "取消 FANBOX 订阅",
            ),
            ("check", self.check, ["POST"], "立即检查全部 FANBOX 订阅"),
            ("preview", self.preview, ["POST"], "预览推送效果"),
        )
        for endpoint, handler, methods, desc in routes:
            context.register_web_api(
                f"/{PLUGIN_NAME}/{endpoint}", handler, methods, desc
            )

    # ---------- 工具 ----------

    @staticmethod
    async def _payload() -> dict | None:
        data = await request.json(default={})
        return data if isinstance(data, dict) else None

    def _aiocqhttp_platforms(self) -> list[Any]:
        manager = getattr(self.context, "platform_manager", None)
        if manager is None:
            return []
        insts = getattr(manager, "platform_insts", None)
        if insts is None:
            get_insts = getattr(manager, "get_insts", None)
            insts = get_insts() if callable(get_insts) else []
        out = []
        for p in list(insts or []):
            try:
                meta = p.meta()
            except Exception:
                continue
            name = (
                meta.get("name")
                if isinstance(meta, dict)
                else getattr(meta, "name", "")
            )
            if str(name or "").casefold() == "aiocqhttp":
                out.append(p)
        return out

    @staticmethod
    def _meta(platform: Any, field: str) -> str:
        meta = platform.meta()
        value = meta.get(field) if isinstance(meta, dict) else getattr(meta, field, "")
        return str(value or "")

    async def _platform_groups(self) -> list[dict]:
        cached = self._group_cache
        if cached and time.time() - cached[0] < 60:
            return cached[1]
        result = []
        for platform in self._aiocqhttp_platforms():
            pid = self._meta(platform, "id")
            item = {
                "id": pid,
                "name": "aiocqhttp",
                "available": False,
                "error": None,
                "groups": [],
            }
            try:
                client = platform.get_client()
                resp = await asyncio.wait_for(
                    client.call_action(action="get_group_list"),
                    timeout=GROUP_LIST_TIMEOUT_SECONDS,
                )
                groups = (
                    resp.get("data", resp.get("groups", []))
                    if isinstance(resp, dict)
                    else resp
                )
                for g in groups or []:
                    if isinstance(g, dict) and g.get("group_id"):
                        item["groups"].append(
                            {
                                "group_id": str(g.get("group_id")),
                                "group_name": str(g.get("group_name") or "").strip(),
                            }
                        )
                item["available"] = True
            except Exception as exc:
                item["error"] = str(exc) or exc.__class__.__name__
                logger.warning(f"[FANBOX] 获取 QQ 群列表失败 ({pid}): {exc}")
            result.append(item)
        self._group_cache = (time.time(), result)
        return result

    # ---------- 接口 ----------

    async def overview(self):
        try:
            return json_response(await self._build_overview())
        except Exception as exc:
            logger.error(f"[FANBOX] 生成面板数据失败: {exc}")
            return error_response("读取插件数据失败", status_code=500)

    async def _build_overview(self) -> dict:
        p = self.plugin
        s = p.s
        now = time.time()
        subs = await p.load_subscriptions()
        summary = p.stats.summary(now)
        creator_stats = summary.pop("creators")

        sessions = []
        creators: dict[str, dict] = {}
        for umo, per in sorted(subs.items()):
            parsed = parse_umo(umo)
            rows = []
            for cid, state in sorted(per.items()):
                floor = p.floor(state)
                rows.append(
                    {
                        "creator": cid,
                        "name": state.get("name") or cid,
                        "subscribed_at": _ms(subscribed_at(state)),
                        "floor_at": _ms(floor),
                        "last_pushed_post_at": _ms(state.get("last_ts")),
                        "pushed_count": len(state.get("seen") or []),
                    }
                )
                c = creators.setdefault(
                    cid,
                    {"creator": cid, "name": state.get("name") or cid, "sessions": []},
                )
                c["sessions"].append(umo)
            sessions.append(
                {
                    "umo": umo,
                    "platform": parsed[0] if parsed else "",
                    "type": parsed[1] if parsed else "",
                    "session_id": parsed[2] if parsed else umo,
                    "subscriptions": rows,
                }
            )
        for cid, c in creators.items():
            st = creator_stats.get(cid) or {}
            c["name"] = st.get("name") or c["name"]
            c["stats"] = st

        mode = (
            s.start_from
            if not (s.start_from == "custom" and s.custom_start_ts is None)
            else "deploy"
        )
        return {
            "generated_at": _ms(now),
            "version": self._version(),
            "plugin": {
                "deployed_at": _ms(p.deployed_at),
                "last_poll_at": _ms(p.last_poll_at) if p.last_poll_at <= now else None,
                "next_poll_at": _ms(p.next_poll_at),
                "last_poll_sent": p.last_poll_sent,
                "polling": p._lock.locked(),
                "poll_interval": s.poll_interval,
                "push_style": s.push_style,
                "start_from": mode,
                "start_label": START_MODE_LABELS[mode],
                "floor_text": p.describe_floor(),
                "max_post_age_hours": s.max_post_age_hours,
                "offset_hours": s.style.offset_hours,
                "deployed_text": format_ts(p.deployed_at, s.style.offset_hours),
            },
            "stats": summary,
            "sessions": sessions,
            "creators": sorted(creators.values(), key=lambda c: c["creator"]),
            "settings": {
                "schema": p.schema,
                "values": p.setting_values(),
                "warnings": list(p.settings_warnings),
            },
            "template": {
                "default": DEFAULT_TEMPLATE,
                "text_variables": TEXT_VARIABLES,
                "image_variables": IMAGE_VARIABLES,
            },
        }

    def _version(self) -> str:
        try:
            from pathlib import Path

            for line in (
                (Path(__file__).with_name("metadata.yaml"))
                .read_text("utf-8")
                .splitlines()
            ):
                if line.startswith("version:"):
                    return line.split(":", 1)[1].strip()
        except Exception:
            pass
        return ""

    async def sessions(self):
        try:
            return json_response({"platforms": await self._platform_groups()})
        except Exception as exc:
            logger.error(f"[FANBOX] 读取会话列表失败: {exc}")
            return error_response("读取会话列表失败", status_code=500)

    async def save_settings(self):
        payload = await self._payload()
        if payload is None:
            return error_response("请求内容必须是 JSON 对象", status_code=400)
        ok, errors, warnings = await self.plugin.save_settings(payload.get("values"))
        if not ok:
            return error_response("；".join(errors) or "保存失败", status_code=400)
        return json_response({"saved": True, "warnings": warnings})

    def _session_from_payload(self, payload: dict) -> str | None:
        umo = payload.get("umo")
        if parse_umo(umo):
            return umo
        # 也接受 {platform, type, target}，方便页面直接填 QQ 号
        platform = str(payload.get("platform") or "").strip()
        kind = str(payload.get("type") or "").strip()
        target = str(payload.get("target") or "").strip()
        if platform and kind in MESSAGE_TYPES and QQ_RE.fullmatch(target):
            return f"{platform}:{kind}:{target}"
        return None

    async def add_subscription(self):
        payload = await self._payload()
        if payload is None:
            return error_response("请求内容必须是 JSON 对象", status_code=400)
        umo = self._session_from_payload(payload)
        cid = parse_creator_id(str(payload.get("creator") or ""))
        if umo is None:
            return error_response("会话格式不正确", status_code=400)
        if cid is None:
            return error_response("创作者 ID 或链接格式不正确", status_code=400)
        result = await self.plugin.add_subscription(umo, cid)
        reason = result.get("reason")
        if reason == "not_found":
            return error_response(f"没找到 FANBOX 创作者：{cid}", status_code=404)
        if reason == "unavailable":
            return error_response("FANBOX 暂时访问不了，请稍后再试", status_code=502)
        if reason == "exists":
            return error_response("这个会话已经订阅了这位创作者", status_code=409)
        return json_response(result)

    async def remove_subscription(self):
        payload = await self._payload()
        if payload is None:
            return error_response("请求内容必须是 JSON 对象", status_code=400)
        umo = payload.get("umo")
        cid = parse_creator_id(str(payload.get("creator") or ""))
        if not parse_umo(umo) or cid is None:
            return error_response("会话或创作者格式不正确", status_code=400)
        state = await self.plugin.remove_subscription(umo, cid)
        if state is None:
            return error_response("这个会话没有订阅这位创作者", status_code=404)
        return json_response({"removed": True})

    async def check(self):
        if self.plugin._lock.locked():
            return error_response("正在检查中，请稍后", status_code=409)
        try:
            sent = await self.plugin.check_now()
        except Exception as exc:
            logger.error(f"[FANBOX] 插件页触发检查失败: {exc}")
            return error_response("检查失败", status_code=500)
        return json_response({"sent": sent})

    async def preview(self):
        payload = await self._payload()
        if payload is None:
            return error_response("请求内容必须是 JSON 对象", status_code=400)
        cid = parse_creator_id(str(payload.get("creator") or ""))
        if cid is None:
            return error_response("创作者 ID 或链接格式不正确", status_code=400)
        s, errors = self.plugin.preview_settings(payload.get("values"))
        if s is None:
            return error_response("；".join(errors), status_code=400)
        try:
            post = await self.plugin.latest_post(cid)
        except FanboxNotFound:
            return error_response(f"没找到 FANBOX 创作者：{cid}", status_code=404)
        except FanboxError:
            return error_response("FANBOX 暂时访问不了，请稍后再试", status_code=502)
        if post is None:
            return error_response("这位创作者还没有发过帖子", status_code=404)
        t0 = time.monotonic()
        pieces = await self.plugin.build_pieces(
            post, post.creator_name, "发布了新帖", s
        )
        out = []
        for kind, value in pieces:
            if kind == "text":
                out.append({"type": "text", "text": value})
            else:
                mime = "image/png" if value[:4] == b"\x89PNG" else "image/jpeg"
                b64 = base64.b64encode(value).decode("ascii")
                out.append(
                    {
                        "type": "image",
                        "src": f"data:{mime};base64,{b64}",
                        "bytes": len(value),
                    }
                )
        return json_response(
            {
                "creator": cid,
                "post": {"id": post.id, "title": post.title, "url": post.url},
                "style": s.push_style,
                "pieces": out,
                "ms": int((time.monotonic() - t0) * 1000),
            }
        )
