"""把 FANBOX 帖子画成和 FANBOX 网页帖子卡片一样的图片（Pillow 本地渲染，不用外部服务）。

尺寸和颜色按 FANBOX 网页在 2 倍屏下的帖子卡片量出来：宽 1430 像素，
封面 1200:630，下面是头像、名字、日期、档位标签、标题、摘要和点赞数。
"""

from __future__ import annotations

import io
import os
from dataclasses import dataclass
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

try:
    from .fanbox_core import Post, clean_excerpt, format_card_time
except ImportError:  # 测试时作为顶层模块导入
    from fanbox_core import Post, clean_excerpt, format_card_time

# ---------- 尺寸（像素，2 倍屏） ----------
CANVAS_W = 1430
MARGIN_X = 22
MARGIN_TOP = 14
MARGIN_BOTTOM = 24
CARD_RADIUS = 16
PAD = 80
COVER_RATIO = 630 / 1200

AVATAR = 64
AVATAR_TOP = 37  # 封面底部到头像顶部
NAME_TOP = 40  # 封面底部到名字字形顶部
DATE_TOP = 80
BADGE_TOP = 49
BADGE_H = 42
BADGE_PAD_X = 16
BADGE_GAP = 12
TITLE_TOP = 147
TITLE_PITCH = 56
TITLE_TO_EXCERPT = 69  # 标题最后一行字形顶部到摘要第一行字形顶部
EXCERPT_PITCH = 45
CONTENT_TO_PILL = 37
PILL_H = 47
PILL_PAD_X = 22
PILL_GAP = 10
BOTTOM_PAD_WITH_PILL = 48
BOTTOM_PAD_NO_PILL = 64

SIZE_NAME = 28
SIZE_DATE = 24
SIZE_BADGE = 23
SIZE_TITLE = 40
SIZE_EXCERPT = 28
SIZE_LIKE = 26
SIZE_HEART = 30

# ---------- 颜色 ----------
PAGE_BG = (243, 245, 249)
CARD_BG = (255, 255, 255)
TEXT_MAIN = (38, 38, 38)
TEXT_SUB = (97, 97, 97)
BADGE_BG = (246, 246, 246)
ADULT_BG = (230, 60, 80)
PILL_BORDER = (153, 153, 153)
PILL_TEXT = (149, 149, 149)
PLACEHOLDER_BG = (233, 234, 238)
PLACEHOLDER_TEXT = (140, 140, 150)

SS = 4  # 圆角、圆形蒙版的超采样倍数

CJK_REGULAR = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
]
CJK_BOLD = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf",
]
FALLBACK_REGULAR = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
FALLBACK_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


class CardRenderError(Exception):
    pass


@dataclass
class CardOptions:
    show_fee: bool = True
    show_timezone: bool = True
    show_adult_mark: bool = True
    show_likes: bool = True
    excerpt_lines: int = 2
    title_lines: int = 2
    offset_hours: int = 8
    hide_cover: bool = False  # R-18 且不允许发封面时为 True
    font_path: str = ""
    bold_font_path: str = ""
    jpeg_quality: int = 92


# ---------- 字体 ----------


def _first_existing(paths: list[str]) -> str | None:
    for p in paths:
        if p and os.path.isfile(p):
            return p
    return None


@lru_cache(maxsize=64)
def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    """加载字体；.ttc 里优先选日文字形（Noto Sans CJK JP）。"""
    if path.lower().endswith(".ttc"):
        for idx in range(16):
            try:
                font = ImageFont.truetype(path, size, index=idx)
            except OSError:
                break
            family = font.getname()[0] or ""
            if family.endswith("JP") and "Mono" not in family:
                return font
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=64)
def _notdef_signature(path: str, size: int) -> tuple:
    mask = _load_font(path, size).getmask("￿")
    return mask.size, bytes(mask)


@lru_cache(maxsize=8192)
def _has_glyph(path: str, size: int, ch: str) -> bool:
    if ch.isspace():
        return True
    mask = _load_font(path, size).getmask(ch)
    if mask.size[0] == 0 or mask.size[1] == 0:
        return False
    return (mask.size, bytes(mask)) != _notdef_signature(path, size)


class FontSet:
    """主字体 + 后备字体。两者都没有的字（比如彩色 emoji）会被省略。"""

    def __init__(self, primary: str, fallbacks: list[str], size: int):
        self.paths = [primary] + [p for p in fallbacks if p and os.path.isfile(p)]
        self.size = size
        self.primary = _load_font(primary, size)

    def font_for(self, ch: str) -> ImageFont.FreeTypeFont | None:
        for path in self.paths:
            if _has_glyph(path, self.size, ch):
                return _load_font(path, self.size)
        return None

    def ink_top_offset(self) -> int:
        """以"国"字为准，字形顶部相对基线的偏移（负数）。"""
        return self.primary.getbbox("国", anchor="ls")[1]


