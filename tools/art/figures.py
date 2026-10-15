"""Pixel figures for 1944: soldiers, tanks, guns, ships, landing craft, vehicles and flags (all facing right)."""
import math
from pixel import *

SKIN, SKIN_D = (228, 184, 146), (192, 146, 112)
WOOD, WOOD_D = (122, 82, 44), (86, 58, 32)
STEEL, STEEL_D = (150, 154, 160), (92, 96, 102)
GUNMETAL, GUNMETAL_D = (70, 72, 76), (44, 46, 50)
RUBBER = (34, 34, 34)
CANVAS, CANVAS_D = (178, 164, 118), (140, 128, 90)
WHITE, RED, BLUE, NAVY, BLACK = (236, 236, 230), (190, 36, 42), (38, 66, 140), (26, 36, 82), (22, 22, 24)
YELLOW, GOLD = (230, 196, 60), (214, 176, 70)

# ------------------------------------------------------------------ uniforms

def uniform(helmet, helmet_d, coat, coat_d, trousers, trousers_d, webbing, boots=(46, 36, 28), extra=None):
    p = {"H": helmet, "h": helmet_d, "C": coat, "c": coat_d, "T": trousers, "t": trousers_d, "B": webbing,
         "K": boots, "S": SKIN, "s": SKIN_D, "R": WOOD, "M": STEEL_D, "m": GUNMETAL, "W": (176, 164, 120),
         "N": RED, "P": BLACK, "Y": GOLD, "G": (100, 100, 96), "L": coat_d, "F": WOOD_D}
    if extra:
        p.update(extra)
    return p


US_OD, US_OD_D = (92, 94, 58), (64, 66, 40)
US_INF = uniform(US_OD, US_OD_D, (134, 122, 84), (104, 94, 62), (98, 90, 62), (76, 70, 48), (160, 148, 104),
                 extra={"W": (176, 164, 120)})
US_PARA = uniform(US_OD, US_OD_D, (152, 140, 100), (122, 110, 76), (146, 134, 96), (116, 106, 74), (120, 112, 80),
                  boots=(96, 58, 36))
US_RANGER = uniform(US_OD, US_OD_D, (128, 118, 82), (100, 92, 62), (100, 92, 64), (78, 72, 50), (160, 148, 104),
                    extra={"O": (230, 128, 40)})
US_GEN = uniform(US_OD, US_OD_D, (96, 86, 58), (72, 64, 42), (150, 130, 96), (120, 102, 74), (90, 70, 46),
                 boots=(96, 58, 36))
US_NAVY = uniform((64, 70, 84), (44, 48, 60), (64, 78, 110), (46, 56, 82), (64, 78, 110), (46, 56, 82), (160, 148, 104))

BR_INF = uniform((100, 94, 62), (72, 68, 44), (122, 100, 64), (94, 76, 48), (116, 94, 60), (90, 72, 46), (176, 166, 128))
CDN_INF = uniform((96, 92, 60), (70, 66, 42), (110, 96, 60), (84, 72, 44), (106, 92, 58), (82, 70, 44), (170, 160, 120))
BR_PARA = uniform((96, 92, 64), (70, 66, 44), (156, 136, 92), (110, 92, 58), (116, 96, 62), (90, 74, 48), (170, 160, 122),
                  extra={"D": (92, 100, 58), "d": (112, 70, 44)})
COMMANDO = uniform((44, 96, 56), (30, 70, 40), (122, 100, 64), (94, 76, 48), (116, 94, 60), (90, 72, 46), (176, 166, 128))
BR_GEN = uniform((30, 30, 32), (16, 16, 18), (130, 108, 70), (100, 82, 52), (124, 102, 66), (96, 78, 50), (130, 100, 60),
                 extra={"N": (200, 40, 40)})

DE_INF = uniform((84, 90, 80), (60, 64, 56), (104, 108, 90), (78, 82, 68), (98, 100, 86), (74, 76, 64), (40, 36, 32),
                 boots=(28, 26, 24))
DE_COAST = uniform((84, 90, 80), (60, 64, 56), (110, 108, 88), (84, 82, 66), (100, 98, 82), (76, 74, 62), (40, 36, 32),
                   boots=(28, 26, 24))
DE_OST = uniform((84, 90, 80), (60, 64, 56), (116, 110, 82), (90, 84, 62), (104, 98, 76), (80, 76, 58), (52, 44, 34),
                 boots=(28, 26, 24))
DE_FJ = uniform((80, 86, 78), (56, 60, 54), (122, 126, 102), (92, 96, 76), (96, 100, 90), (72, 76, 68), (40, 36, 32),
                boots=(28, 26, 24), extra={"D": (88, 96, 66), "d": (108, 82, 56)})
DE_SS = uniform((84, 90, 80), (60, 64, 56), (130, 118, 72), (100, 90, 54), (96, 98, 84), (72, 74, 62), (40, 36, 32),
                boots=(28, 26, 24), extra={"D": (78, 94, 50), "d": (96, 64, 42)})
DE_GEN = uniform((96, 100, 88), (70, 74, 64), (112, 116, 100), (86, 90, 76), (104, 106, 94), (78, 80, 70), (40, 36, 32),
                 boots=(28, 26, 24), extra={"N": (196, 40, 40), "Y": (214, 180, 80)})
