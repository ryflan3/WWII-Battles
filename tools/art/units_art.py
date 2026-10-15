"""Map sprites for every unit (64x56, facing right), drawn from the figures library, and the landing craft that
embarked units are shown in (EmbarkedUnit-<unit>)."""
import math
from figures import *

W, H = 64, 56
GROUND = 44

NEUTRAL = uniform((104, 108, 100), (74, 78, 72), (116, 112, 96), (88, 84, 70), (100, 98, 88), (76, 74, 66), (60, 54, 44))


def canvas():
    return new(W, H)


# ------------------------------------------------------------------ infantry

def squad(pal, hat, flag_kind=None, front=AIM, front2=None, rear=STAND, mg=False, bazooka=False, seed=0, extra=None):
    img = canvas()
    if flag_kind:
        bearer = dict(pal)
        bearer["F"] = WOOD_D
        flag(img, 31, 8, flag_kind, pole_len=7)
        soldier(img, 23, 15, bearer, BEARER, hat, seed=seed)
    else:
        soldier(img, 24, 16, pal, rear, hat, seed=seed + 1)
    soldier(img, 10, 17, pal, rear, hat, seed=seed + 2)
    soldier(img, 13, 28, pal, front, hat, seed=seed + 3)
    if mg:
        soldier(img, 28, 38, pal, PRONE_MG, hat, seed=seed + 4)
    elif bazooka:
        soldier(img, 30, 31, pal, BAZOOKA, hat, seed=seed + 4)
    else:
        soldier(img, 30, 29, pal, front2 or front, hat, seed=seed + 4)
    if extra:
        extra(img)
    return finish(img, (30, 42, 23, 4))