@dataclass
class Fonts:
    name: FontSet
    date: FontSet
    badge: FontSet
    title: FontSet
    excerpt: FontSet
    like: FontSet
    heart: FontSet


def _fonts(opts: CardOptions) -> Fonts:
    regular = (
        opts.font_path
        if opts.font_path and os.path.isfile(opts.font_path)
        else _first_existing(CJK_REGULAR)
    )
    bold = (
        opts.bold_font_path
        if opts.bold_font_path and os.path.isfile(opts.bold_font_path)
        else _first_existing(CJK_BOLD)
    ) or regular
    if not regular:
        raise CardRenderError("找不到中日文字体（Noto Sans CJK），无法渲染卡片")
    fb_r = [p for p in FALLBACK_REGULAR if os.path.isfile(p)]
    fb_b = [p for p in FALLBACK_BOLD if os.path.isfile(p)] or fb_r
    return Fonts(
        name=FontSet(bold, fb_b, SIZE_NAME),
        date=FontSet(regular, fb_r, SIZE_DATE),
        badge=FontSet(regular, fb_r, SIZE_BADGE),
        title=FontSet(bold, fb_b, SIZE_TITLE),
        excerpt=FontSet(regular, fb_r, SIZE_EXCERPT),
        like=FontSet(regular, fb_r, SIZE_LIKE),
        heart=FontSet((fb_r or [regular])[0], [regular], SIZE_HEART),
    )


# ---------- 文字排版 ----------

Glyph = tuple[str, ImageFont.FreeTypeFont, float]


def _glyphs(text: str, fs: FontSet) -> list[Glyph]:
    out: list[Glyph] = []
    for ch in text:
        if ch in "‍︎️":
            continue
        font = fs.font_for(ch)
        if font is None:
            continue
        out.append((ch, font, font.getlength(ch)))
    return out


def _width(glyphs: list[Glyph]) -> float:
    return sum(g[2] for g in glyphs)


def _is_word_char(ch: str) -> bool:
    return ch.isascii() and (ch.isalnum() or ch in "'-_.")


def wrap(text: str, fs: FontSet, max_width: float, max_lines: int) -> list[list[Glyph]]:
    """按宽度折行，最多 max_lines 行，超出时最后一行末尾加"…"。"""
    if max_lines <= 0:
        return []
    paragraphs = [p for p in text.split("\n")]
    lines: list[list[Glyph]] = []
    truncated = False
    for para in paragraphs:
        glyphs = _glyphs(para, fs)
        while glyphs:
            if len(lines) == max_lines:
                truncated = True
                break
            used = 0.0
            cut = 0
            for i, g in enumerate(glyphs):
                if used + g[2] > max_width and i > 0:
                    break
                used += g[2]
                cut = i + 1
            if cut < len(glyphs) and _is_word_char(glyphs[cut][0]):
                # 英文单词不从中间断开：退到这一行最后一个空格
                for j in range(cut - 1, max(0, cut - 24), -1):
                    if glyphs[j][0] == " ":
                        cut = j + 1
                        break
            line = glyphs[:cut]
            while line and line[-1][0] == " ":
                line = line[:-1]
            lines.append(line)
            glyphs = glyphs[cut:]
            while glyphs and glyphs[0][0] == " ":
                glyphs = glyphs[1:]
        if truncated:
            break
        if len(lines) == max_lines and para is not paragraphs[-1]:
            truncated = True
            break
    lines = [ln for ln in lines if ln] or []
    if truncated and lines:
        ell = _glyphs("…", fs)
        last = lines[-1]
        while last and _width(last) + _width(ell) > max_width:
            last = last[:-1]
        lines[-1] = last + ell
    return lines


def _draw_line(
    draw: ImageDraw.ImageDraw, x: float, baseline: float, line: list[Glyph], fill
):
    # 相邻同字体的字合成一段画，保留字距调整
    run = ""
    run_font = None
    run_x = x
    for ch, font, w in line:
        if font is not run_font and run:
            draw.text((run_x, baseline), run, font=run_font, fill=fill, anchor="ls")
            run_x += run_font.getlength(run)
            run = ""
        run_font = font
        run += ch
    if run:
        draw.text((run_x, baseline), run, font=run_font, fill=fill, anchor="ls")