DE_ART = DE_INF

# ------------------------------------------------------------------ headgear (drawn above the face; face row 0)

HATS = {
    "m1":      (["...HH..", "..HHHH.", "..hhhhh"], -3),
    "m1net":   (["...hH..", "..HhHh.", "..hhhhh"], -3),
    "ranger":  (["...HH..", ".OHHHH.", "..hhhhh"], -3),
    "brodie":  (["...HH...", ".hhhhhhh"], -2),
    "para":    (["..HHH..", "..hhhh."], -2),
    "beret":   (["..HHHH.", "...hhh."], -2),
    "stahl":   (["...HHH.", "..HHHHH", ".hH...."], -2),
    "fj":      (["..HHH..", "..hhhh."], -2),
    "cap":     (["..HHH..", "..YYY..", "..hhhhh"], -3),
    "garrison": (["..HHHH.", "..hhh.."], -2),
    "bare":    ([], 0),
}

# ------------------------------------------------------------------ bodies (row 0 = top of face)

STAND = [  # rifle at the shoulder
    "...SSs..M",
    "...SSS..M",
    "..BCCCC.R",
    ".CCCBCCSR",
    ".CCCBCC.R",
    ".C.CCCC.R",
    ".S.BBBB.R",
    "...CCCC..",
    "...TTTt..",
    "...TT.T..",
    "...TT.T..",
    "...TK.K..",
    "..KK..KK.",
]
AIM = [  # standing, firing to the right
    "...SSs........",
    "...SSSRRRRmmmm",
    "..CCCSSR......",
    ".CCCCCC.......",
    ".CBCCCc.......",
    "..BBBB........",
    "..CCCC........",
    "..TTTt........",
    "..TT.TT.......",
    "..T...T.......",
    ".TT...TT......",
    ".KK...KK......",
]
ADVANCE = [  # running forward with the rifle at the port
    "...SSs.......",
    "...SSS....M..",
    "..CCCCS..R...",
    ".CCBCCSRR....",
    ".CCBCCc......",
    "..BBBB.......",
    "..CCCC.......",
    "..TTTt.......",
    ".TT..TT......",
    "TT....TT.....",
    "KK.....KK....",
]
SMG = [  # firing a sub-machine gun from the hip
    "...SSs......",
    "...SSS......",
    "..CCCCS.....",
    ".CCBCCSmmmmm",
    ".CCBCCPP....",
    "..BBBB.P....",
    "..CCCC......",
    "..TTTt......",
    "..TT.TT.....",
    "..T...T.....",
    ".KK...KK....",
]
KNEEL = [  # kneeling, firing
    "...SSs.........",
    "...SSSRRRRmmmmm",
    "..CCCSSR.......",
    ".CCCCCC........",
    ".CBCCCc........",
    "..BBBB.........",
    "..CCTTTTT......",
    "..TT....T......",
    ".KTT....T......",
    ".KKK....KK.....",
]
PRONE_MG = [  # lying behind a machine gun on its bipod
    "......SSs.......",
    "..CCCCSSSmmmmmmm",
    "TTTCCCCCCPm.....",
    "KTTTBBBBCC.m....",
]
BAZOOKA = [  # kneeling with a rocket launcher on the shoulder
    "...SSs.........",
    "..mmmmmmmmmmmmm",
    "..CCCSSm.......",
    ".CCCCCC........",
    ".CBCCCc........",
    "..BBBB.........",
    "..CCTTTTT......",
    "..TT....T......",
    ".KTT....T......",
    ".KKK....KK.....",
]
BEARER = [  # colour bearer: staff held upright in front
    "...SSs..F",
    "...SSS..F",
    "..BCCCC.F",
    ".CCCBCCSF",
    ".CCCBCC.F",
    ".C.CCCC.F",
    ".S.BBBB.F",
    "...CCCC.F",
    "...TTTt..",
    "...TT.T..",
    "...TT.T..",
    "...TK.K..",
    "..KK..KK.",
]
GUNNER = [  # gunner with a shell
    "...SSs......",
    "...SSS......",
    "..CCCCSGG...",
    ".CCCBCSGG...",
    ".CCCBCC.....",
    "..BBBB......",
    "..CCCC......",
    "..TTTt......",
    "..TT.TT.....",
    "..T...T.....",
    ".KK...KK....",
]
DIGGER = [  # engineer with a shovel
    "...SSs.....",
    "...SSS.....",
    "..CCCCS....",
    ".CCCBCSR...",
    ".CCCBCC.R..",
    "..BBBB...R.",
    "..CCCC....R",
    "..TTTt...MMM",
    "..TT.TT..MM",
    "..T...T....",
    ".KK...KK...",
]
SWEEPER = [  # engineer with a mine detector
    "...SSs........",
    "...SSS........",
    "..CCCCS.......",
    ".CCCBCSMM.....",
    ".CCCBCC..MM...",
    "..BBBB.....M..",
    "..CCCC......M.",
    "..TTTt.......M",
    "..TT.TT.....MMM",
    "..T...T.......",
    ".KK...KK......",
]
SEATED = [  # seated in a vehicle, seen above its side
    "...SSs.",
    "...SSS.",
    "..CCCCS",
    ".CCCBCS",
]
BINOCULARS = [  # an officer with binoculars
    "...SSs..",
    "...SSmm.",
    "..CCCSS.",
    ".CCCCCC.",
    ".CCBCCc.",
    "..BBBB..",
    "..CCCC..",
    "..TTTt..",
    "..TT.T..",
    "..TT.T..",
    "..TK.K..",
    ".KK..KK.",
]


