"""Renders a labelled top-down preview of the Normandy map (tools/build/normandy_tiles.json), for checking the geography.

Run from the repository root:  python3 tools/preview_map.py [out.png]
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import normandy_geo as geo

COLORS = {"Grassland": (118, 160, 72), "Plains": (196, 182, 96), "Coast": (70, 120, 190)}
FEATURE_TINT = {
    "Forest": (40, 92, 40), "Hill": (150, 120, 70), "Ridge": (140, 150, 80), "Town": (150, 70, 55),
    "Orchard": (170, 200, 90), "Bocage": (70, 110, 50), "Beach": (232, 214, 160), "Bluffs": (160, 150, 110),
    "Cliffs": (120, 110, 100), "Flooded": (90, 150, 170),
}


def render(data, out, scale=18, labels=True):
    tiles = {(t["x"], t["y"]): t for t in data["tiles"]}
    pts = {h: geo.hex_to_world(*h) for h in tiles}
    minx = min(p[0] for p in pts.values()); maxx = max(p[0] for p in pts.values())
    miny = min(p[1] for p in pts.values()); maxy = max(p[1] for p in pts.values())
    W = int((maxx - minx + 2) * scale); H = int((maxy - miny + 2) * scale)
    img = Image.new("RGB", (W, H), (30, 30, 30))
    d = ImageDraw.Draw(img)

    def to_px(wx, wy):
        return (wx - minx + 1) * scale, (maxy - wy + 1) * scale

    def corners(h):
        cx, cy = to_px(*pts[h])
        r = scale * 1.0
        return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 360, 60)]

    for h, t in tiles.items():
        col = COLORS[t["base"]]
        for f in t["features"]:
            tint = FEATURE_TINT[f]
            k = 0.7 if f in ("Forest", "Town", "Beach", "Cliffs", "Flooded") else 0.45
            col = tuple(int(col[i] * (1 - k) + tint[i] * k) for i in range(3))
        if t["wonder"]:
            col = (230, 200, 60)
        d.polygon(corners(h), fill=col, outline=(60, 70, 50))
    for h, t in tiles.items():
        if not t["road"]:
            continue
        for n in geo.neighbors(h):
            if tiles.get(n, {}).get("road") and n > h:
                d.line([to_px(*pts[h]), to_px(*pts[n])], fill=(110, 75, 45), width=3)
    for x1, y1, x2, y2 in data["rivers"]:
        a, b = to_px(*pts[(x1, y1)]), to_px(*pts[(x2, y2)])
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        px, py = -dy / L * scale * 0.55, dx / L * scale * 0.55
        d.line([(mx - px, my - py), (mx + px, my + py)], fill=(40, 90, 220), width=3)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    if labels:
        city_tiles = {(c["x"], c["y"]) for c in data["cities"]}
        for h, t in tiles.items():
            if t["wonder"] and h not in city_tiles:
                cx, cy = to_px(*pts[h])
                d.text((cx + 6, cy - 6), t["wonder"], fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
        for c in data["cities"]:
            cx, cy = to_px(*pts[(c["x"], c["y"])])
            colr = (60, 90, 220) if c["civ"] == "Allies" else (200, 60, 60)
            d.rectangle([cx - 6, cy - 6, cx + 6, cy + 6], fill=colr, outline=(255, 255, 255))
            d.text((cx + 8, cy + 2), ("* " if c["objective"] else "") + c["name"], fill=(255, 255, 255), font=font,
                   stroke_width=2, stroke_fill=(0, 0, 0))
        for u in data.get("startUnits", []):
            cx, cy = to_px(*pts[(u["x"], u["y"])])
            colr = (40, 70, 230) if u["civ"] == "Allies" else (200, 40, 40)
            r = 3 if u["unit"].endswith("General") or u["unit"] == "Medics" else 5
            d.ellipse([cx - r, cy - r + 6, cx + r, cy + r + 6], fill=colr, outline=(255, 255, 255))
    img.save(out)
    return img


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    data = json.load(open(os.path.join(here, "build", "normandy_tiles.json")))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "build", "normandy_preview.png")
    render(data, out)
    print("wrote", out)
