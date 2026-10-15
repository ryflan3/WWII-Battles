"""Tile overlays (64x56, drawn over Grassland/Plains) for the HexaRealm tileset; FantasyHex gets 32x28 downscales.
Landmarks (natural wonders) and city centers, including the Allied fleets at anchor (a city on a Coast tile)."""
import random
from figures import *

TW, TH = 64, 56
HEX = [(16, 1), (48, 1), (63, 29), (49, 55), (15, 55), (1, 29)]

GRASS_HI, GRASS, GRASS_D = (134, 174, 86), (108, 148, 70), (78, 112, 52)
HEDGE, HEDGE_D, HEDGE_HI = (52, 92, 40), (34, 66, 28), (78, 122, 56)
LEAF, LEAF_HI, LEAF_D = (52, 104, 46), (78, 136, 60), (34, 74, 34)
ROCK, ROCK_HI, ROCK_D = (132, 130, 124), (172, 170, 162), (88, 86, 82)
CHALK, CHALK_D, CHALK_HI = (204, 198, 180), (160, 154, 136), (228, 224, 210)
STONE, STONE_D = (196, 186, 160), (150, 140, 118)          # Caen stone
SLATE, SLATE_D = (86, 90, 100), (60, 64, 72)
ROOF, ROOF_D = (150, 80, 60), (112, 58, 44)
DIRT, DIRT_D = (128, 98, 64), (92, 70, 46)
SAND, SAND_D, SAND_HI = (226, 208, 156), (196, 176, 124), (240, 228, 188)
WATER, WATER_D, WATER_HI = (70, 120, 170), (52, 94, 140), (130, 176, 210)
CONCRETE, CONCRETE_D, CONCRETE_HI = (160, 156, 146), (116, 112, 104), (188, 184, 174)


def tile():
    return new(TW, TH)


def inside(x, y):
    poly = HEX
    inside_ = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside_ = not inside_
        j = i
    return inside_


def clip(img):
    px = img.load()
    for x in range(TW):
        for y in range(TH):
            if px[x, y][3] and not inside(x + 0.5, y + 0.5):
                px[x, y] = (0, 0, 0, 0)
    return img


def fill_hex(img, color, alpha=255, noise_colors=None, density=0.0, seed=0):
    rnd = random.Random(seed)
    for x in range(TW):
        for y in range(TH):
            if inside(x + 0.5, y + 0.5):
                c = color
                if noise_colors and rnd.random() < density:
                    c = rnd.choice(noise_colors)
                put(img, x, y, (*c, alpha))


def mound(img, cx, cy, rx, ry, base=GRASS, rocky=False):
    for x in range(int(cx - rx - 1), int(cx + rx + 2)):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            dd = dx * dx + dy * dy
            if dd > 1:
                continue
            light = -dx * 0.5 - dy * 0.8
            c = base
            if light > 0.45:
                c = shade(base, 1.18)
            elif light < -0.45:
                c = shade(base, 0.8)
            if rocky and random.random() < 0.10:
                c = ROCK if light > 0 else ROCK_D
            alpha = 255 if dd < 0.6 else int(255 * (1 - dd) / 0.4)
            put(img, x, y, (*c, max(alpha, 40)))


