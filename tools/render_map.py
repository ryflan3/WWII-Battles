"""Renders the Normandy map with the mod's own art (docs/normandy_map.png) and the mod-manager preview (preview.png).

Run from the repository root after tools/normandy_geo.py and tools/art/make_art.py:
    python3 tools/render_map.py
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "art"))
import normandy_geo as geo
from pixel import new, put, upscale
from tiles_art import tree, mound, inside, clip, tile

TILES = os.path.join(ROOT, "Images", "TileSets", "HexaRealm", "Tiles")
UNITS = os.path.join(ROOT, "Images", "TileSets", "WWII", "Units")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
ERA = "Second World War"


def base_hex(color, seed, waves=False):
    random.seed(seed)
    img = tile()
    for x in range(64):
        for y in range(56):
            if inside(x + 0.5, y + 0.5):
                k = random.random()
                c = color if k > 0.15 else tuple(max(0, v - 14) for v in color)
                if waves and k > 0.97:
                    c = tuple(min(255, v + 40) for v in color)
                put(img, x, y, c)
    for x in range(64):
        for y in range(56):
            if img.getpixel((x, y))[3] and (not inside(x + 2.5, y + 0.5) or not inside(x - 1.5, y + 0.5) or not inside(x + 0.5, y + 2.5)):
                put(img, x, y, tuple(max(0, v - 24) for v in color))
    return img


def forest_overlay(seed):
    random.seed(seed)
    img = tile()
    for _ in range(9):
        x, y = random.randint(12, 52), random.randint(10, 44)
        if inside(x, y):
            tree(img, x, y, 3, kind=random.choice(("leaf", "leaf", "pine")))
    return clip(img)


def hill_overlay():
    img = tile()
    mound(img, 32, 30, 26, 18)
    return clip(img)


def load(path):
    return Image.open(path).convert("RGBA")


def render(with_units=True, labels=True):
    data = json.load(open(os.path.join(HERE, "build", "normandy_tiles.json")))
    tiles = {(t["x"], t["y"]): t for t in data["tiles"]}
    pos = {}
    for h in tiles:
        wx, wy = geo.hex_to_world(*h)
        pos[h] = (wx * 32.0, -wy * 32.33)
    minx = min(p[0] for p in pos.values()) - 32; maxx = max(p[0] for p in pos.values()) + 32
    miny = min(p[1] for p in pos.values()) - 28; maxy = max(p[1] for p in pos.values()) + 28
    W, H = int(maxx - minx), int(maxy - miny)
    img = Image.new("RGBA", (W, H), (30, 30, 30, 255))
    bases = {"Grassland": [base_hex((104, 150, 66), s) for s in range(3)],
             "Plains": [base_hex((186, 172, 92), s + 10) for s in range(3)],
             "Coast": [base_hex((64, 112, 160), s + 20, waves=True) for s in range(3)]}
    forests = [forest_overlay(s) for s in range(4)]
    hill = hill_overlay()
    cache = {}

    def art(name):
        if name not in cache:
            p = os.path.join(TILES, name + ".png")
            cache[name] = load(p) if os.path.exists(p) else None
        return cache[name]

    city_at = {(c["x"], c["y"]): c for c in data["cities"]}
    order = sorted(tiles, key=lambda h: (pos[h][1], pos[h][0]))
    centers = {}
    for h in order:
        t = tiles[h]
        cx, cy = pos[h][0] - minx, pos[h][1] - miny
        centers[h] = (cx, cy)
        ox, oy = int(cx - 32), int(cy - 28)
        img.alpha_composite(bases[t["base"]][(h[0] * 7 + h[1] * 3) % 3], (ox, oy))
        layers = []
        for f in t["features"]:
            if f == "Hill":
                layers.append(hill)
            elif f == "Forest":
                layers.append(forests[(h[0] + h[1]) % 4])
            else:
                layers.append(art(f))
        if t["wonder"]:
            layers.append(art(t["wonder"]))
        for l in layers:
            if l is not None:
                img.alpha_composite(l, (ox, oy))
    d = ImageDraw.Draw(img)
    for h, t in tiles.items():
        if not t["road"]:
            continue
        for n in geo.neighbors(h):
            if n in tiles and tiles[n]["road"] and n > h:
                d.line([centers[h], centers[n]], fill=(120, 96, 66), width=5)
                d.line([centers[h], centers[n]], fill=(176, 150, 106), width=2)
    for x1, y1, x2, y2 in data["rivers"]:
        a, b = centers[(x1, y1)], centers[(x2, y2)]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        px, py = -dy / L * 19, dx / L * 19
        d.line([(mx - px, my - py), (mx + px, my + py)], fill=(64, 120, 200), width=5)
    for c in data["cities"]:
        h = (c["x"], c["y"])
        cx, cy = centers[h]
        if tiles[h]["base"] == "Coast":
            city = art("Coast+City center-%s-%s" % (c["civ"], ERA))
        else:
            city = art("City center-%s-%s" % (c["civ"], ERA)) or art("City center-%s" % ERA)
        if c["objective"]:   # a key position keeps its landmark: draw only a small flag over it
            continue
        img.alpha_composite(city, (int(cx - 32), int(cy - 28)))
    if with_units:
        for u in data["startUnits"]:
            cx, cy = centers[(u["x"], u["y"])]
            name = ("EmbarkedUnit-" + u["unit"]) if u["embarked"] else u["unit"]
            p = os.path.join(UNITS, name + ".png")
            if not os.path.exists(p):
                p = os.path.join(UNITS, "EmbarkedUnit-Military.png" if u["embarked"] else u["unit"] + ".png")
            sp = load(p)
            if u["unit"].endswith("General") or u["unit"] == "Medics":
                sp = sp.resize((40, 35), Image.NEAREST)
                img.alpha_composite(sp, (int(cx - 2), int(cy - 6)))
            else:
                img.alpha_composite(sp, (int(cx - 32), int(cy - 30)))
    if labels:
        font = ImageFont.truetype(FONT, 17)
        for h, t in tiles.items():
            if t["wonder"] and h not in city_at:
                cx, cy = centers[h]
                d.text((cx - 4, cy + 10), t["wonder"], fill=(255, 250, 230), font=font, stroke_width=3, stroke_fill=(20, 16, 12), anchor="mt")
        for c in data["cities"]:
            cx, cy = centers[(c["x"], c["y"])]
            col = {"Allies": (150, 190, 255), "Germany": (255, 160, 150)}.get(c["civ"], (235, 220, 170))
            name = ("★ " + c["name"]) if c.get("objective") else c["name"]
            if cx + 0.5 * font.getlength(name) > W:     # right edge
                cx = W - 0.5 * font.getlength(name) - 4
            if cy + 44 > H:     # bottom row: label above the city
                d.text((cx, cy - 24), name, fill=col, font=font, stroke_width=3, stroke_fill=(20, 16, 12), anchor="mb")
            else:
                d.text((cx, cy + 22), name, fill=col, font=font, stroke_width=3, stroke_fill=(20, 16, 12), anchor="mt")
    return img


def preview(map_img):
    W, H = 900, 500
    out = Image.new("RGBA", (W, H), (24, 26, 34, 255))
    m = map_img.copy()
    k = 1.25 * W / m.width
    m = m.resize((int(m.width * k), int(m.height * k)), Image.LANCZOS)
    left, top = min(int(m.width * 0.40), m.width - W), min(int(m.height * 0.12), m.height - H)   # the Gold-Sword sector
    out.alpha_composite(m.crop((left, top, left + W, top + H)))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    sd.rectangle([0, 0, W, 150], fill=(16, 18, 26, 205))
    sd.rectangle([0, H - 110, W, H], fill=(16, 18, 26, 190))
    out.alpha_composite(shade)
    d = ImageDraw.Draw(out)
    d.text((W // 2, 46), "WWII BATTLES", fill=(236, 230, 206), font=ImageFont.truetype(SERIF, 54), anchor="mm")
    d.text((W // 2, 106), "D-Day  -  the Normandy landings, June 6-8, 1944", fill=(206, 200, 170), font=ImageFont.truetype(SERIF, 26), anchor="mm")
    allies = ["US Infantry", "US Rangers", "Sherman", "British Paratroopers", "Commandos"]
    germans = ["German General", "Panther", "88 Flak", "Grenadiers", "Fallschirmjaeger"]
    for i, n in enumerate(allies):
        sp = upscale(load(os.path.join(UNITS, n + ".png")), 2)
        out.alpha_composite(sp, (10 + i * 82, H - 112))
    for i, n in enumerate(germans):
        sp = upscale(load(os.path.join(UNITS, n + ".png")), 2).transpose(Image.FLIP_LEFT_RIGHT)
        out.alpha_composite(sp, (W - 138 - i * 82, H - 112))
    return out.convert("RGB")


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    full = render()
    full.resize((full.width // 2, full.height // 2), Image.LANCZOS).convert("RGB").save(os.path.join(ROOT, "docs", "normandy_map.png"), optimize=True)
    preview(full).save(os.path.join(ROOT, "preview.png"), optimize=True)
    print("map", full.size, "-> docs/normandy_map.png (half size), preview.png")