def camo(img, x, y, w, h, pal, seed=0):
    """Splash the coat pixels of a figure with the palette's camouflage colours D and d."""
    if "D" not in pal:
        return
    import random
    rnd = random.Random(seed)
    for i in range(w):
        for j in range(h):
            c = img.getpixel((x + i, y + j))
            if c[3] and c[:3] in (pal["C"], pal["c"]):
                k = rnd.random()
                if k < 0.22:
                    put(img, x + i, y + j, pal["D"])
                elif k < 0.36:
                    put(img, x + i, y + j, pal["d"])


def soldier(img, x, y, pal, pose=STAND, hat="m1", flip=False, seed=0):
    """(x, y) = top-left of the face."""
    template(img, x, y, pose, pal, flip)
    w = max(len(r) for r in pose)
    camo(img, x, y, w, len(pose), pal, seed)
    rows, dy = HATS[hat]
    if rows:
        hat_w = max(len(r) for r in rows)
        template(img, x + (w - hat_w if flip else 0), y + dy, rows, pal, flip)


# ------------------------------------------------------------------ flags (x, y = top of the pole, flying right)

def flag(img, x, y, kind, pole_len=14, pole=WOOD_D):
    for j in range(pole_len):
        put(img, x, y + j, pole)
    fx, fy = x + 1, y
    if kind == "us":            # 48 stars and 13 stripes
        for j in range(7):
            rect(img, fx, fy + j, 10, 1, RED if j % 2 == 0 else WHITE)
        rect(img, fx, fy, 4, 4, NAVY)
        put(img, fx + 1, fy + 1, WHITE); put(img, fx + 3, fy + 1, WHITE); put(img, fx + 2, fy + 2, WHITE)
    elif kind == "uk":          # Union Jack
        rect(img, fx, fy, 10, 7, NAVY)
        for i in range(10):
            yy = int(i * 6 / 9)
            put(img, fx + i, fy + yy, WHITE); put(img, fx + i, fy + 6 - yy, WHITE)
        rect(img, fx, fy + 2, 10, 3, WHITE); rect(img, fx + 4, fy, 2, 7, WHITE)
        rect(img, fx, fy + 3, 10, 1, RED); rect(img, fx + 4, fy, 1, 7, RED); rect(img, fx + 5, fy, 1, 7, RED)
    elif kind == "canada":      # Canadian Red Ensign
        rect(img, fx, fy, 10, 7, RED)
        rect(img, fx, fy, 4, 3, NAVY); put(img, fx + 1, fy + 1, WHITE); put(img, fx + 2, fy + 1, RED)
        rect(img, fx + 6, fy + 2, 2, 3, (220, 200, 120))
    elif kind == "france":      # Free French: tricolour with the Cross of Lorraine
        rect(img, fx, fy, 3, 7, BLUE); rect(img, fx + 3, fy, 3, 7, WHITE); rect(img, fx + 6, fy, 3, 7, RED)
        rect(img, fx + 4, fy + 1, 1, 5, RED); put(img, fx + 3, fy + 2, RED); put(img, fx + 5, fy + 2, RED)
    elif kind == "pegasus":     # 6th Airborne: Bellerophon on Pegasus, light blue on maroon
        rect(img, fx, fy, 9, 7, (122, 30, 42))
        rect(img, fx + 2, fy + 3, 4, 2, (130, 190, 220)); put(img, fx + 6, fy + 2, (130, 190, 220))
        put(img, fx + 3, fy + 2, (130, 190, 220)); put(img, fx + 2, fy + 5, (130, 190, 220)); put(img, fx + 5, fy + 5, (130, 190, 220))
    elif kind == "eagle":       # 101st Airborne: the Screaming Eagle
        rect(img, fx, fy, 8, 7, BLACK)
        rect(img, fx + 2, fy + 2, 4, 4, WHITE); put(img, fx + 6, fy + 3, YELLOW); put(img, fx + 3, fy + 3, BLACK)
    elif kind == "aa":          # 82nd Airborne: "AA" on red, white and blue
        rect(img, fx, fy, 8, 7, (180, 40, 40))
        rect(img, fx + 1, fy + 1, 6, 5, BLUE)
        put(img, fx + 2, fy + 3, WHITE); put(img, fx + 3, fy + 2, WHITE); put(img, fx + 4, fy + 3, WHITE); put(img, fx + 5, fy + 2, WHITE)
    elif kind == "cross":       # German pennant with the Balkenkreuz
        rect(img, fx, fy, 9, 7, (82, 86, 74))
        rect(img, fx + 3, fy + 1, 3, 5, WHITE); rect(img, fx + 2, fy + 2, 5, 3, WHITE)
        rect(img, fx + 4, fy + 1, 1, 5, BLACK); rect(img, fx + 2, fy + 3, 5, 1, BLACK)
    elif kind == "medic":
        rect(img, fx, fy, 7, 6, WHITE)
        rect(img, fx + 3, fy + 1, 1, 4, RED); rect(img, fx + 1, fy + 2, 5, 2, RED)
    elif kind == "beach":       # beach-group marker flag
        rect(img, fx, fy, 8, 3, (220, 60, 60)); rect(img, fx, fy + 3, 8, 3, (240, 220, 80))
    elif kind == "navy":        # ensign: white with a red cross
        rect(img, fx, fy, 9, 6, WHITE); rect(img, fx + 3, fy, 2, 6, RED); rect(img, fx, fy + 2, 9, 2, RED)


