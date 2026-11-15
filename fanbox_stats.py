"""插件运行统计：检查、推送、报错，按小时分桶，整体存进 AstrBot 的插件 KV。

只用标准库，可以脱离 AstrBot 单独测试。所有时间都是 Unix 秒。
"""

from __future__ import annotations

import time
from typing import Any

HOUR = 3600
KEEP_HOURS = 90 * 24  # 全局按小时统计保留 90 天
CREATOR_KEEP_HOURS = 8 * 24  # 每个创作者的按小时统计保留 8 天（够算 7 天）
LOG_LIMIT = 60  # 推送记录、报错各保留最近多少条
ERROR_KEEP_DAYS = 30

SERIES = ("checks", "pushes", "push_failures", "errors")
CHECK_OUTCOMES = ("ok", "not_found", "blocked", "error")
ERROR_KINDS = (
    "blocked",  # FANBOX 返回 403
    "not_found",  # 创作者不存在或已删除
    "list_failed",  # 获取帖子列表失败
    "send_failed",  # 消息发不出去
    "card_failed",  # 卡片图渲染失败
    "image_failed",  # 封面或头像下载失败
)


def _hour(ts: float) -> int:
    return int(ts // HOUR)


def _int_keys(d: Any) -> dict[int, int]:
    out: dict[int, int] = {}
    if isinstance(d, dict):
        for k, v in d.items():
            try:
                out[int(k)] = int(v)
            except (TypeError, ValueError):
                continue
    return out


def _str_keys(d: dict[int, int]) -> dict[str, int]:
    return {str(k): v for k, v in d.items() if v}


def _window(hourly: dict[int, int], now: float, hours: int) -> int:
    cur = _hour(now)
    return sum(v for h, v in hourly.items() if cur - hours < h <= cur)


def _last24(hourly: dict[int, int], now: float) -> list[int]:
    cur = _hour(now)
    return [hourly.get(cur - 23 + i, 0) for i in range(24)]


def _periods(hourly: dict[int, int], total: int, now: float) -> dict[str, int]:
    return {
        "hour": _window(hourly, now, 1),
        "day": _window(hourly, now, 24),
        "week": _window(hourly, now, 24 * 7),
        "total": total,
    }


class Stats:
    def __init__(self, data: Any = None):
        d = data if isinstance(data, dict) else {}
        series = d.get("series") if isinstance(d.get("series"), dict) else {}
        self.series: dict[str, dict[int, int]] = {
            k: _int_keys(series.get(k)) for k in SERIES
        }
        totals = d.get("totals") if isinstance(d.get("totals"), dict) else {}
        self.totals: dict[str, int] = {}
        for k in SERIES + ("card_renders", "card_failures", "card_ms_total"):
            try:
                self.totals[k] = int(totals.get(k) or 0)
            except (TypeError, ValueError):
                self.totals[k] = 0
        self.creators: dict[str, dict[str, Any]] = {}
        for cid, c in (d.get("creators") or {}).items():
            if isinstance(c, dict):
                self.creators[str(cid)] = self._load_creator(c)
        self.pushes: list[dict[str, Any]] = [
            p for p in d.get("pushes") or [] if isinstance(p, dict)
        ]
        self.errors: list[dict[str, Any]] = [
            e for e in d.get("errors") or [] if isinstance(e, dict)
        ]
        self.seq = int(d.get("seq") or 0)
        self.since = float(d.get("since") or 0.0)

    # ---------- 读写 ----------

    @staticmethod
    def _load_creator(c: dict[str, Any]) -> dict[str, Any]:
        out = dict(c)
        hourly = c.get("hourly") if isinstance(c.get("hourly"), dict) else {}
        out["hourly"] = {k: _int_keys(hourly.get(k)) for k in ("checks", "pushes")}
        counts = c.get("counts") if isinstance(c.get("counts"), dict) else {}
        out["counts"] = {}
        for k in CHECK_OUTCOMES + ("checks", "pushes", "push_failures"):
            try:
                out["counts"][k] = int(counts.get(k) or 0)
            except (TypeError, ValueError):
                out["counts"][k] = 0
        outcomes = (
            c.get("outcomes_hourly")
            if isinstance(c.get("outcomes_hourly"), dict)
            else {}
        )
        out["outcomes_hourly"] = {k: _int_keys(outcomes.get(k)) for k in CHECK_OUTCOMES}
        return out

    def to_dict(self) -> dict[str, Any]:
        creators = {}
        for cid, c in self.creators.items():
            cc = dict(c)
            cc["hourly"] = {k: _str_keys(v) for k, v in c["hourly"].items()}
            cc["outcomes_hourly"] = {
                k: _str_keys(v) for k, v in c["outcomes_hourly"].items()
            }
            creators[cid] = cc
        return {
            "version": 1,
            "since": self.since,
            "seq": self.seq,
            "series": {k: _str_keys(v) for k, v in self.series.items()},
            "totals": dict(self.totals),
            "creators": creators,
            "pushes": self.pushes[:LOG_LIMIT],
            "errors": self.errors[:LOG_LIMIT],
        }

    def prune(self, now: float | None = None) -> None:
        now = time.time() if now is None else now
        cur = _hour(now)
        for k in SERIES:
            self.series[k] = {
                h: v for h, v in self.series[k].items() if h > cur - KEEP_HOURS
            }
        for c in self.creators.values():
            for key in ("hourly", "outcomes_hourly"):
                for k, v in c[key].items():
                    c[key][k] = {
                        h: n for h, n in v.items() if h > cur - CREATOR_KEEP_HOURS
                    }
        cutoff = now - ERROR_KEEP_DAYS * 86400
        self.errors = [e for e in self.errors if float(e.get("at") or 0) >= cutoff][
            :LOG_LIMIT
        ]
        self.pushes = self.pushes[:LOG_LIMIT]

    # ---------- 记录 ----------

    def _bump(self, series: str, now: float, n: int = 1) -> None:
        h = _hour(now)
        self.series[series][h] = self.series[series].get(h, 0) + n
        self.totals[series] = self.totals.get(series, 0) + n
        if not self.since:
            self.since = now

    def _creator(self, cid: str) -> dict[str, Any]:
        c = self.creators.get(cid)
        if c is None:
            c = self._load_creator({})
            self.creators[cid] = c
        return c

    def _next_id(self) -> int:
        self.seq += 1
        return self.seq

    def record_check(
        self,
        cid: str,
        outcome: str,
        latency_ms: int,
        now: float | None = None,
        *,
        name: str = "",
        icon_url: str = "",
        latest: dict[str, Any] | None = None,
        post_count: int | None = None,
        message: str = "",
    ) -> None:
        now = time.time() if now is None else now
        outcome = outcome if outcome in CHECK_OUTCOMES else "error"
        self._bump("checks", now)
        c = self._creator(cid)
        h = _hour(now)
        c["hourly"]["checks"][h] = c["hourly"]["checks"].get(h, 0) + 1
        c["outcomes_hourly"][outcome][h] = c["outcomes_hourly"][outcome].get(h, 0) + 1
        c["counts"]["checks"] += 1
        c["counts"][outcome] += 1
        c["last_check_at"] = now
        c["last_outcome"] = outcome
        c["last_latency_ms"] = int(latency_ms)
        prev = c.get("avg_latency_ms")
        c["avg_latency_ms"] = int(
            latency_ms if prev is None else prev * 0.8 + latency_ms * 0.2
        )
        if outcome == "ok":
            c["last_ok_at"] = now
            c["last_error"] = ""
        else:
            c["last_error"] = message
        if name:
            c["name"] = name
        if icon_url:
            c["icon_url"] = icon_url
        if latest is not None:
            c["latest"] = latest
        if post_count is not None:
            c["post_count"] = post_count

    def record_push(
        self,
        cid: str,
        *,
        name: str,
        post_id: str,
        title: str,
        post_url: str,
        umo: str,
        style: str,
        ok: bool,
        error: str = "",
        now: float | None = None,
    ) -> None:
        now = time.time() if now is None else now
        series = "pushes" if ok else "push_failures"
        self._bump(series, now)
        c = self._creator(cid)
        c["counts"][series] += 1
        if ok:
            h = _hour(now)
            c["hourly"]["pushes"][h] = c["hourly"]["pushes"].get(h, 0) + 1
            c["last_push_at"] = now
        self.pushes.insert(
            0,
            {
                "id": self._next_id(),
                "at": now,
                "creator": cid,
                "name": name,
                "post_id": post_id,
                "title": title,
                "url": post_url,
                "umo": umo,
                "style": style,
                "ok": bool(ok),
                "error": error,
            },
        )
        del self.pushes[LOG_LIMIT:]

    def record_error(
        self,
        kind: str,
        message: str,
        *,
        creator: str = "",
        umo: str = "",
        post_id: str = "",
        now: float | None = None,
    ) -> None:
        now = time.time() if now is None else now
        self._bump("errors", now)
        self.errors.insert(
            0,
            {
                "id": self._next_id(),
                "at": now,
                "kind": kind if kind in ERROR_KINDS else "list_failed",
                "creator": creator,
                "umo": umo,
                "post_id": post_id,
                "message": str(message)[:500],
            },
        )
        del self.errors[LOG_LIMIT:]

    def record_card(self, ok: bool, ms: int) -> None:
        self.totals["card_renders"] = self.totals.get("card_renders", 0) + 1
        if ok:
            self.totals["card_ms_total"] = self.totals.get("card_ms_total", 0) + int(ms)
        else:
            self.totals["card_failures"] = self.totals.get("card_failures", 0) + 1

    def forget_creator(self, cid: str) -> None:
        self.creators.pop(cid, None)

    # ---------- 给页面用的汇总 ----------

    def summary(self, now: float | None = None) -> dict[str, Any]:
        now = time.time() if now is None else now
        series = {
            k: {
                "periods": _periods(self.series[k], self.totals.get(k, 0), now),
                "hourly": _last24(self.series[k], now),
            }
            for k in SERIES
        }
        renders = self.totals.get("card_renders", 0)
        ok_renders = renders - self.totals.get("card_failures", 0)
        creators = {}
        for cid, c in self.creators.items():
            creators[cid] = {
                "name": c.get("name", ""),
                "icon_url": c.get("icon_url", ""),
                "latest": c.get("latest"),
                "post_count": c.get("post_count"),
                "last_check_at": c.get("last_check_at"),
                "last_ok_at": c.get("last_ok_at"),
                "last_push_at": c.get("last_push_at"),
                "last_outcome": c.get("last_outcome"),
                "last_error": c.get("last_error", ""),
                "last_latency_ms": c.get("last_latency_ms"),
                "avg_latency_ms": c.get("avg_latency_ms"),
                "counts": dict(c["counts"]),
                "checks": _periods(c["hourly"]["checks"], c["counts"]["checks"], now),
                "pushes": _periods(c["hourly"]["pushes"], c["counts"]["pushes"], now),
                "hourly_checks": _last24(c["hourly"]["checks"], now),
                "hourly_pushes": _last24(c["hourly"]["pushes"], now),
                "outcomes_day": {
                    k: _window(c["outcomes_hourly"][k], now, 24) for k in CHECK_OUTCOMES
                },
            }
        return {
            "since": self.since,
            "series": series,
            "card": {
                "renders": renders,
                "failures": self.totals.get("card_failures", 0),
                "avg_ms": int(self.totals.get("card_ms_total", 0) / ok_renders)
                if ok_renders > 0
                else None,
            },
            "creators": creators,
            "pushes": self.pushes[:LOG_LIMIT],
            "errors": self.errors[:LOG_LIMIT],
        }