def tree(img, x, y, r=3, kind="leaf", fruit=None):
    if kind == "pine":
        for i in range(r + 2):
            rect(img, x - i // 2, y - (r + 2) + i, (i // 2) * 2 + 1, 1, (40, 86, 50) if i % 2 else (26, 60, 36))
        put(img, x, y + 1, WOOD_D)
        return
    disc(img, x, y + r + 1, r, (0, 0, 0, 60))
    put(img, x, y + r, WOOD_D); put(img, x, y + r + 1, WOOD_D)
    disc(img, x, y, r, LEAF_D)
    disc(img, x - 0.5, y - 0.5, r - 0.8, LEAF)
    put(img, x - 1, y - 1, LEAF_HI)
    if fruit:
        put(img, x + 1, y, fruit); put(img, x - 1, y + 1, fruit)


def rock(img, x, y, r):
    ellipse(img, x + 1, y + 1, r + 0.5, r * 0.7 + 0.5, (0, 0, 0, 70))
    ellipse(img, x, y, r, r * 0.75, ROCK_D)
    ellipse(img, x - 0.5, y - 0.5, r - 0.6, r * 0.75 - 0.6, ROCK)
    put(img, x - r // 2, y - r // 2, ROCK_HI)


def house(img, x, y, w=6, h=4, wall=STONE, roof=SLATE, windows=True):
    """(x, y) = bottom-left corner: a Norman stone house with a steep roof."""
    rect(img, x + 1, y + 1, w, 1, (0, 0, 0, 70))
    rect(img, x, y - h, w, h, wall)
    rect(img, x + w - 1, y - h, 1, h, shade(wall, 0.8))
    for i in range(3):
        rect(img, x - 1 + i, y - h - 1 - i, w + 2 - 2 * i, 1, roof if i % 2 == 0 else shade(roof, 0.75))
    if windows:
        for wx in range(x + 1, x + w - 1, 2):
            put(img, wx, y - h + 1, (60, 60, 70))
    put(img, x + w // 2, y - 1, (70, 50, 40))


def ruin(img, x, y, w=6, h=4):
    """A shelled house: broken walls and rubble."""
    rect(img, x, y - h, 2, h, STONE)
    rect(img, x + w - 2, y - h + 2, 2, h - 2, STONE_D)
    for i in range(w):
        put(img, x + i, y, (110, 104, 92)); put(img, x + i, y - 1, (140, 132, 116) if i % 2 else (90, 84, 74))


def church(img, x, y, spire=12, wall=STONE):
    rect(img, x, y - 7, 12, 7, wall)
    rect(img, x + 11, y - 7, 1, 7, shade(wall, 0.8))
    for i in range(3):
        rect(img, x - 1 + i, y - 8 - i, 14 - 2 * i, 1, SLATE if i % 2 == 0 else SLATE_D)
    rect(img, x + 1, y - 12, 4, 5, wall)                           # tower
    for i in range(spire - 4):
        w = max(1, 4 - i // 2)
        rect(img, x + 3 - w // 2, y - 12 - i, w, 1, SLATE_D if i % 2 else SLATE)
    put(img, x + 3, y - 9 - spire + 1, (220, 200, 90))
    rect(img, x + 6, y - 5, 2, 3, (60, 50, 50))


def hedgerow(img, x0, y0, x1, y1, seed=0):
    rnd = random.Random(seed)
    n = max(abs(x1 - x0), abs(y1 - y0))
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / max(n, 1)
        y = y0 + (y1 - y0) * k / max(n, 1)
        put(img, x, y + 1, (0, 0, 0, 60))
        put(img, x, y, HEDGE_D)
        put(img, x, y - 1, HEDGE if rnd.random() < 0.7 else HEDGE_HI)
        if rnd.random() < 0.25:                                      # hedgerow trees
            disc(img, x, y - 2, 1.6, HEDGE)
            put(img, x - 1, y - 3, HEDGE_HI)


def fence(img, x0, y0, x1, y1):
    line(img, x0, y0, x1, y1, (150, 120, 80))


def crater(img, x, y, r=2):
    ellipse(img, x, y, r + 1, r * 0.7 + 0.5, (96, 80, 58))
    ellipse(img, x, y, r, r * 0.6, (66, 54, 40))


def small_casemate(img, x, y, w=10):
    for j in range(5):
        rect(img, x + j // 2, y - j, w - j, 1, CONCRETE if j < 4 else CONCRETE_HI)
    rect(img, x + w - 4, y - 3, 3, 2, (30, 30, 30))
    rect(img, x + w - 1, y - 3, 4, 1, GUNMETAL)


def hedgehogs(img, spots):
    for x, y in spots:
        hedgehog(img, x, y, 2, (70, 64, 58))


def water_strip(img, side="top", depth=12, seed=0):
    """Paint the sea along one edge of the hex (for coastal landmarks)."""
    rnd = random.Random(seed)
    for x in range(TW):
        for y in range(TH):
            yy = y if side == "top" else TH - 1 - y
            edge = depth + 2 * math.sin(x / 6.0 + seed)
            if yy < edge and inside(x + 0.5, y + 0.5):
                c = WATER if rnd.random() > 0.08 else WATER_HI
                if yy > edge - 2:
                    c = (220, 230, 236)                               # surf line
                put(img, x, y, c)


# ------------------------------------------------------------------ features

def f_ridge():
    random.seed(1)
    img = tile()
    for x in range(4, 60):
        for y in range(14, 44):
            dx, dy = (x - 32) / 28, (y - 30) / 11
            if dx * dx + dy * dy > 1:
                continue
            if dy < -0.15:
                put(img, x, y, (*GRASS_HI, 110))
            elif dy > 0.35:
                put(img, x, y, (*GRASS_D, 120))
    return clip(img)


def f_bocage():
    img = tile()
    # a patchwork of small fields, each walled by a hedgerow on an earth bank
    for y in (12, 26, 40):
        hedgerow(img, 2, y, 62, y + 3, seed=y)
    for x, y0, y1 in ((14, 12, 26), (36, 13, 27), (52, 13, 27), (24, 27, 41), (46, 28, 42), (12, 41, 54), (36, 42, 54)):
        hedgerow(img, x, y0, x + 1, y1, seed=x)
    for x, y in ((24, 18), (44, 34), (8, 33)):
        rect(img, x, y, 2, 1, (*GRASS_HI, 160))
    return clip(img)


def f_orchard():
    img = tile()
    for row in range(3):
        for col in range(4):
            x = 14 + col * 11 + (5 if row % 2 else 0)
            y = 14 + row * 12
            if inside(x, y) and x < 56:
                tree(img, x, y, 3, fruit=(200, 40, 40))
    return clip(img)


def f_town(square=False):
    img = tile()
    rect(img, 6, 29, 52, 2, (*DIRT, 200))
    rect(img, 30, 6, 2, 46, (*DIRT, 200))
    spots = [(9, 26), (19, 25), (36, 26), (46, 25), (12, 45), (22, 46), (36, 46), (45, 45), (20, 14), (38, 14)]
    for i, (x, y) in enumerate(spots):
        if i in (2, 6):
            ruin(img, x, y, 7, 5)
        else:
            house(img, x, y, 7, 5, wall=STONE if i % 2 else (210, 200, 176))
    church(img, 44, 19, 10)
    return clip(img)


def f_beach():
    img = tile()
    fill_hex(img, SAND, 210, [SAND_D, SAND_HI], 0.25, seed=3)
    for x in range(4, 60, 3):                                          # dune grass along the top
        put(img, x, 8 + (x % 5 == 0), (120, 140, 80)); put(img, x + 1, 7, (100, 124, 66))
    hedgehogs(img, [(14, 40), (26, 46), (40, 41), (52, 47), (32, 34)])
    for x in range(8, 58, 6):                                          # stakes
        put(img, x, 50, WOOD_D); put(img, x, 49, WOOD_D)
    return clip(img)


def f_bluffs():
    img = tile()
    fill_hex(img, SAND, 230, [SAND_D], 0.2, seed=5)
    for x in range(TW):                                                # the bluff rising behind the beach
        top = 6 + int(3 * math.sin(x / 5.0))
        for y in range(top, 34 - int(4 * math.sin(x / 9.0))):
            if inside(x + 0.5, y + 0.5):
                put(img, x, y, GRASS if (x + y) % 7 else GRASS_D if y > 20 else GRASS_HI)
    for x in range(4, 60, 2):
        put(img, x, 33 - int(4 * math.sin(x / 9.0)), (150, 136, 90))
    hedgehogs(img, [(16, 46), (34, 50), (48, 45)])
    small_casemate(img, 36, 22)
    return clip(img)


def f_cliffs():
    img = tile()
    for x in range(TW):
        edge = 34 + int(3 * math.sin(x / 4.0))
        for y in range(TH):
            if not inside(x + 0.5, y + 0.5):
                continue
            if y < 10:
                put(img, x, y, GRASS)
            elif y < edge:
                c = CHALK if (x * 7 + y * 3) % 13 else CHALK_D
                if y < 12:
                    c = CHALK_HI
                put(img, x, y, c)
            else:
                put(img, x, y, (*ROCK_D, 230) if (x + y) % 5 else (*ROCK, 230))
    for x, y in ((10, 46), (30, 50), (48, 44)):
        rock(img, x, y, 3)
    return clip(img)


def f_flooded():
    img = tile()
    rnd = random.Random(9)
    for cx, cy, rx, ry in ((18, 20, 12, 6), (42, 30, 14, 7), (22, 42, 11, 6), (48, 46, 8, 4)):
        ellipse(img, cx, cy, rx, ry, WATER)
        ellipse(img, cx - 2, cy - 1, rx - 3, ry - 2, (*WATER_HI, 200))
    for _ in range(40):                                                 # reeds
        x, y = rnd.randint(4, 60), rnd.randint(6, 52)
        if inside(x, y):
            put(img, x, y, (96, 120, 60)); put(img, x, y - 1, (120, 144, 72))
    return clip(img)


def f_foxholes():
    img = tile()
    for x, y in ((16, 24), (30, 30), (44, 24), (22, 40), (38, 42)):
        ellipse(img, x, y, 4, 2, DIRT_D)
        ellipse(img, x, y - 1, 3, 1.4, (50, 40, 30))
        rect(img, x - 4, y + 1, 8, 1, DIRT)
    return clip(img)


# ------------------------------------------------------------------ landmarks (natural wonders)

def nw_utah():
    img = tile()
    water_strip(img, "top", 10, seed=1)
    for x in range(TW):
        for y in range(11, 30):
            if inside(x + 0.5, y + 0.5):
                put(img, x, y, SAND if (x + y) % 6 else SAND_D)
    for x in range(2, 62, 2):                                         # the dune line
        put(img, x, 30, (130, 146, 84)); put(img, x + 1, 31, (110, 128, 70))
    hedgehogs(img, [(12, 20), (28, 24), (46, 21)])
    small_casemate(img, 22, 40, 14)
    rect(img, 34, 36, 2, 10, (*DIRT, 220))                              # the causeway (Exit 2) inland
    fill = [(40, 44, 12, 4), (16, 48, 8, 3)]
    for cx, cy, rx, ry in fill:
        ellipse(img, cx, cy, rx, ry, (*WATER, 220))
    return clip(img)


def nw_sme():
    img = tile()
    for x, y in ((8, 30), (16, 46), (46, 46), (50, 30), (10, 44)):
        house(img, x, y, 7, 5, wall=STONE)
    rect(img, 20, 34, 24, 10, (*DIRT, 180))                              # the square
    church(img, 26, 34, 14)
    parachute(img, 29, 10, 5, (230, 226, 210), (190, 184, 166))         # Private Steele's parachute on the steeple
    soldier(img, 28, 14, US_PARA, STAND, "m1net")
    return clip(img)


def nw_carentan():
    img = tile()
    for cx, cy, rx, ry in ((14, 16, 12, 6), (50, 44, 10, 6)):
        ellipse(img, cx, cy, rx, ry, (*WATER, 230))
    rect(img, 0, 30, 64, 2, (*DIRT, 230))                                # the causeway
    for x, y in ((8, 28), (40, 28), (48, 26), (22, 46), (32, 46), (40, 48)):
        house(img, x, y, 7, 5)
    church(img, 22, 28, 13)
    return clip(img)


def nw_pointe_du_hoc():
    img = tile()
    water_strip(img, "top", 9, seed=2)
    for x in range(TW):
        for y in range(9, 18):
            if inside(x + 0.5, y + 0.5):
                put(img, x, y, CHALK if (x + y) % 5 else CHALK_D)
    mound(img, 32, 34, 28, 16, base=(122, 140, 90))
    for x, y in ((14, 30), (24, 40), (36, 28), (46, 38), (30, 48), (52, 28), (18, 46)):
        crater(img, x, y, 2 + (x % 2))
    small_casemate(img, 30, 26, 12)
    rect(img, 38, 18, 2, 10, (180, 176, 160))                            # the observation post
    flag(img, 39, 8, "us", pole_len=4)
    return clip(img)


def nw_omaha():
    img = tile()
    water_strip(img, "top", 8, seed=3)
    for x in range(TW):
        for y in range(9, 22):
            if inside(x + 0.5, y + 0.5):
                put(img, x, y, SAND if (x * 3 + y) % 7 else SAND_D)
        for y in range(22, 50):
            if inside(x + 0.5, y + 0.5) and abs(x - 32) > (y - 18) // 3:   # the draw: a gully up the bluffs
                put(img, x, y, GRASS if y > 26 else (150, 146, 104))
    rect(img, 30, 22, 4, 30, (*DIRT, 230))
    hedgehogs(img, [(10, 15), (22, 18), (44, 16), (54, 19)])
    small_casemate(img, 14, 30); small_casemate(img, 40, 32, 12)
    house(img, 44, 48, 7, 5)
    return clip(img)


def nw_vierville():
    img = tile()
    water_strip(img, "top", 8, seed=4)
    for x in range(TW):
        for y in range(9, 20):
            if inside(x + 0.5, y + 0.5):
                put(img, x, y, SAND if (x + 2 * y) % 7 else SAND_D)
        for y in range(20, 52):
            if inside(x + 0.5, y + 0.5) and abs(x - 30) > (y - 16) // 4:
                put(img, x, y, (*GRASS, 255) if y > 24 else (150, 146, 104))
    rect(img, 22, 22, 18, 4, CONCRETE)                                  # the anti-tank wall across the draw
    rect(img, 22, 22, 18, 1, CONCRETE_HI)
    small_casemate(img, 8, 30, 12)
    house(img, 40, 46, 7, 5); church(img, 46, 36, 10)
    hedgehogs(img, [(14, 15), (44, 16)])
    return clip(img)


def nw_port_en_bessin():
    img = tile()
    water_strip(img, "top", 12, seed=5)
    ellipse(img, 32, 22, 12, 7, WATER)                                   # the harbour basin
    rect(img, 18, 14, 4, 12, CONCRETE); rect(img, 42, 14, 4, 12, CONCRETE)   # jetties
    for x in (26, 34):
        rect(img, x, 20, 5, 2, (180, 70, 50)); put(img, x + 2, 18, WOOD_D); put(img, x + 2, 19, WOOD_D)
    for x, y in ((8, 36), (16, 40), (24, 44), (40, 44), (48, 40), (54, 34)):
        house(img, x, y, 7, 5)
    mound(img, 6, 24, 8, 8, base=(122, 140, 90)); mound(img, 58, 24, 8, 8, base=(122, 140, 90))
    small_casemate(img, 52, 22, 8)
    return clip(img)


def nw_le_hamel():
    img = tile()
    water_strip(img, "top", 10, seed=6)
    for x in range(TW):
        for y in range(11, 24):
            if inside(x + 0.5, y + 0.5):
                put(img, x, y, SAND if (x + y) % 6 else SAND_D)
    rect(img, 4, 24, 56, 2, CONCRETE)                                    # the sea wall
    small_casemate(img, 10, 34, 16)                                      # the 75mm casemate firing along the beach
    for x, y in ((30, 34), (40, 36), (50, 34), (34, 46), (44, 48)):
        house(img, x, y, 7, 5, wall=(212, 204, 186), roof=ROOF)
    hedgehogs(img, [(18, 18), (34, 16), (50, 19)])
    return clip(img)


def nw_bayeux():
    img = tile()
    for x, y in ((6, 30), (14, 46), (44, 48), (52, 32), (8, 44), (50, 44)):
        house(img, x, y, 7, 5)
    # the cathedral of Notre-Dame: nave, twin west spires and the crossing tower
    rect(img, 18, 26, 30, 10, STONE)
    rect(img, 18, 26, 30, 1, (220, 212, 190))
    for i in range(3):
        rect(img, 17 + i, 25 - i, 32 - 2 * i, 1, SLATE if i % 2 == 0 else SLATE_D)
    for sx in (16, 21):
        rect(img, sx, 14, 4, 12, STONE)
        for i in range(7):
            rect(img, sx + 1 + (i > 3), 7 + i, 2 - (i > 3), 1, SLATE)
    rect(img, 36, 14, 7, 12, STONE)
    rect(img, 37, 12, 5, 2, STONE_D)
    for x in range(24, 46, 4):
        put(img, x, 30, (90, 110, 160))                                  # windows
    return clip(img)


def nw_courseulles():
    img = tile()
    water_strip(img, "top", 10, seed=7)
    rect(img, 30, 8, 6, 30, WATER)                                       # the harbour channel of the Seulles
    rect(img, 28, 10, 2, 22, CONCRETE); rect(img, 36, 10, 2, 22, CONCRETE)
    for x in range(TW):
        for y in range(11, 20):
            if inside(x + 0.5, y + 0.5) and not 28 <= x <= 37:
                put(img, x, y, SAND)
    for x, y in ((8, 30), (16, 32), (44, 30), (52, 32), (12, 44), (22, 46), (44, 46), (52, 44)):
        house(img, x, y, 7, 5, wall=(214, 206, 188))
    small_casemate(img, 40, 22, 10)
    return clip(img)


def nw_carpiquet():
    img = tile()
    fill_hex(img, (150, 166, 100), 160)
    line(img, 4, 40, 60, 18, (90, 88, 84)); line(img, 4, 41, 60, 19, (110, 108, 102)); line(img, 4, 42, 60, 20, (90, 88, 84))
    line(img, 10, 14, 54, 46, (90, 88, 84)); line(img, 11, 14, 55, 46, (110, 108, 102))
    for x in (14, 30):                                                  # hangars (shot up)
        rect(img, x, 44, 12, 6, (130, 132, 126))
        for i in range(12):
            put(img, x + i, 43 - int(2 * math.sin(i / 11 * math.pi)), (150, 152, 146))
    crater(img, 40, 30, 2); crater(img, 24, 24, 2); crater(img, 50, 40, 2)
    return clip(img)


def nw_caen():
    img = tile()
    for i, (x, y) in enumerate(((4, 28), (10, 44), (20, 50), (44, 50), (54, 44), (56, 28), (30, 52))):
        (ruin if i in (1, 4) else house)(img, x, y, 7, 5)
    # the castle of William the Conqueror and the Abbaye aux Hommes
    rect(img, 12, 14, 22, 12, STONE_D)
    rect(img, 12, 14, 22, 1, STONE)
    for x in range(12, 34, 3):
        put(img, x, 13, STONE_D)
    rect(img, 15, 17, 16, 9, (130, 140, 90))
    rect(img, 36, 24, 18, 10, STONE)
    for sx in (36, 50):
        rect(img, sx, 12, 4, 12, STONE)
        for i in range(6):
            rect(img, sx + 1, 6 + i, 2, 1, SLATE)
    rect(img, 36, 23, 18, 1, SLATE)
    return clip(img)


def nw_la_breche():
    img = tile()
    water_strip(img, "top", 10, seed=8)
    for x in range(TW):
        for y in range(11, 26):
            if inside(x + 0.5, y + 0.5):
                put(img, x, y, SAND if (x + y) % 5 else SAND_D)
    for x, y in ((8, 38), (20, 36), (44, 38), (54, 40)):
        house(img, x, y, 8, 6, wall=(220, 214, 198), roof=ROOF)          # seaside villas
    small_casemate(img, 28, 30, 14)
    hedgehogs(img, [(12, 18), (30, 22), (48, 18)])
    rect(img, 30, 30, 2, 22, (*DIRT, 200))
    return clip(img)


def nw_pegasus():
    img = tile()
    rect(img, 0, 22, 64, 9, WATER)                                       # the Caen Canal
    rect(img, 0, 22, 64, 1, WATER_D); rect(img, 0, 30, 64, 1, WATER_D)
    rect(img, 26, 16, 12, 20, (*DIRT, 255))                               # the road
    # the lifting bridge: counterweight frame on the east bank
    rect(img, 26, 23, 12, 7, (80, 84, 88))
    rect(img, 38, 14, 3, 10, (60, 64, 68)); rect(img, 38, 14, 10, 2, (60, 64, 68))
    for x, y, a in ((10, 44, 0), (48, 46, 1)):                            # the gliders in the field
        rect(img, x, y, 12, 2, (220, 214, 196)); rect(img, x + 4, y - 3, 2, 8, (220, 214, 196)); put(img, x + 11, y - 1, (220, 214, 196))
    house(img, 6, 16, 7, 5)                                              # the Café Gondrée
    flag(img, 20, 4, "pegasus", pole_len=8)
    return clip(img)


def nw_marcouf():
    img = tile()
    fill_hex(img, WATER, 255, [WATER_HI], 0.06, seed=11)
    for cx, cy, r in ((24, 26, 11), (44, 36, 7)):
        ellipse(img, cx, cy, r + 1, r * 0.7 + 1, SAND)
        ellipse(img, cx, cy, r, r * 0.7, GRASS)
    rect(img, 18, 20, 12, 8, STONE_D)                                    # the old fort
    rect(img, 20, 22, 8, 4, STONE)
    return clip(img)


def nw_crisbecq():
    img = tile()
    mound(img, 32, 30, 28, 18, base=(110, 134, 80))
    for x, y in ((8, 30), (26, 24), (42, 32)):
        small_casemate(img, x, y, 16)
        rect(img, x + 15, y - 4, 6, 2, GUNMETAL)
    for x, y in ((18, 44), (34, 46), (50, 20), (12, 20)):
        crater(img, x, y, 2)
    return clip(img)


def nw_la_fiere():
    img = tile()
    for cx, cy, rx, ry in ((16, 18, 14, 9), (16, 44, 14, 9), (52, 30, 10, 14)):
        ellipse(img, cx, cy, rx, ry, (*WATER, 240))
        ellipse(img, cx - 2, cy - 2, rx - 4, ry - 3, (*WATER_HI, 180))
    rect(img, 0, 29, 46, 3, (*DIRT, 255))                                # the causeway
    rect(img, 42, 27, 6, 7, (150, 146, 136))                             # the bridge over the Merderet
    house(img, 48, 22, 8, 6); house(img, 52, 32, 6, 4)                    # the manor
    return clip(img)


def nw_brecourt():
    img = tile()
    hedgerow(img, 4, 30, 60, 32, seed=3)
    hedgerow(img, 30, 6, 31, 54, seed=4)
    house(img, 8, 20, 10, 7); house(img, 40, 20, 8, 6, wall=(200, 190, 170))
    for x, y in ((10, 40), (20, 44), (40, 40), (50, 44)):                # the four 105mm guns along the hedge
        rect(img, x, y, 6, 2, GUNMETAL); disc(img, x + 1, y + 2, 1.5, RUBBER)
    return clip(img)


def nw_longues():
    img = tile()
    water_strip(img, "top", 7, seed=9)
    for x in range(TW):
        for y in range(7, 13):
            if inside(x + 0.5, y + 0.5):
                put(img, x, y, CHALK)
    rect(img, 26, 14, 10, 6, CONCRETE)                                   # the fire control post on the cliff edge
    rect(img, 27, 15, 8, 2, (40, 40, 40))
    for x in (6, 18, 34, 46):
        small_casemate(img, x, 42 - (x % 3), 12)
    return clip(img)


def nw_douvres():
    img = tile()
    fill_hex(img, (150, 160, 110), 140)
    for x, y in ((14, 24), (44, 22)):                                    # Würzburg-Riese radar dishes
        disc(img, x, y, 7, (200, 200, 196))
        disc(img, x + 1, y, 5, (170, 170, 166))
        rect(img, x - 1, y + 7, 3, 8, GUNMETAL)
    for x, y in ((24, 44), (40, 46)):
        small_casemate(img, x, y, 12)
    for x in range(4, 60, 3):                                            # wire round the perimeter
        put(img, x, 52, (90, 86, 80)); put(img, x + 1, 51, (90, 86, 80))
    return clip(img)


def nw_merville():
    img = tile()
    mound(img, 32, 30, 28, 18, base=(116, 140, 84))
    for x, y in ((8, 26), (34, 22), (12, 42), (40, 40)):                  # four casemates under earth cover
        for j in range(6):
            rect(img, x + j // 2, y - j, 16 - j, 1, (110, 132, 78) if j > 3 else CONCRETE)
        rect(img, x + 11, y - 3, 3, 2, (30, 30, 30))
    for x, y in ((28, 34), (50, 30), (26, 50), (54, 46)):
        crater(img, x, y, 2)
    return clip(img)


# ------------------------------------------------------------------ city centers

def tent(img, x, y):
    for i in range(5):
        rect(img, x - i, y - 4 + i, i * 2 + 1, 1, (120, 116, 80))
        put(img, x + i, y - 4 + i, (90, 88, 60))
    put(img, x, y, (60, 56, 40))


def city_center(side=None):
    img = tile()
    rect(img, 12, 26, 40, 2, (*DIRT, 180))
    if side == "Germany":
        # a command bunker with its pennant, sandbags and a staff car
        small_casemate(img, 16, 30, 18)
        for i in range(8):
            ellipse(img, 14 + i * 4, 36, 2, 1.2, (150, 138, 100))
        staff_car(img, 40, 48)
        flag(img, 30, 4, "cross", pole_len=20)
    else:
        for x, y in ((14, 22), (24, 20), (40, 22), (18, 34), (44, 34)):
            tent(img, x, y)
        jeep(img, 28, 48, star_mark=side == "Allies")
        if side == "Allies":
            flag(img, 30, 4, "us", pole_len=20)
            put(img, 18, 46, (200, 190, 150)); rect(img, 10, 44, 6, 4, (110, 100, 70))    # supply crates
    return clip(img)


def fleet_anchorage():
    """An Allied fleet city on a Coast tile: the headquarters ship at anchor among the transports and landing craft."""
    img = tile()
    fill_hex(img, (64, 112, 160), 255, [(80, 128, 176), (56, 100, 146)], 0.12, seed=12)
    ship(img, 6, 36, "hq")
    for x, y in ((40, 18), (46, 48), (14, 48)):                          # transports and landing craft
        rect(img, x, y - 3, 12, 3, (110, 118, 124)); rect(img, x + 3, y - 6, 5, 3, (150, 156, 162))
    for x, y in ((24, 12), (52, 30), (8, 22)):
        rect(img, x, y - 2, 6, 2, (120, 128, 132)); put(img, x + 6, y - 2, (84, 90, 94))
    return clip(img)


FEATURES = {
    "Ridge": f_ridge, "Bocage": f_bocage, "Orchard": f_orchard, "Town": f_town, "Beach": f_beach,
    "Bluffs": f_bluffs, "Cliffs": f_cliffs, "Flooded": f_flooded, "Foxholes": f_foxholes,
}
WONDERS = {
    "La Madeleine": nw_utah, "Sainte-Mere-Eglise": nw_sme, "Carentan": nw_carentan, "Pointe du Hoc": nw_pointe_du_hoc,
    "Les Moulins": nw_omaha, "Port-en-Bessin": nw_port_en_bessin, "Le Hamel": nw_le_hamel, "Bayeux": nw_bayeux,
    "Courseulles": nw_courseulles, "Carpiquet Airfield": nw_carpiquet, "Caen": nw_caen, "La Breche": nw_la_breche,
    "Pegasus Bridge": nw_pegasus, "Iles Saint-Marcouf": nw_marcouf, "Crisbecq Battery": nw_crisbecq,
    "La Fiere Causeway": nw_la_fiere, "Brecourt Manor": nw_brecourt, "Vierville Draw": nw_vierville,
    "Longues Battery": nw_longues, "Douvres Radar Station": nw_douvres, "Merville Battery": nw_merville,
}
ERA = "Second World War"
CITY_CENTERS = {
    "City center-%s" % ERA: lambda: city_center(None),
    "City center-Allies-%s" % ERA: lambda: city_center("Allies"),
    "City center-Germany-%s" % ERA: lambda: city_center("Germany"),
    "Coast+City center-Allies-%s" % ERA: fleet_anchorage,
}