def _text_width(text: str, fs: FontSet) -> float:
    return _width(_glyphs(text, fs))


# ---------- 图形 ----------


def _rounded_mask(
    size: tuple[int, int], radius: int, corners=(True, True, True, True)
) -> Image.Image:
    w, h = size
    big = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        (0, 0, w * SS - 1, h * SS - 1), radius=radius * SS, fill=255, corners=corners
    )
    return big.resize((w, h), Image.LANCZOS)


def _paste_rounded(
    base: Image.Image, box: tuple[int, int, int, int], fill, radius: int
):
    x0, y0, x1, y1 = box
    layer = Image.new("RGB", (x1 - x0, y1 - y0), fill)
    base.paste(layer, (x0, y0), _rounded_mask(layer.size, radius))


def _pill_outline(base: Image.Image, box, color, width: int):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    big = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(big)
    r = h * SS // 2
    d.rounded_rectangle((0, 0, w * SS - 1, h * SS - 1), radius=r, fill=255)
    d.rounded_rectangle(
        (width * SS, width * SS, w * SS - 1 - width * SS, h * SS - 1 - width * SS),
        radius=r - width * SS,
        fill=0,
    )
    mask = big.resize((w, h), Image.LANCZOS)
    base.paste(Image.new("RGB", (w, h), color), (x0, y0), mask)


def _cover_fit(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    """等比缩放后居中裁切，铺满 size。"""
    tw, th = size
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = max(tw, round(sw * scale)), max(th, round(sh * scale))
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def _open_image(data: bytes | None) -> Image.Image | None:
    if not data:
        return None
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception:
        return None
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, CARD_BG)
        bg.paste(img, mask=img.split()[-1])
        return bg
    return img.convert("RGB")


# ---------- 主函数 ----------


