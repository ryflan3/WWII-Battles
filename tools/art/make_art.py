"""Generates every image of the mod into <repo>/Images. Run from anywhere:  python3 tools/art/make_art.py

Afterwards pack the atlas (game.atlas / game.png) - tools/build_all.sh does both.
"""
import os, sys, json, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from figures import *
from units_art import SPRITES, EMBARKED, NEUTRAL
from icons_art import (portrait_background, nation_allies, nation_germany, leader_portrait, PROMOTION_ICONS, vector_icon,
                       pi_us_general, pi_br_general, pi_de_general, pi_hillflag, bi_headquarters, bi_depot, bi_hedgehog,
                       bi_anchor, bi_landing, bi_arrivals, bi_glider, ri_calendar, ri_watch, ri_scroll, ii_foxholes)
from tiles_art import FEATURES, WONDERS, CITY_CENTERS

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
IMAGES = os.path.join(ROOT, "Images")
UNITSET = "WWII"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gen_promotions
import gen_buildings
import gen_events
import dday_oob as oob

# ------------------------------------------------------------------ hero figures (one figure per unit, for portraits and icons)

def hero_soldier(pal, hat, pose=AIM, flag_kind=None, parachute_canopy=None):
    img = new(40, 40)
    if parachute_canopy:
        parachute(img, 10, 6, 6, parachute_canopy)
    if flag_kind:
        flag(img, 26, 4, flag_kind, pole_len=14)
    soldier(img, 8, 16, pal, pose, hat)
    return img


def hero_tank(kind, side):
    img = new(48, 40)
    tank(img, 2, 36, kind, side)
    return img


def hero_gun(kind, side):
    img = new(48, 40)
    gun(img, 18, 36, kind, side)
    return img


def hero_ship(kind):
    img = new(64, 40)
    ship(img, 2, 34, kind)
    return img


def hero_vehicle(fn):
    img = new(48, 40)
    fn(img)
    return img


def hero_general(pal, hat, flag_kind):
    img = new(40, 40)
    flag(img, 26, 4, flag_kind, pole_len=14)
    soldier(img, 10, 16, pal, BINOCULARS, hat)
    return img


HERO = {
    "Rifle Infantry": lambda f: hero_soldier(NEUTRAL, "m1"),
    "Paratroopers": lambda f: hero_soldier(NEUTRAL, "para", SMG, parachute_canopy=f and (214, 210, 190)),
    "Medium Tank": lambda f: hero_tank("light", "neutral"),
    "Heavy Tank": lambda f: hero_tank("churchill", "neutral"),
    "Tank Destroyer": lambda f: hero_tank("m10", "neutral"),
    "Field Artillery": lambda f: hero_gun("howitzer", "neutral"),
    "Anti-Tank Gun": lambda f: hero_gun("atgun", "neutral"),
    "Destroyer": lambda f: hero_ship("destroyer"),
    "Cruiser": lambda f: hero_ship("cruiser"),
    "Battleship": lambda f: hero_ship("battleship"),
    "Headquarters Ship": lambda f: hero_ship("hq"),
    "General": lambda f: hero_general(NEUTRAL, "m1", "beach"),
    "Engineers": lambda f: hero_soldier(NEUTRAL, "m1", SWEEPER),
    "Medics": lambda f: hero_vehicle(lambda img: truck(img, 12, 36, cross=True)),
    "Supply Column": lambda f: hero_vehicle(lambda img: truck(img, 12, 36)),
    "US Infantry": lambda f: hero_soldier(US_INF, "m1", AIM, f and "us"),
    "British Infantry": lambda f: hero_soldier(BR_INF, "brodie", AIM, f and "uk"),
    "Canadian Infantry": lambda f: hero_soldier(CDN_INF, "brodie", ADVANCE, f and "canada"),
    "US Rangers": lambda f: hero_soldier(US_RANGER, "ranger", ADVANCE),
    "Commandos": lambda f: hero_soldier(COMMANDO, "beret", SMG, f and "france"),
    "US Paratroopers": lambda f: hero_soldier(US_PARA, "m1net", SMG, parachute_canopy=f and (214, 210, 190)),
    "British Paratroopers": lambda f: hero_soldier(BR_PARA, "para", KNEEL, f and "pegasus"),
    "Sherman": lambda f: hero_tank("sherman", "us"),
    "DD Sherman": lambda f: hero_tank("dd", "us"),
    "Sherman Firefly": lambda f: hero_tank("firefly", "br"),
    "Churchill AVRE": lambda f: hero_tank("churchill", "br"),
    "Cromwell": lambda f: hero_tank("cromwell", "br"),
    "M10 Tank Destroyer": lambda f: hero_tank("m10", "us"),
    "US Artillery": lambda f: hero_gun("howitzer", "us"),
    "Royal Artillery": lambda f: hero_vehicle(lambda img: sexton(img, 2, 36)),
    "Allied Anti-Tank Guns": lambda f: hero_gun("atgun", "br"),
    "US General": lambda f: hero_general(US_GEN, "m1", "us"),
    "British General": lambda f: hero_general(BR_GEN, "beret", "uk"),
    "Combat Engineers": lambda f: hero_soldier(US_INF, "m1", SWEEPER),
    "Grenadiers": lambda f: hero_soldier(DE_INF, "stahl", AIM),
    "Coastal Infantry": lambda f: hero_soldier(DE_COAST, "stahl", STAND),
    "Ost Battalion": lambda f: hero_soldier(DE_OST, "stahl", STAND),
    "Fallschirmjaeger": lambda f: hero_soldier(DE_FJ, "fj", KNEEL),
    "Panzergrenadiers": lambda f: hero_vehicle(lambda img: halftrack(img, 4, 36, "de")),
    "Panzer IV": lambda f: hero_tank("pz4", "de"),
    "Panther": lambda f: hero_tank("panther", "de"),
    "StuG III": lambda f: hero_tank("stug", "de"),
    "German Artillery": lambda f: hero_gun("howitzer", "de"),
    "Nebelwerfer": lambda f: hero_gun("werfer", "de"),
    "88 Flak": lambda f: hero_gun("flak88", "de"),
    "Coastal Battery": lambda f: hero_vehicle(lambda img: casemate(img, 2, 36, w=34, h=14, barrel=10)),
    "German General": lambda f: hero_general(DE_GEN, "cap", "cross"),
    "Pioniere": lambda f: hero_soldier(DE_INF, "stahl", DIGGER),
}


