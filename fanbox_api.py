"""FANBOX 公开接口的最小客户端：只请求创作者资料、帖子列表和公开的封面图。

不带登录 cookie，所以拿不到也不会转发付费内容。
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx

API_BASE = "https://api.fanbox.cc"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
MAX_IMAGE_BYTES = 10 * 1024 * 1024


class FanboxError(Exception):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class FanboxNotFound(FanboxError):
    """创作者不存在（FANBOX 对不存在的 ID 返回 400 general_error）。"""


class FanboxBlocked(FanboxError):
    """FANBOX 拒绝了请求（HTTP 403，通常是出口 IP 或客户端被它的规则拦了）。"""


def _is_allowed_image_url(url: str) -> bool:
    parsed = urlparse(url or "")
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (
        host == "pximg.net" or host.endswith(".pximg.net")
    )


class FanboxAPI:
    def __init__(
        self,
        timeout: float = 20.0,
        proxy: str = "",
        user_agent: str = DEFAULT_USER_AGENT,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        kwargs: dict[str, Any] = {
            "timeout": timeout,
            "follow_redirects": False,
            "headers": {
                "User-Agent": user_agent,
                # 不带 Origin 时 api.fanbox.cc 返回 400。
                "Origin": "https://www.fanbox.cc",
                "Referer": "https://www.fanbox.cc/",
                "Accept": "application/json, text/plain, */*",
            },
        }
        if proxy:
            kwargs["proxy"] = proxy
        if transport is not None:
            kwargs["transport"] = transport
        self._client = httpx.AsyncClient(**kwargs)

    async def _get_body(self, path: str, params: dict[str, Any]) -> Any:
        try:
            resp = await self._client.get(API_BASE + path, params=params)
        except httpx.HTTPError as exc:
            raise FanboxError(f"请求 FANBOX 失败: {exc.__class__.__name__}") from exc

        if resp.status_code == 403:
            raise FanboxBlocked("FANBOX 拒绝了请求（HTTP 403）", 403)
        if resp.status_code in (400, 404):
            raise FanboxNotFound(
                f"FANBOX 返回 HTTP {resp.status_code}", resp.status_code
            )
        if resp.status_code != 200:
            raise FanboxError(f"FANBOX 返回 HTTP {resp.status_code}", resp.status_code)
        try:
            data = resp.json()
        except ValueError as exc:
            raise FanboxError("FANBOX 返回的不是 JSON") from exc
        if not isinstance(data, dict) or "body" not in data:
            raise FanboxError("FANBOX 返回格式不对")
        return data["body"]

    async def get_creator(self, creator_id: str) -> dict[str, Any]:
        body = await self._get_body("/creator.get", {"creatorId": creator_id})
        if not isinstance(body, dict):
            raise FanboxNotFound("找不到这个创作者")
        return body

    async def list_posts(self, creator_id: str, limit: int = 10) -> list[Any]:
        body = await self._get_body(
            "/post.listCreator", {"creatorId": creator_id, "limit": limit}
        )
        posts = body.get("posts") if isinstance(body, dict) else body
        if not isinstance(posts, list):
            raise FanboxError("FANBOX 帖子列表格式不对")
        return posts

    async def download_image(self, url: str) -> bytes:
        """下载公开封面图（只允许 pximg.net），超过 10 MB 放弃。"""
        if not _is_allowed_image_url(url):
            raise FanboxError("不允许的图片地址")
        try:
            async with self._client.stream(
                "GET", url, headers={"Accept": "image/*"}
            ) as resp:
                if resp.status_code != 200:
                    raise FanboxError(
                        f"封面下载返回 HTTP {resp.status_code}", resp.status_code
                    )
                buf = bytearray()
                async for chunk in resp.aiter_bytes():
                    buf += chunk
                    if len(buf) > MAX_IMAGE_BYTES:
                        raise FanboxError("封面图太大")
        except httpx.HTTPError as exc:
            raise FanboxError(f"封面下载失败: {exc.__class__.__name__}") from exc
        return bytes(buf)

    async def close(self) -> None:
        await self._client.aclose()
