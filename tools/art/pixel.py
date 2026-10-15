"""Tiny pixel-art toolkit used to draw every graphic in the mod.

All drawing happens on PIL RGBA images at 1 pixel = 1 pixel; nothing is copied from Unciv.
"""
from PIL import Image, ImageDraw, ImageFilter
import math, random

T = (0, 0, 0, 0)


def rgba(c, a=255):
    if len(c) == 4:
        return tuple(c)
    return (c[0], c[1], c[2], a)


def shade(c, f):
    """Darken (f<1) or lighten (f>1) a colour."""
    r, g, b = c[:3]
    if f < 1:
        return (int(r * f), int(g * f), int(b * f))
    return (min(255, int(r + (255 - r) * (f - 1))), min(255, int(g + (255 - g) * (f - 1))), min(255, int(b + (255 - b) * (f - 1))))


def new(w, h):
    return Image.new("RGBA", (w, h), T)


def put(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height and c is not None:
        img.putpixel((int(x), int(y)), rgba(c))


def rect(img, x, y, w, h, c):
    for i in range(int(w)):
        for j in range(int(h)):
            put(img, x + i, y + j, c)


def line(img, x0, y0, x1, y1, c):
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        put(img, x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy


def disc(img, cx, cy, r, c):
    for x in range(int(cx - r - 1), int(cx + r + 2)):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 0.3:
                put(img, x, y, c)


def ellipse(img, cx, cy, rx, ry, c):
    for x in range(int(cx - rx - 1), int(cx + rx + 2)):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            if ((x - cx) / max(rx, 0.1)) ** 2 + ((y - cy) / max(ry, 0.1)) ** 2 <= 1.0:
                put(img, x, y, c)


def ring(img, cx, cy, r, c):
    for a in range(0, 360, 6):
        put(img, round(cx + r * math.cos(math.radians(a))), round(cy + r * math.sin(math.radians(a))), c)


def template(img, x, y, rows, pal, flip=False):
    """Stamp an ASCII template. '.' is transparent; other characters are looked up in pal."""
    w = max(len(r) for r in rows)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.' or ch == ' ':
                continue
            c = pal.get(ch)
            if c is None:
                continue
            xx = x + (w - 1 - i if flip else i)
            put(img, xx, y + j, c)


def outline(img, color=(24, 20, 18), alpha_threshold=40):
    """Adds a 1-pixel dark outline around opaque pixels (AbsoluteUnits-style readability)."""
    src = img.copy()
    px = src.load()
    out = img.load()
    for x in range(img.width):
        for y in range(img.height):
            if px[x, y][3] > alpha_threshold:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < img.width and 0 <= ny < img.height and px[nx, ny][3] > alpha_threshold:
                    out[x, y] = rgba(color, 230)
                    break
    return img


def shadow(img, cx, cy, rx, ry, alpha=70):
    """Soft ground shadow drawn *under* existing pixels."""
    sh = new(img.width, img.height)
    ellipse(sh, cx, cy, rx, ry, (0, 0, 0, alpha))
    sh.alpha_composite(img)
    return sh


def silhouette(img, color=(255, 255, 255)):
    a = img.split()[3]
    out = Image.new("RGBA", img.size, rgba(color))
    out.putalpha(a.point(lambda v: 255 if v > 40 else 0))
    return out


def upscale(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def fit_center(img, size, pad=0):
    """Crop to content and centre inside a size x size transparent square (keeps pixel crispness)."""
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    w, h = img.size
    k = max(1, min((size - 2 * pad) // max(w, 1), (size - 2 * pad) // max(h, 1)))
    img = upscale(img, k)
    out = new(size, size)
    out.alpha_composite(img, ((size - img.width) // 2, (size - img.height) // 2))
    return out


def smooth_icon(img, size=100, pad=6):
    """Like fit_center but scales smoothly - used for white UI icons."""
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    w, h = img.size
    k = min((size - 2 * pad) / w, (size - 2 * pad) / h)
    img = img.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
    out = new(size, size)
    out.alpha_composite(img, ((size - img.width) // 2, (size - img.height) // 2))
    return out