def bunker_squad(pal, hat):
    """Coastal infantry in a concrete pillbox with a machine gun."""
    img = canvas()
    CONCRETE, CONCRETE_D = (156, 152, 140), (112, 108, 100)
    for j in range(9):
        rect(img, 26 + j // 3, 44 - j, 26 - j // 2, 1, CONCRETE)
    rect(img, 40, 37, 8, 3, (30, 30, 30))
    rect(img, 47, 38, 8, 1, GUNMETAL)
    rect(img, 26, 43, 26, 2, CONCRETE_D)
    soldier(img, 12, 20, pal, STAND, hat, seed=1)
    soldier(img, 20, 27, pal, AIM, hat, seed=2)
    for x in (4, 8, 56, 60):                                     # barbed wire
        put(img, x, 42, (90, 86, 80)); put(img, x + 1, 41, (90, 86, 80)); put(img, x + 2, 42, (90, 86, 80))
    return finish(img, (32, 43, 25, 3))


def airborne(pal, hat, flag_kind, front=KNEEL, seed=0, canopy=(214, 210, 190)):
    img = canvas()
    parachute(img, 12, 7, 7, canopy)
    soldier(img, 9, 13, pal, STAND, hat, seed=seed)                # the jumper still in his harness
    if flag_kind:
        flag(img, 47, 10, flag_kind, pole_len=8)
    soldier(img, 30, 21, pal, SMG, hat, seed=seed + 1)
    soldier(img, 14, 30, pal, front, hat, seed=seed + 2)
    soldier(img, 34, 31, pal, ADVANCE, hat, seed=seed + 3)
    return finish(img, (32, 42, 22, 4))


def rangers():
    img = canvas()
    # the cliff face at Pointe du Hoc, with the grapnel ropes
    ROCK, ROCK_D, ROCK_L = (176, 168, 148), (134, 126, 110), (204, 198, 182)
    for j in range(36):
        left = 40 + int(3 * math.sin(j * 0.7)) - j // 8
        for i in range(left, 64):
            c = ROCK if (i + j) % 7 else ROCK_D
            if i == left:
                c = ROCK_D
            elif (i * 3 + j) % 11 == 0:
                c = ROCK_L
            put(img, i, 10 + j, c)
    rect(img, 38, 9, 26, 2, (96, 132, 70))                     # turf on the clifftop
    for rx in (44, 51, 57):
        line(img, rx, 9, rx - 4, 46, (200, 180, 128))
        put(img, rx - 1, 8, STEEL); put(img, rx + 1, 8, STEEL); put(img, rx, 7, STEEL)
    soldier(img, 42, 20, US_RANGER, STAND, "ranger", flip=True, seed=5)
    soldier(img, 6, 18, US_RANGER, STAND, "ranger", seed=1)
    soldier(img, 9, 29, US_RANGER, ADVANCE, "ranger", seed=2)
    soldier(img, 22, 30, US_RANGER, SMG, "ranger", seed=3)
    return finish(img, (26, 42, 22, 4))


def commandos():
    img = canvas()
    flag(img, 31, 8, "france", pole_len=7)
    b = dict(COMMANDO); b["F"] = WOOD_D
    soldier(img, 23, 15, b, BEARER, "beret", seed=1)
    soldier(img, 9, 17, COMMANDO, STAND, "beret", seed=2)
    soldier(img, 13, 28, COMMANDO, SMG, "beret", seed=3)
    soldier(img, 30, 29, COMMANDO, ADVANCE, "beret", seed=4)
    # Lovat's piper: bagpipe drones over the shoulder
    rect(img, 8, 14, 1, 4, BLACK); rect(img, 10, 13, 1, 5, BLACK); rect(img, 9, 19, 3, 2, (120, 30, 40))
    return finish(img, (30, 42, 23, 4))


def engineers(pal, hat, obstacle=True):
    img = canvas()
    if obstacle:
        hedgehog(img, 50, 42, 5)
        hedgehog(img, 58, 36, 3)
    soldier(img, 8, 19, pal, SWEEPER, hat, seed=1)
    soldier(img, 26, 28, pal, DIGGER, hat, seed=2)
    soldier(img, 10, 30, pal, STAND, hat, seed=3)
    return finish(img, (30, 42, 24, 4))


def panzergrenadiers():
    img = canvas()
    halftrack(img, 20, 44, "de")
    soldier(img, 26, 21, DE_SS, SEATED, "stahl", seed=1)
    soldier(img, 33, 21, DE_SS, SEATED, "stahl", seed=2)
    soldier(img, 6, 28, DE_SS, ADVANCE, "stahl", seed=3)
    return finish(img, (34, 43, 26, 3))


# ------------------------------------------------------------------ armour

def armour(kind, side, pair=True, crew_pal=None, crew_hat="m1"):
    img = canvas()
    if pair:
        tank(img, 2, 37, kind, side)
    tank(img, 14 if pair else 8, 47, kind, side)
    if crew_pal and kind not in ("dd",):
        x = (14 if pair else 8) + 13
        soldier(img, x, 22 if kind not in ("pz4",) else 21, crew_pal, SEATED, crew_hat)
    return finish(img, (34, 46, 27, 3))


def dd_tanks():
    img = canvas()
    tank(img, 2, 36, "dd", "us")
    tank(img, 14, 47, "dd", "us")
    return finish(img, (34, 46, 27, 3))


def dd_swimming():
    """A DD tank afloat: only the canvas flotation screen and the turret show above the waves."""
    img = canvas()
    x, y = 14, 46
    tank(img, x, y, "dd", "us")
    water = y - 6
    for px in range(W):
        for py in range(water, H):
            img.putpixel((px, py), (0, 0, 0, 0))
    foam, foam_d = (226, 236, 240, 255), (168, 196, 214, 255)
    for i in range(-4, 36):
        if img.getpixel((min(W - 1, max(0, x + i)), water - 1))[3] or i in (-4, -3, 34, 35):
            put(img, x + i, water, foam if i % 3 else foam_d)
    for i in range(1, 9):                       # wake from the propellers
        put(img, x - 2 - i * 2, water + (i % 2), foam_d)
        put(img, x - 3 - i * 2, water, foam)
    return finish(img)


def avre():
    img = canvas()
    tank(img, 8, 47, "churchill", "br")
    # a fascine (bundle of brushwood for filling ditches) carried on the front
    for i in range(4):
        ellipse(img, 28 + i * 2, 28, 3, 3, WOOD if i % 2 else WOOD_D)
    soldier(img, 22, 20, BR_INF, SEATED, "beret")
    return finish(img, (32, 46, 25, 3))


def self_propelled():
    img = canvas()
    sexton(img, 2, 37)
    sexton(img, 14, 47)
    return finish(img, (34, 46, 27, 3))


# ------------------------------------------------------------------ artillery

def battery(pal, hat, kind, side, flag_kind=None):
    img = canvas()
    if flag_kind:
        flag(img, 10, 10, flag_kind, pole_len=14)
    gun(img, 34, GROUND, kind, side)
    soldier(img, 12, 26, pal, STAND, hat, seed=1)
    soldier(img, 22, 29, pal, GUNNER, hat, seed=2)
    if kind in ("flak88",):
        soldier(img, 46, 28, pal, STAND, hat, flip=True, seed=3)
    return finish(img, (32, 42, 27, 4))


def coastal_battery():
    img = canvas()
    casemate(img, 6, 44, w=40, h=16, barrel=16)
    soldier(img, 4, 22, DE_INF, BINOCULARS, "stahl")
    return finish(img, (32, 43, 28, 3))


# ------------------------------------------------------------------ commanders and support

def commander(car, pal, hat, flag_kind, side="us"):
    img = canvas()
    flag(img, 10, 10, flag_kind, pole_len=14)
    if car == "jeep":
        jeep(img, 30, GROUND, star_mark=side == "us", body=US_TANK if side == "us" else BR_TANK)
    else:
        staff_car(img, 30, GROUND)
    soldier(img, 36, 23, pal, SEATED, hat)
    soldier(img, 14, 27, pal, BINOCULARS, hat)
    return finish(img, (32, 42, 25, 4))


def medics():
    img = canvas()
    truck(img, 32, GROUND, cross=True)
    flag(img, 12, 10, "medic", pole_len=12)
    stretcher(img, 4, 28, US_INF)
    return finish(img, (32, 43, 27, 3))


def supply():
    img = canvas()
    truck(img, 10, 40)
    jeep(img, 36, 47)
    return finish(img, (32, 44, 27, 3))


# ------------------------------------------------------------------ ships

def warship(kind):
    img = canvas()
    ship(img, 3, 42, kind)
    return finish(img)


SPRITES = {
    # generic (free play)
    "Rifle Infantry": lambda: squad(NEUTRAL, "m1", None),
    "Paratroopers": lambda: airborne(NEUTRAL, "para", None),
    "Medium Tank": lambda: armour("light", "neutral"),
    "Heavy Tank": lambda: armour("churchill", "neutral", pair=False),
    "Tank Destroyer": lambda: armour("m10", "neutral"),
    "Field Artillery": lambda: battery(NEUTRAL, "m1", "howitzer", "neutral"),
    "Anti-Tank Gun": lambda: battery(NEUTRAL, "m1", "atgun", "neutral"),
    "Destroyer": lambda: warship("destroyer"),
    "Cruiser": lambda: warship("cruiser"),
    "Battleship": lambda: warship("battleship"),
    "Headquarters Ship": lambda: warship("hq"),
    "General": lambda: commander("jeep", NEUTRAL, "m1", "beach", side="br"),
    "Engineers": lambda: engineers(NEUTRAL, "m1"),
    "Medics": medics,
    "Supply Column": supply,
    # the Allies
    "US Infantry": lambda: squad(US_INF, "m1", "us", AIM, ADVANCE, bazooka=True, seed=10),
    "British Infantry": lambda: squad(BR_INF, "brodie", "uk", AIM, mg=True, seed=20),
    "Canadian Infantry": lambda: squad(CDN_INF, "brodie", "canada", ADVANCE, AIM, seed=30),
    "US Rangers": rangers,
    "Commandos": commandos,
    "US Paratroopers": lambda: airborne(US_PARA, "m1net", "eagle", seed=40),
    "British Paratroopers": lambda: airborne(BR_PARA, "para", "pegasus", seed=50, canopy=(160, 150, 110)),
    "Sherman": lambda: armour("sherman", "us"),
    "DD Sherman": dd_tanks,
    "Sherman Firefly": lambda: armour("firefly", "br", pair=False, crew_pal=BR_INF, crew_hat="beret"),
    "Churchill AVRE": avre,
    "Cromwell": lambda: armour("cromwell", "br"),
    "M10 Tank Destroyer": lambda: armour("m10", "us"),
    "US Artillery": lambda: battery(US_INF, "m1", "howitzer", "us", "us"),
    "Royal Artillery": self_propelled,
    "Allied Anti-Tank Guns": lambda: battery(BR_INF, "brodie", "atgun", "br"),
    "US General": lambda: commander("jeep", US_GEN, "m1", "us"),
    "British General": lambda: commander("jeep", BR_GEN, "beret", "uk", side="br"),
    "Combat Engineers": lambda: engineers(US_INF, "m1"),
    # Germany
    "Grenadiers": lambda: squad(DE_INF, "stahl", None, AIM, mg=True, seed=60),
    "Coastal Infantry": lambda: bunker_squad(DE_COAST, "stahl"),
    "Ost Battalion": lambda: squad(DE_OST, "stahl", None, AIM, STAND, seed=70),
    "Fallschirmjaeger": lambda: squad(DE_FJ, "fj", None, KNEEL, mg=True, seed=80),
    "Panzergrenadiers": panzergrenadiers,
    "Panzer IV": lambda: armour("pz4", "de"),
    "Panther": lambda: armour("panther", "de", pair=False),
    "StuG III": lambda: armour("stug", "de"),
    "German Artillery": lambda: battery(DE_ART, "stahl", "howitzer", "de"),
    "Nebelwerfer": lambda: battery(DE_ART, "stahl", "werfer", "de"),
    "88 Flak": lambda: battery(DE_ART, "garrison", "flak88", "de"),
    "Coastal Battery": coastal_battery,
    "German General": lambda: commander("kuebel", DE_GEN, "cap", "cross", side="de"),
    "Pioniere": lambda: engineers(DE_INF, "stahl", obstacle=False),
}

# ------------------------------------------------------------------ embarked: the landing craft
# Unciv shows an embarked unit with "EmbarkedUnit-<unit name>", else "EmbarkedUnit-Military" / "EmbarkedUnit-Civilian".

def boat(kind, pal=None, hat="m1"):
    img = canvas()
    load = None
    if pal is not None:
        load = dict(pal)
        load["_hat"] = hat
    landing_craft(img, 12, 40, kind, load)
    return finish(img)


def lct(cargo):
    img = canvas()
    x, y = landing_craft(img, 8, 42, "lct")
    cargo(img, x, y)
    return finish(img)


EMBARKED = {
    "Military": lambda: boat("lcvp", US_INF),
    "Civilian": lambda: lct(lambda img, x, y: jeep(img, x + 8, y)),
    "US Infantry": lambda: boat("lcvp", US_INF),
    "US Paratroopers": lambda: boat("lcvp", US_PARA, "m1net"),
    "US Rangers": lambda: boat("lca", US_RANGER, "ranger"),
    "Combat Engineers": lambda: boat("lcvp", US_INF),
    "British Infantry": lambda: boat("lca", BR_INF, "brodie"),
    "Canadian Infantry": lambda: boat("lca", CDN_INF, "brodie"),
    "British Paratroopers": lambda: boat("lca", BR_PARA, "para"),
    "Commandos": lambda: boat("lca", COMMANDO, "beret"),
    "Sherman": lambda: lct(lambda img, x, y: tank(img, x, y, "sherman", "us")),
    "DD Sherman": dd_swimming,
    "Sherman Firefly": lambda: lct(lambda img, x, y: tank(img, x - 2, y, "firefly", "br")),
    "Churchill AVRE": lambda: lct(lambda img, x, y: tank(img, x - 3, y, "churchill", "br")),
    "Cromwell": lambda: lct(lambda img, x, y: tank(img, x, y, "cromwell", "br")),
    "M10 Tank Destroyer": lambda: lct(lambda img, x, y: tank(img, x, y, "m10", "us")),
    "US Artillery": lambda: lct(lambda img, x, y: gun(img, x + 16, y, "howitzer", "us")),
    "Royal Artillery": lambda: lct(lambda img, x, y: sexton(img, x, y)),
    "Allied Anti-Tank Guns": lambda: lct(lambda img, x, y: gun(img, x + 16, y, "atgun", "br")),
    "Medics": lambda: lct(lambda img, x, y: truck(img, x + 6, y, cross=True)),
    "Supply Column": lambda: lct(lambda img, x, y: truck(img, x + 6, y)),
}