# ------------------------------------------------------------------ vehicles

US_TANK, US_TANK_D, US_TANK_L = (86, 92, 56), (60, 64, 40), (112, 118, 74)
BR_TANK, BR_TANK_D, BR_TANK_L = (90, 92, 62), (62, 64, 42), (116, 118, 82)
DE_TANK, DE_TANK_D, DE_TANK_L = (186, 160, 96), (146, 124, 72), (210, 186, 124)
DE_GREEN, DE_BROWN = (78, 92, 52), (118, 70, 42)


def star(img, cx, cy, r=2, color=WHITE):
    """Allied white star (a tiny pixel star)."""
    put(img, cx, cy - r, color); put(img, cx, cy - r + 1, color)
    rect(img, cx - r, cy - 1 + (r > 2), r * 2 + 1, 1, color)
    rect(img, cx - 1, cy, 3, 1, color)
    put(img, cx - 1, cy + 1, color); put(img, cx + 1, cy + 1, color)
    if r > 2:
        put(img, cx - 2, cy + 2, color); put(img, cx + 2, cy + 2, color)


def balkenkreuz(img, cx, cy):
    rect(img, cx - 1, cy - 2, 3, 5, WHITE); rect(img, cx - 2, cy - 1, 5, 3, WHITE)
    rect(img, cx, cy - 2, 1, 5, BLACK); rect(img, cx - 2, cy, 5, 1, BLACK)


def tracks(img, x, y, length, wheels=5, r=2):
    """x, y = left end of the track at ground level."""
    rect(img, x + 1, y - 2 * r - 2, length - 2, 2 * r + 2, RUBBER)
    disc(img, x + r + 1, y - r - 1, r + 1, RUBBER); disc(img, x + length - r - 2, y - r - 1, r + 1, RUBBER)
    step = (length - 2 * r - 4) / max(1, wheels - 1)
    for i in range(wheels):
        cx = x + r + 2 + i * step
        disc(img, cx, y - r - 1, r, (90, 90, 86))
        put(img, cx, y - r - 1, (54, 54, 52))


def camo_stripes(img, x, y, w, h, base, seed=1):
    """Three-tone German camouflage over the pixels of colour base inside a box."""
    import random
    rnd = random.Random(seed)
    stripes = [(rnd.randint(0, w), rnd.choice((DE_GREEN, DE_BROWN))) for _ in range(5)]
    for i in range(w):
        for j in range(h):
            c = img.getpixel((x + i, y + j))
            if not c[3] or c[:3] not in base:
                continue
            for sx, col in stripes:
                if abs((i - sx) + j * 0.6) < 1.6:
                    put(img, x + i, y + j, col)