def save(img, *parts):
    path = os.path.join(IMAGES, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def main():
    if os.path.isdir(IMAGES):
        shutil.rmtree(IMAGES)
    count = 0
    units = [u["name"] for u in json.load(open(os.path.join(ROOT, "jsons", "Units.json")))]
    assert set(units) == set(SPRITES) == set(HERO), ("unit list mismatch", set(units) ^ set(SPRITES), set(units) ^ set(HERO))
    save(portrait_background(), "UnitPortraits", "Background.png"); count += 1
    for name in units:
        save(SPRITES[name](), "TileSets", UNITSET, "Units", name + ".png")
        hero_color = HERO[name](True)
        outline(hero_color)
        save(fit_center(hero_color, 128, 6), "UnitPortraits", name + ".png")
        save(fit_center(silhouette(HERO[name](False)), 100, 4), "UnitIcons", name + ".png")
        count += 3
    for name, fn in EMBARKED.items():
        assert name in ("Military", "Civilian") or name in units, name
        save(fn(), "TileSets", UNITSET, "Units", "EmbarkedUnit-%s.png" % name); count += 1

    save(nation_allies(), "NationIcons", "Allies.png")
    save(nation_germany(), "NationIcons", "Germany.png")
    for leader in ("Dwight D. Eisenhower", "Erwin Rommel"):
        save(leader_portrait(leader), "LeaderIcons", leader + ".png")
    count += 4

    for name, fn in PROMOTION_ICONS.items():
        save(vector_icon(fn), "UnitPromotionIcons", name + ".png"); count += 1
    icons = {"US": vector_icon(pi_us_general), "UK": vector_icon(pi_br_general), "DE": vector_icon(pi_de_general)}
    german = set(oob.FREE_PLAY_GENERALS["Germany"])
    for g in gen_promotions.GENERALS:
        side = "DE" if g["name"] in german else "US" if g["name"] in oob.US_GENERALS else "UK"
        save(icons[side], "UnitPromotionIcons", g["name"] + ".png"); count += 1

    buildings = [b["name"] for b in json.load(open(os.path.join(ROOT, "jsons", "Buildings.json")))]
    special = {gen_buildings.HEADQUARTERS: bi_headquarters, "Supply Depot": bi_depot, oob.OBJECTIVE_BUILDING: pi_hillflag,
               oob.BEACH_BUILDING: bi_hedgehog, gen_buildings.TRANSPORT_AREA: bi_anchor}
    for b in buildings:
        if b in special:
            fn = special[b]
        elif b.startswith("Landing Point"):
            fn = bi_landing
        elif b.startswith("Allied Arrivals: Force"):
            fn = bi_landing
        elif b.startswith("Allied Arrivals"):
            fn = bi_glider
        else:
            fn = bi_arrivals
        save(vector_icon(fn), "BuildingIcons", b + ".png"); count += 1
    save(vector_icon(ii_foxholes), "ImprovementIcons", "Foxholes.png"); count += 1
    for name, fn in ((gen_events.DAY, ri_calendar), (gen_events.HOUR, ri_watch), (gen_events.HISTORY_OFF, ri_scroll)):
        save(vector_icon(fn), "ResourceIcons", name + ".png"); count += 1

    tiles = {}
    tiles.update(FEATURES); tiles.update(WONDERS); tiles.update(CITY_CENTERS)
    for name, fn in tiles.items():
        img = fn()
        save(img, "TileSets", "HexaRealm", "Tiles", name + ".png")
        save(img.resize((32, 28), Image.LANCZOS), "TileSets", "FantasyHex", "Tiles", name + ".png")
        count += 2
    print("Wrote %d images to %s" % (count, IMAGES))


if __name__ == "__main__":
    main()
