"""插件设置：按 _conf_schema.json 读取、校验、整理成 Settings。

插件启动、插件页保存设置、插件页"预览"都走这里，保证三处规则一致。只用标准库。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from .fanbox_core import (
        CARD_ELEMENT,
        CARD_TEXT_MODES,
        DEFAULT_CARD_TEMPLATE,
        DEFAULT_TEMPLATE,
        START_MODES,
        StyleOptions,
        ensure_card_element,
        parse_start_time,
        unknown_variables,
    )
except ImportError:  # 测试时作为顶层模块导入
    from fanbox_core import (
        CARD_ELEMENT,
        CARD_TEXT_MODES,
        DEFAULT_CARD_TEMPLATE,
        DEFAULT_TEMPLATE,
        START_MODES,
        StyleOptions,
        ensure_card_element,
        parse_start_time,
        unknown_variables,
    )

SCHEMA_PATH = Path(__file__).with_name("_conf_schema.json")
PUSH_STYLES = ("text", "card")

# 数字配置的取值范围（闭区间）；None 表示不限
INT_RANGES: dict[str, tuple[int | None, int | None]] = {
    "poll_interval_minutes": (5, 1440),
    "max_new_posts_per_poll": (1, 20),
    "max_post_age_hours": (0, 24 * 365),
    "excerpt_max_chars": (0, 2000),
    "max_tags": (0, 30),
    "timezone_offset_hours": (-12, 14),
    "card_excerpt_lines": (0, 6),
    "card_title_lines": (1, 4),
}
MAX_TEXT = {"message_template": 4000, "card_template": 4000}
MAX_STRING = 500


def load_schema(path: Path | None = None) -> dict[str, Any]:
    with open(path or SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def key_sections(schema: dict[str, Any]) -> dict[str, str]:
    """配置项 → 所在分组。"""
    return {
        key: group for group, body in schema.items() for key in body.get("items", {})
    }


def current_values(config: Any, schema: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """读出当前全部配置（缺的用默认值）。也兼容 v0.1.0 的扁平配置。"""
    config = config if config is not None else {}
    out: dict[str, dict[str, Any]] = {}
    for group, body in schema.items():
        section = config.get(group) if hasattr(config, "get") else None
        section = section if isinstance(section, dict) else {}
        out[group] = {}
        for key, item in body.get("items", {}).items():
            if key in section:
                value = section[key]
            elif hasattr(config, "get") and key in config:
                value = config.get(key)
            else:
                value = item.get("default")
            if key == "card_template" and isinstance(value, str):
                value = ensure_card_element(value)
            out[group][key] = value
    return out


def _coerce(key: str, item: dict[str, Any], value: Any) -> tuple[Any, str | None]:
    """把一个值按 schema 转成正确类型；失败返回 (None, 错误说明)。"""
    kind = item.get("type")
    label = item.get("description") or key
    if kind == "bool":
        if isinstance(value, bool):
            return value, None
        return None, f"{label}：必须是开或关"
    if kind == "int":
        if isinstance(value, bool):
            return None, f"{label}：必须是整数"
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            value = int(value.strip())
        if not isinstance(value, int):
            return None, f"{label}：必须是整数"
        lo, hi = INT_RANGES.get(key, (None, None))
        if lo is not None and value < lo:
            return None, f"{label}：不能小于 {lo}"
        if hi is not None and value > hi:
            return None, f"{label}：不能大于 {hi}"
        return value, None
    if kind in ("string", "text"):
        if value is None:
            value = ""
        if not isinstance(value, str):
            return None, f"{label}：必须是文字"
        limit = MAX_TEXT.get(key, 20000 if kind == "text" else MAX_STRING)
        if len(value) > limit:
            return None, f"{label}：太长了（最多 {limit} 个字）"
        options = item.get("options")
        if options and value not in options:
            return None, f"{label}：只能是 {' / '.join(options)}"
        return value, None
    return value, None


def validate(
    patch: Any,
    schema: dict[str, Any],
    base: dict[str, dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """把页面提交的 {分组: {配置项: 值}} 校验后合并进 base。返回 (合并结果, 错误列表)。

    只接受 schema 里有的分组和配置项；没提交的配置项保持原值。
    """
    merged = {g: dict(v) for g, v in base.items()}
    errors: list[str] = []
    if not isinstance(patch, dict):
        return merged, ["提交的内容必须是 {分组: {配置项: 值}}"]
    for group, values in patch.items():
        body = schema.get(group)
        if body is None or not isinstance(values, dict):
            errors.append(f"未知的配置分组：{group}")
            continue
        items = body.get("items", {})
        for key, value in values.items():
            item = items.get(key)
            if item is None:
                errors.append(f"未知的配置项：{group}.{key}")
                continue
            clean, err = _coerce(key, item, value)
            if err:
                errors.append(err)
            else:
                merged[group][key] = clean

    # 跨配置项的检查
    start = merged.get("start", {})
    content = merged.get("content", {})
    if start.get("start_from") == "custom":
        offset = content.get("timezone_offset_hours", 8)
        if parse_start_time(start.get("start_time", ""), int(offset or 0)) is None:
            errors.append("自定义起点时间：格式不对，例如 2026-11-15 08:00")
    card_tpl = merged.get("style", {}).get("card_template") or ""
    if card_tpl and card_tpl.count(CARD_ELEMENT) != 1:
        errors.append("卡片图配文模板：必须保留且只能有一个 {card_image}（卡片图本身）")
    fmt = content.get("time_format") or ""
    if fmt:
        try:
            datetime(2026, 1, 2, 3, 4).strftime(fmt)
        except (ValueError, TypeError):
            errors.append("时间格式：不是有效的 strftime 格式")
    return merged, errors


@dataclass
class Settings:
    poll_interval: int = 10
    max_new_per_poll: int = 3
    proxy: str = ""
    start_from: str = "deploy"
    start_time_text: str = ""
    custom_start_ts: float | None = None
    max_post_age_hours: int = 0
    push_style: str = "text"
    template: str = DEFAULT_TEMPLATE
    template_is_default: bool = True
    card_text: str = "merge"
    card_template: str = DEFAULT_CARD_TEMPLATE
    card_template_is_default: bool = True
    send_cover: bool = True
    send_adult_cover: bool = False
    creator_cover_fallback: bool = True
    style: StyleOptions = field(default_factory=StyleOptions)
    card_show_likes: bool = True
    card_excerpt_lines: int = 2
    card_title_lines: int = 2
    card_font_path: str = ""
    card_bold_font_path: str = ""


def _int(v: Any, default: int, key: str) -> int:
    try:
        value = int(v)
    except (TypeError, ValueError):
        value = default
    lo, hi = INT_RANGES.get(key, (None, None))
    if lo is not None:
        value = max(lo, value)
    if hi is not None:
        value = min(hi, value)
    return value


def _bool(v: Any, default: bool) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in {"1", "true", "yes", "on"}
    return default if v is None else bool(v)


def _str(v: Any) -> str:
    return "" if v is None else str(v)


def build_settings(values: dict[str, dict[str, Any]]) -> tuple[Settings, list[str]]:
    """把配置值整理成 Settings。值不合法时用默认值，并在 warnings 里说明。"""
    flat: dict[str, Any] = {}
    for group in values.values():
        flat.update(group)
    warnings: list[str] = []

    push_style = _str(flat.get("push_style", "text")).strip().lower()
    if push_style not in PUSH_STYLES:
        warnings.append(f"未知的推送样式 {push_style!r}，改用 text")
        push_style = "text"
    raw_template = _str(flat.get("message_template", ""))
    template = raw_template or DEFAULT_TEMPLATE
    bad = unknown_variables(template)
    if bad:
        warnings.append(
            "推送模板里有不认识的变量，会原样显示: "
            + "、".join("{" + b + "}" for b in bad)
        )
    card_text = _str(flat.get("card_text", "merge")).strip().lower()
    if card_text not in CARD_TEXT_MODES:
        warnings.append(f"未知的卡片图配文方式 {card_text!r}，改用 merge")
        card_text = "merge"
    raw_card_template = ensure_card_element(_str(flat.get("card_template", "")))
    card_template = raw_card_template or DEFAULT_CARD_TEMPLATE
    bad = unknown_variables(card_template)
    if bad:
        warnings.append(
            "卡片图配文模板里有不认识的变量，会原样显示: "
            + "、".join("{" + b + "}" for b in bad)
        )

    style = StyleOptions(
        excerpt_max=_int(flat.get("excerpt_max_chars", 120), 120, "excerpt_max_chars"),
        offset_hours=_int(
            flat.get("timezone_offset_hours", 8), 8, "timezone_offset_hours"
        ),
        show_fee=_bool(flat.get("show_fee"), True),
        show_timezone=_bool(flat.get("show_timezone"), True),
        show_tags=_bool(flat.get("show_tags"), True),
        show_adult_mark=_bool(flat.get("show_adult_mark"), True),
        time_format=_str(flat.get("time_format")) or "%Y-%m-%d %H:%M",
        max_tags=_int(flat.get("max_tags", 6), 6, "max_tags"),
    )

    start_from = _str(flat.get("start_from", "deploy")).strip().lower()
    if start_from not in START_MODES:
        warnings.append(f"未知的推送起点 {start_from!r}，改用 deploy")
        start_from = "deploy"
    start_time_text = _str(flat.get("start_time")).strip()
    custom_ts = parse_start_time(start_time_text, style.offset_hours)
    if start_from == "custom" and custom_ts is None:
        warnings.append(
            f"自定义起点时间 {start_time_text!r} 无法解析，改用插件部署时间作为起点"
        )

    s = Settings(
        poll_interval=_int(
            flat.get("poll_interval_minutes", 10), 10, "poll_interval_minutes"
        ),
        max_new_per_poll=_int(
            flat.get("max_new_posts_per_poll", 3), 3, "max_new_posts_per_poll"
        ),
        proxy=_str(flat.get("proxy")).strip(),
        start_from=start_from,
        start_time_text=start_time_text,
        custom_start_ts=custom_ts,
        max_post_age_hours=_int(
            flat.get("max_post_age_hours", 0), 0, "max_post_age_hours"
        ),
        push_style=push_style,
        template=template,
        template_is_default=(not raw_template) or raw_template == DEFAULT_TEMPLATE,
        card_text=card_text,
        card_template=card_template,
        card_template_is_default=(not raw_card_template)
        or raw_card_template == DEFAULT_CARD_TEMPLATE,
        send_cover=_bool(flat.get("send_cover"), True),
        send_adult_cover=_bool(flat.get("send_adult_cover"), False),
        creator_cover_fallback=_bool(flat.get("creator_cover_fallback"), True),
        style=style,
        card_show_likes=_bool(flat.get("card_show_likes"), True),
        card_excerpt_lines=_int(
            flat.get("card_excerpt_lines", 2), 2, "card_excerpt_lines"
        ),
        card_title_lines=_int(flat.get("card_title_lines", 2), 2, "card_title_lines"),
        card_font_path=_str(flat.get("card_font_path")).strip(),
        card_bold_font_path=_str(flat.get("card_bold_font_path")).strip(),
    )
    return s, warnings