def tank(img, x, y, kind, side="us"):
    """x, y = rear of the tank at ground level. Faces right. Returns the gun muzzle position."""
    if side == "de":
        body, dark, light = DE_TANK, DE_TANK_D, DE_TANK_L
    elif side == "neutral":
        body, dark, light = (104, 106, 100), (74, 76, 72), (132, 134, 128)
    elif side == "br":
        body, dark, light = BR_TANK, BR_TANK_D, BR_TANK_L
    else:
        body, dark, light = US_TANK, US_TANK_D, US_TANK_L
    L = {"sherman": 30, "firefly": 30, "dd": 30, "churchill": 34, "cromwell": 30, "m10": 30, "pz4": 31,
         "panther": 34, "stug": 30, "light": 26}[kind]
    tracks(img, x, y, L, wheels=6 if kind in ("churchill", "pz4") else 5)
    hull_top = y - 9
    if kind in ("sherman", "firefly", "dd", "m10"):
        # rounded cast hull, sloping glacis
        rect(img, x + 1, hull_top - 4, L - 4, 5, body)
        for i in range(5):
            rect(img, x + L - 4 + i, hull_top - 4 + i, 1, 5 - i, body)
        rect(img, x + 1, hull_top - 4, L - 6, 1, light)
        tx, tw, th = x + 9, 12, 5
        if kind == "m10":
            # open-topped five-sided turret with a long 3-inch gun
            for j in range(th):
                rect(img, tx - j // 2, hull_top - 5 - j, tw + j, 1, body if j else light)
            rect(img, tx + 1, hull_top - 9, tw - 2, 1, dark)
            gun_y, gun_len = hull_top - 7, 17
        else:
            disc(img, tx + 6, hull_top - 7, 5, body)
            rect(img, tx, hull_top - 7, tw + 1, 3, body)
            rect(img, tx + 2, hull_top - 11, 7, 1, light)
            rect(img, tx + 4, hull_top - 12, 3, 1, dark)           # hatch
            gun_y = hull_top - 7
            gun_len = 22 if kind == "firefly" else 11
        rect(img, tx + tw, gun_y, gun_len, 2, GUNMETAL)
        rect(img, tx + tw, gun_y, gun_len, 1, (94, 96, 100))
        if kind == "firefly":
            rect(img, tx - 4, gun_y - 1, 4, 4, body)                 # counterweight bustle
            rect(img, tx + tw + gun_len - 3, gun_y - 1, 3, 4, GUNMETAL_D)
        if side == "us":
            star(img, x + 13, hull_top - 1, 2)
        muzzle = (tx + tw + gun_len, gun_y)
        if kind == "dd":
            # the raised canvas flotation screen hides most of the hull
            for i in range(L + 2):
                h = 11 if 2 < i < L - 1 else 9
                rect(img, x - 1 + i, y - 4 - h, 1, h, CANVAS if i % 4 else CANVAS_D)
            rect(img, x - 1, y - 15, L + 2, 1, (120, 108, 76))
            for px in (x + 6, x + 14, x + 22):
                rect(img, px, y - 17, 1, 3, WOOD_D)                  # struts
    elif kind == "churchill":
        # long, slab-sided hull with the tracks running round it, small turret and the Petard mortar
        rect(img, x, hull_top - 6, L, 7, body)
        rect(img, x, hull_top - 6, L, 1, light)
        for i in range(0, L, 5):
            put(img, x + i + 2, hull_top - 3, dark)
        rect(img, x + 11, hull_top - 11, 11, 5, body)
        rect(img, x + 11, hull_top - 11, 11, 1, light)
        rect(img, x + 22, hull_top - 9, 4, 4, GUNMETAL)               # stubby spigot mortar
        rect(img, x + 26, hull_top - 10, 2, 6, GUNMETAL_D)
        muzzle = (x + 28, hull_top - 8)
    elif kind == "light":          # generic light/medium tank for free-play base units (neutral grey)
        rect(img, x + 1, hull_top - 4, L - 2, 5, body)
        rect(img, x + 1, hull_top - 4, L - 2, 1, light)
        rect(img, x + 8, hull_top - 9, 11, 5, body)
        rect(img, x + 19, hull_top - 7, 10, 2, GUNMETAL)
        muzzle = (x + 29, hull_top - 7)
    elif kind == "cromwell":
        rect(img, x + 1, hull_top - 4, L - 2, 5, body)
        rect(img, x + 1, hull_top - 4, L - 2, 1, light)
        rect(img, x + 8, hull_top - 10, 14, 6, body)                 # flat-sided box turret
        rect(img, x + 8, hull_top - 10, 14, 1, light)
        rect(img, x + 22, hull_top - 8, 12, 2, GUNMETAL)
        muzzle = (x + 34, hull_top - 8)
    elif kind in ("pz4", "panther", "stug"):
        if kind == "panther":
            rect(img, x + 1, hull_top - 4, L - 6, 5, body)
            for i in range(7):                                       # long sloped glacis
                rect(img, x + L - 7 + i, hull_top - 4 + i * 5 // 7, 1, 5 - i * 5 // 7, body)
            rect(img, x + 9, hull_top - 10, 14, 6, body)
            for i in range(4):
                put(img, x + 23 + i, hull_top - 10 + i, body)
            rect(img, x + 9, hull_top - 10, 13, 1, light)
            rect(img, x + 23, hull_top - 8, 20, 2, GUNMETAL)
            rect(img, x + 41, hull_top - 9, 3, 4, GUNMETAL_D)         # muzzle brake
            muzzle = (x + 44, hull_top - 8)
        elif kind == "pz4":
            rect(img, x + 1, hull_top - 5, L - 2, 6, body)
            rect(img, x + 1, hull_top - 5, L - 2, 1, light)
            rect(img, x + 9, hull_top - 11, 12, 6, body)
            rect(img, x + 9, hull_top - 11, 12, 1, light)
            rect(img, x + 21, hull_top - 9, 17, 2, GUNMETAL)
            rect(img, x + 36, hull_top - 10, 3, 4, GUNMETAL_D)
            muzzle = (x + 39, hull_top - 9)
        else:   # StuG III: no turret, a low casemate with the gun in the hull
            rect(img, x + 1, hull_top - 4, L - 2, 5, body)
            rect(img, x + 7, hull_top - 8, 15, 4, body)
            for i in range(3):
                put(img, x + 22 + i, hull_top - 8 + i, body)
            rect(img, x + 7, hull_top - 8, 14, 1, light)
            rect(img, x + 23, hull_top - 6, 15, 2, GUNMETAL)
            rect(img, x + 36, hull_top - 7, 3, 4, GUNMETAL_D)
            muzzle = (x + 39, hull_top - 6)
        if kind in ("pz4", "stug"):
            # Schürzen: armour skirts hung along the sides
            for i in range(2, L - 2, 6):
                rect(img, x + i, y - 9, 5, 5, dark)
                rect(img, x + i, y - 9, 5, 1, body)
        camo_stripes(img, x, hull_top - 12, L + 10, 20, (body, light), seed=L)
        balkenkreuz(img, x + 6, hull_top - 1 if kind != "stug" else y - 7)
    return muzzle


def jeep(img, x, y, body=US_TANK, star_mark=True):
    """Willys jeep. x, y = rear wheel at ground level."""
    rect(img, x - 2, y - 8, 20, 4, body)
    rect(img, x + 10, y - 9, 8, 2, body)
    rect(img, x + 9, y - 13, 1, 5, GUNMETAL)                          # windscreen frame
    disc(img, x + 1, y - 3, 3, RUBBER); disc(img, x + 15, y - 3, 3, RUBBER)
    put(img, x + 1, y - 3, (90, 90, 86)); put(img, x + 15, y - 3, (90, 90, 86))
    if star_mark:
        star(img, x + 5, y - 6, 1)


def staff_car(img, x, y):
    """German Kübelwagen."""
    rect(img, x - 2, y - 9, 21, 5, DE_TANK)
    rect(img, x + 2, y - 11, 10, 2, DE_TANK_D)
    disc(img, x + 1, y - 3, 3, RUBBER); disc(img, x + 15, y - 3, 3, RUBBER)
    put(img, x + 1, y - 3, (90, 90, 86)); put(img, x + 15, y - 3, (90, 90, 86))


def truck(img, x, y, body=US_TANK, cover=CANVAS, cross=False):
    """2.5-ton truck ('deuce and a half'). x, y = rear wheel at ground level."""
    rect(img, x - 4, y - 16, 20, 11, cover)
    rect(img, x - 4, y - 16, 20, 1, CANVAS_D)
    for i in range(0, 20, 5):
        rect(img, x - 4 + i, y - 16, 1, 11, CANVAS_D)
    rect(img, x - 4, y - 6, 30, 2, body)
    rect(img, x + 16, y - 13, 8, 8, body)                             # cab
    rect(img, x + 18, y - 12, 4, 3, (150, 170, 180))
    rect(img, x + 24, y - 9, 3, 4, body)
    if cross:
        rect(img, x + 2, y - 14, 8, 7, WHITE); rect(img, x + 5, y - 13, 2, 5, RED); rect(img, x + 3, y - 11, 6, 2, RED)
    for wx in (x, x + 6, x + 22):
        disc(img, wx, y - 3, 3, RUBBER); put(img, wx, y - 3, (90, 90, 86))


# ------------------------------------------------------------------ guns

def gun(img, x, y, kind, side="us"):
    """Towed guns. x, y = ground point under the wheel. Muzzle points right. Returns nothing."""
    body = {"us": US_TANK, "br": BR_TANK, "de": (110, 112, 96), "neutral": (104, 106, 100)}[side]
    if kind == "flak88":
        # cruciform platform on two bogies, long barrel raised, gun shield
        rect(img, x - 14, y - 4, 30, 2, body)
        for wx in (x - 11, x + 12):
            disc(img, wx, y - 2, 2, RUBBER)
        rect(img, x - 2, y - 10, 6, 6, body)
        line(img, x + 2, y - 10, x + 26, y - 22, GUNMETAL); line(img, x + 2, y - 11, x + 26, y - 23, GUNMETAL)
        rect(img, x + 24, y - 24, 3, 3, GUNMETAL_D)
        rect(img, x + 4, y - 16, 2, 8, body)                          # shield
        return
    if kind == "werfer":
        # six barrels in a ring on a light two-wheeled carriage
        disc(img, x, y - 3, 3, RUBBER)
        line(img, x - 12, y - 1, x, y - 6, body)
        for i in range(3):
            for j in range(2):
                rect(img, x - 4 + j * 4, y - 15 + i * 3, 13, 2, GUNMETAL if (i + j) % 2 else (90, 92, 96))
        rect(img, x - 4, y - 16, 2, 10, GUNMETAL_D)
        return
    wheel_r = 5 if kind != "atgun" else 3
    # trail resting on the ground behind the gun
    line(img, x, y - wheel_r, x - 14, y, body); line(img, x, y - wheel_r + 1, x - 13, y, shade(body, 0.7))
    by = y - wheel_r - 4
    if kind == "howitzer":          # 105mm / leFH 18: short fat barrel, recoil cylinder
        rect(img, x - 4, by, 18, 3, GUNMETAL); rect(img, x - 4, by - 1, 12, 1, (96, 98, 102))
        rect(img, x + 12, by - 1, 3, 5, GUNMETAL_D)
        rect(img, x - 2, by + 3, 8, 2, body)
    elif kind == "25pdr":           # gun-howitzer with the round firing platform
        ellipse(img, x, y, 8, 1.5, GUNMETAL_D)
        rect(img, x - 4, by, 19, 2, GUNMETAL); rect(img, x + 13, by - 1, 3, 4, GUNMETAL_D)
        rect(img, x - 1, by - 5, 4, 7, body)                          # shield
    elif kind == "atgun":           # small gun with a low shield
        rect(img, x - 3, by, 18, 2, GUNMETAL); rect(img, x + 13, by - 1, 2, 4, GUNMETAL_D)
        rect(img, x - 1, by - 5, 3, 8, body)
    disc(img, x, y - wheel_r, wheel_r, RUBBER)
    disc(img, x, y - wheel_r, wheel_r - 2, (80, 80, 78))
    put(img, x, y - wheel_r, (40, 40, 40))


def casemate(img, x, y, w=30, h=12, barrel=14):
    """A concrete gun casemate facing right. x, y = bottom-left."""
    CONCRETE, CONCRETE_D, CONCRETE_L = (156, 152, 140), (112, 108, 100), (186, 182, 170)
    for j in range(h):
        rect(img, x + j // 3, y - j, w - j // 2, 1, CONCRETE if j < h - 2 else CONCRETE_L)
    rect(img, x + w - 6, y - h + 3, 5, 5, (30, 30, 30))                # embrasure
    rect(img, x + w - 3, y - h + 5, barrel, 2, GUNMETAL)
    rect(img, x, y - 2, w, 2, CONCRETE_D)
    for i in range(4):
        put(img, x + 3 + i * 6, y - h + 2, CONCRETE_D)


# ------------------------------------------------------------------ ships (side view, facing right; x, y = stern at the waterline)

HULL, HULL_D, DECK, SUPER = (118, 126, 136), (78, 86, 96), (150, 156, 162), (170, 174, 180)


def wake(img, x, y, length):
    for i in range(0, length, 3):
        put(img, x + i, y + 1, (220, 232, 240, 200))
        put(img, x + i + 1, y + 2, (200, 220, 236, 150))


def ship(img, x, y, kind):
    if kind == "battleship":
        L, H = 58, 6
    elif kind == "cruiser":
        L, H = 54, 5
    elif kind == "destroyer":
        L, H = 46, 4
    else:   # hq: transport/command ship
        L, H = 52, 6
    wake(img, x - 2, y, L + 4)
    for i in range(L):
        bow = max(0, i - (L - 8))
        rect(img, x + i, y - H + bow // 2, 1, H - bow // 2, HULL if i % 9 else HULL_D)
    rect(img, x, y - H, L - 6, 1, DECK)
    rect(img, x + 2, y - 1, L - 6, 1, HULL_D)                           # boot topping
    if kind == "battleship":
        for tx in (x + 8, x + 18, x + 40):
            rect(img, tx, y - H - 3, 7, 3, SUPER); rect(img, tx + 7, y - H - 2, 8, 1, GUNMETAL); rect(img, tx + 7, y - H - 3, 8, 1, GUNMETAL)
        rect(img, x + 26, y - H - 10, 10, 10, SUPER)                    # bridge and tower mast
        rect(img, x + 29, y - H - 17, 4, 7, SUPER)
        rect(img, x + 30, y - H - 22, 1, 5, GUNMETAL_D)
        rect(img, x + 20, y - H - 7, 4, 4, HULL_D)                      # funnel
    elif kind == "cruiser":
        for tx in (x + 6, x + 38):
            rect(img, tx, y - H - 3, 6, 3, SUPER); rect(img, tx + 6, y - H - 2, 6, 1, GUNMETAL)
        rect(img, x + 18, y - H - 8, 14, 8, SUPER)
        rect(img, x + 21, y - H - 13, 3, 5, HULL_D); rect(img, x + 27, y - H - 12, 3, 4, HULL_D)
        rect(img, x + 24, y - H - 19, 1, 11, GUNMETAL_D)
    elif kind == "destroyer":
        rect(img, x + 4, y - H - 2, 5, 2, SUPER); rect(img, x + 9, y - H - 1, 5, 1, GUNMETAL)
        rect(img, x + 30, y - H - 3, 5, 3, SUPER); rect(img, x + 35, y - H - 2, 5, 1, GUNMETAL)
        rect(img, x + 20, y - H - 7, 9, 7, SUPER)
        rect(img, x + 15, y - H - 6, 3, 6, HULL_D)
        rect(img, x + 24, y - H - 13, 1, 6, GUNMETAL_D)
    else:
        rect(img, x + 20, y - H - 9, 16, 9, SUPER)
        rect(img, x + 25, y - H - 13, 4, 4, HULL_D)
        for mx in (x + 8, x + 44):                                     # masts and radio aerials
            rect(img, mx, y - H - 20, 1, 20, GUNMETAL_D)
            line(img, mx, y - H - 20, x + 27, y - H - 14, (60, 62, 66, 200))
        for bx in (x + 10, x + 38):
            rect(img, bx, y - H - 3, 6, 3, (110, 116, 104))            # landing craft in davits
        flag(img, x + 44, y - H - 22, "navy", pole_len=2, pole=GUNMETAL_D)


def landing_craft(img, x, y, kind="lcvp", load=None):
    """Landing craft, facing right. x, y = stern at the waterline. load: palette for helmets, or 'tank' etc."""
    GREY, GREY_D, GREY_L = (118, 128, 134), (80, 88, 94), (150, 158, 162)
    if kind in ("lcvp", "lca"):
        L, Hh = 38, 10
        wake(img, x - 3, y, L + 3)
        hull = GREY if kind == "lcvp" else (128, 134, 124)
        rect(img, x, y - Hh, L - 4, Hh, hull)
        rect(img, x, y - Hh, L - 4, 1, GREY_L)
        rect(img, x + 1, y - 3, L - 5, 2, GREY_D)
        for i in range(4):                                       # the bow ramp, slightly raked
            rect(img, x + L - 4 + i, y - Hh - 1 + i // 2, 1, Hh + 1 - i // 2, GREY_D if i else GREY)
        if kind == "lca":                                        # British LCA: armoured cover over the after part
            rect(img, x, y - Hh - 2, 12, 2, GREY_D)
        rect(img, x + 2, y - Hh - 5, 4, 5, GREY_D)                 # coxswain's station
        put(img, x + 3, y - Hh - 6, SKIN)
        if load is not None:
            hat = load.get("_hat", "m1")
            top = y - Hh
            for row in (1, 0):                                   # two rows of men crouching inside: helmets above the gunwale
                for hx in range(x + 8 + row * 2, x + L - 9, 5):
                    hy = top - 1 - row * 2
                    if hat == "brodie":
                        rect(img, hx - 1, hy, 5, 1, load["h"]); rect(img, hx, hy - 1, 3, 1, load["H"])
                    elif hat == "beret":
                        rect(img, hx, hy, 3, 1, load["h"]); rect(img, hx, hy - 1, 4, 1, load["H"])
                    else:
                        rect(img, hx, hy, 3, 1, load["h"]); rect(img, hx, hy - 1, 3, 1, load["H"]); put(img, hx + 1, hy - 2, load["H"])
                        if hat == "ranger":
                            put(img, hx, hy - 1, load["O"])
                    put(img, hx + 1, hy + 1, SKIN)
        return
    # LCT: long, flat, with the cargo on deck
    L = 44
    wake(img, x - 2, y, L + 2)
    rect(img, x, y - 6, L - 3, 6, GREY)
    rect(img, x, y - 6, L - 3, 1, GREY_D)
    rect(img, x + L - 3, y - 7, 3, 7, GREY_D)
    rect(img, x + 1, y - 13, 6, 7, GREY_D)                               # wheelhouse aft
    return (x + 8, y - 6)                                                # where the cargo sits


def finish(img, shadow_box=None):
    """Outline and drop shadow for a unit sprite."""
    outline(img)
    if shadow_box:
        cx, cy, rx, ry = shadow_box
        img = shadow(img, cx, cy, rx, ry)
    return img


# ------------------------------------------------------------------ extras

def halftrack(img, x, y, side="de"):
    """Sd.Kfz. 251 (or M3) half-track. x, y = rear of the track at ground level."""
    body, dark, light = (DE_TANK, DE_TANK_D, DE_TANK_L) if side == "de" else (US_TANK, US_TANK_D, US_TANK_L)
    tracks(img, x, y, 18, wheels=4, r=2)
    disc(img, x + 27, y - 3, 3, RUBBER); put(img, x + 27, y - 3, (90, 90, 86))
    rect(img, x, y - 13, 24, 7, body)
    for i in range(6):                                           # the angled armoured bonnet
        rect(img, x + 24 + i, y - 12 + i // 2, 1, 6 - i // 2, body)
    rect(img, x, y - 13, 24, 1, light)
    rect(img, x + 2, y - 10, 20, 1, dark)
    if side == "de":
        camo_stripes(img, x, y - 14, 32, 10, (body, light), seed=7)
        balkenkreuz(img, x + 8, y - 9)
    else:
        star(img, x + 8, y - 9, 2)


def sexton(img, x, y):
    """Sexton self-propelled 25-pounder: a tank chassis with an open-topped gun compartment."""
    tracks(img, x, y, 30, wheels=5)
    rect(img, x + 1, y - 13, 26, 5, BR_TANK)
    for i in range(4):
        rect(img, x + 26 + i, y - 13 + i, 1, 5 - i, BR_TANK)
    rect(img, x + 4, y - 18, 18, 5, BR_TANK)                     # open box
    rect(img, x + 4, y - 18, 18, 1, BR_TANK_L)
    rect(img, x + 6, y - 19, 14, 1, BR_TANK_D)
    rect(img, x + 18, y - 17, 16, 2, GUNMETAL); rect(img, x + 32, y - 18, 3, 4, GUNMETAL_D)


def hedgehog(img, cx, y, size=4, color=(84, 78, 72)):
    """Czech hedgehog beach obstacle: three crossed steel beams."""
    line(img, cx - size, y, cx + size, y - size * 2, color)
    line(img, cx + size, y, cx - size, y - size * 2, color)
    line(img, cx, y + 1, cx, y - size * 2 - 1, shade(color, 1.3))


def parachute(img, cx, cy, r=7, canopy=(214, 210, 190), shadow_c=(170, 164, 140)):
    """A parachute canopy with its rigging lines, the jumper below."""
    for x in range(cx - r, cx + r + 1):
        for yy in range(cy - r // 2 - 1, cy + 1):
            if ((x - cx) / r) ** 2 + ((yy - cy) / (r * 0.6)) ** 2 <= 1:
                put(img, x, yy, canopy if (x - cx) % 3 else shadow_c)
    for dx in (-r, -r // 2, r // 2, r):
        line(img, cx + dx, cy, cx, cy + r + 2, (120, 116, 100, 200))


def stretcher(img, x, y, pal):
    """Two bearers carrying a stretcher. x, y = top-left of the first bearer's face."""
    soldier(img, x, y, pal, STAND, "m1")
    soldier(img, x + 14, y, pal, STAND, "m1")
    rect(img, x + 4, y + 6, 16, 2, CANVAS)
    rect(img, x + 2, y + 6, 20, 1, WOOD_D)
    for (bx, by) in ((x + 3, y + 3), (x + 17, y + 3)):           # red-cross armbands
        put(img, bx, by, WHITE); put(img, bx, by + 1, RED)