def render_card(
    post: Post,
    creator_name: str,
    cover: bytes | None,
    avatar: bytes | None,
    opts: CardOptions | None = None,
) -> bytes:
    """返回 JPEG 字节。"""
    opts = opts or CardOptions()
    fonts = _fonts(opts)

    card_x0, card_x1 = MARGIN_X, CANVAS_W - MARGIN_X
    card_w = card_x1 - card_x0
    cover_h = round(card_w * COVER_RATIO)
    inner_x0, inner_x1 = card_x0 + PAD, card_x1 - PAD
    inner_w = inner_x1 - inner_x0

    # 先排版，算出卡片高度
    title_lines = wrap(
        post.title or "（无标题）", fonts.title, inner_w, max(1, opts.title_lines)
    )
    # 网页上摘要的换行会显示成空格，连成一段
    excerpt = " ".join(clean_excerpt(post.excerpt, 10_000).split("\n"))
    excerpt_lines = (
        wrap(excerpt, fonts.excerpt, inner_w, opts.excerpt_lines) if excerpt else []
    )

    cb = MARGIN_TOP + cover_h  # 封面底部
    title_top = cb + TITLE_TOP
    last_title_top = title_top + TITLE_PITCH * (len(title_lines) - 1)
    content_bottom = last_title_top + SIZE_TITLE - 2
    excerpt_top = last_title_top + TITLE_TO_EXCERPT
    if excerpt_lines:
        content_bottom = (
            excerpt_top + EXCERPT_PITCH * (len(excerpt_lines) - 1) + SIZE_EXCERPT + 5
        )
    show_pill = opts.show_likes
    if show_pill:
        pill_top = content_bottom + CONTENT_TO_PILL
        card_bottom = pill_top + PILL_H + BOTTOM_PAD_WITH_PILL
    else:
        card_bottom = content_bottom + BOTTOM_PAD_NO_PILL
    canvas_h = card_bottom + MARGIN_BOTTOM

    canvas = Image.new("RGB", (CANVAS_W, canvas_h), PAGE_BG)
    card = Image.new("RGB", (card_w, card_bottom - MARGIN_TOP), CARD_BG)

    # 封面
    cover_img = None if opts.hide_cover else _open_image(cover)
    if cover_img is not None:
        card.paste(_cover_fit(cover_img, (card_w, cover_h)), (0, 0))
    else:
        ImageDraw.Draw(card).rectangle((0, 0, card_w, cover_h), fill=PLACEHOLDER_BG)
        label = "R-18 · 封面已隐藏" if opts.hide_cover else "FANBOX"
        ph = FontSet(fonts.title.paths[0], fonts.title.paths[1:], 44)
        lw = _text_width(label, ph)
        _draw_line(
            ImageDraw.Draw(card),
            (card_w - lw) / 2,
            cover_h / 2 + 16,
            _glyphs(label, ph),
            PLACEHOLDER_TEXT,
        )
    canvas.paste(card, (card_x0, MARGIN_TOP), _rounded_mask(card.size, CARD_RADIUS))
    draw = ImageDraw.Draw(canvas)

    # 头像
    av = _open_image(avatar)
    av_box = (inner_x0, cb + AVATAR_TOP)
    if av is not None:
        av = _cover_fit(av, (AVATAR, AVATAR))
        circle = Image.new("L", (AVATAR * SS, AVATAR * SS), 0)
        ImageDraw.Draw(circle).ellipse(
            (0, 0, AVATAR * SS - 1, AVATAR * SS - 1), fill=255
        )
        canvas.paste(av, av_box, circle.resize((AVATAR, AVATAR), Image.LANCZOS))
    else:
        draw.ellipse(
            (av_box[0], av_box[1], av_box[0] + AVATAR, av_box[1] + AVATAR),
            fill=PLACEHOLDER_BG,
        )

    # 右上角标签：R-18、档位
    badges: list[tuple[str, tuple, tuple]] = []
    if opts.show_adult_mark and post.adult:
        badges.append(("R-18", ADULT_BG, (255, 255, 255)))
    if opts.show_fee:
        badges.append(
            ("免费" if post.fee <= 0 else f"{post.fee}日元", BADGE_BG, TEXT_SUB)
        )
    bx1 = inner_x1
    badge_top = cb + BADGE_TOP
    badge_left_limit = inner_x1
    for text, bg, fg in reversed(badges):
        tw = _text_width(text, fonts.badge)
        bw = round(tw + BADGE_PAD_X * 2)
        bx0 = bx1 - bw
        _paste_rounded(canvas, (bx0, badge_top, bx1, badge_top + BADGE_H), bg, 8)
        base = badge_top + 10 - fonts.badge.ink_top_offset()
        _draw_line(draw, bx0 + BADGE_PAD_X, base, _glyphs(text, fonts.badge), fg)
        badge_left_limit = bx0
        bx1 = bx0 - BADGE_GAP

    # 名字、日期
    text_x = inner_x0 + AVATAR + 16
    name_max = badge_left_limit - 24 - text_x
    name_line = wrap(
        creator_name or post.creator_name or post.creator_id, fonts.name, name_max, 1
    )
    if name_line:
        _draw_line(
            draw,
            text_x,
            cb + NAME_TOP - fonts.name.ink_top_offset(),
            name_line[0],
            TEXT_MAIN,
        )
    when = format_card_time(post.published, opts.offset_hours, opts.show_timezone)
    if when:
        date_line = wrap(when, fonts.date, name_max, 1)
        if date_line:
            _draw_line(
                draw,
                text_x,
                cb + DATE_TOP - fonts.date.ink_top_offset(),
                date_line[0],
                TEXT_SUB,
            )

    # 标题、摘要
    for i, line in enumerate(title_lines):
        top = title_top + TITLE_PITCH * i
        _draw_line(draw, inner_x0, top - fonts.title.ink_top_offset(), line, TEXT_MAIN)
    for i, line in enumerate(excerpt_lines):
        top = excerpt_top + EXCERPT_PITCH * i
        _draw_line(draw, inner_x0, top - fonts.excerpt.ink_top_offset(), line, TEXT_SUB)

    # 点赞数
    if show_pill:
        num = str(max(0, post.like_count))
        heart = _glyphs("♥", fonts.heart)
        hw = _width(heart)
        nw = _text_width(num, fonts.like)
        pw = round(PILL_PAD_X * 2 + hw + PILL_GAP + nw)
        px1 = inner_x1
        px0 = px1 - pw
        _pill_outline(canvas, (px0, pill_top, px1, pill_top + PILL_H), PILL_BORDER, 2)
        mid = pill_top + PILL_H / 2
        if heart:
            hb = fonts.heart.primary.getbbox("♥", anchor="ls")
            _draw_line(
                draw, px0 + PILL_PAD_X, mid - (hb[1] + hb[3]) / 2, heart, PILL_TEXT
            )
        nb = fonts.like.primary.getbbox("0", anchor="ls")
        _draw_line(
            draw,
            px0 + PILL_PAD_X + hw + PILL_GAP,
            mid - (nb[1] + nb[3]) / 2,
            _glyphs(num, fonts.like),
            PILL_TEXT,
        )

    out = io.BytesIO()
    canvas.save(out, "JPEG", quality=opts.jpeg_quality, subsampling=0, optimize=True)
    return out.getvalue()
