"""Generates jsons/Buildings.json and jsons/UnitNameGroups.json from tools/dday_oob.py.

Every scenario objective city holds the 'Key Position' building, which the Hold the Beachhead victory counts; the five
beach cities also hold 'Beach Defenses' (counted by the German Into the Sea victory) and a 'Landing Point'.

Reinforcements appear at the start of their turn from 'arrivals' buildings, e.g.
  "[3] free [US Infantry] units appear <upon turn start> <after turn number [9]> <before turn number [10]> <for [Allies] Civilizations>"
Allied waves come from two places: the fleet's arrivals building (in the fleet city, offshore) spawns them embarked
while the beach is still German - "<if [Landing Point: Omaha Beach] is not constructed>" - and the beach's Landing
Point building spawns them ashore once the Allies hold the beach. The Landing Point stays in the beach city whoever owns
it, but its uniques only fire for the Allies.
Units spawned on a turn get their historical names from a UnitNameGroup that is only available on that turn.
Run from the repository root:  python3 tools/gen_buildings.py
"""
import json, os, sys, unicodedata
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dday_oob as oob

# Every building the scenario places carries this tag; "<if [Normandy Scenario] is constructed>" means "in the scenario"
SCENARIO_TAG = "Normandy Scenario"
HEADQUARTERS = "Headquarters"
TRANSPORT_AREA = "Transport Area"

# A captured city normally costs its new owner happiness. Happiness is meant to stay at exactly 0 (no unhappiness, no
# golden ages: see Difficulties.json and GlobalUniques.json), so every city keeps a building that removes it.
NO_OCCUPATION_UNHAPPINESS = "Removes extra unhappiness from annexed cities"


def _names(names):
    names = list(names)
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1] if names else ""


def ascii_name(text):
    """Ruleset object names double as image file names: keep them plain ASCII ("Sainte-Mere-Eglise")."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def arrivals_building(side, entry):
    return "%s Arrivals: %s" % ("Allied" if side == "Allies" else "German", ascii_name(entry))


def landing_point(beach):
    return "Landing Point: " + beach


def spawn_unique(count, unit, turn, side, extra=""):
    when = "<upon turn start> <after turn number [%d]> <before turn number [%d]> <for [%s] Civilizations>%s" % (
        turn, turn + 1, side, (" " + extra) if extra else "")
    if count == 1:
        return "Free [%s] appears %s" % (unit, when)
    return "[%d] free [%s] units appear %s" % (count, unit, when)


def timetable_text(rows, side):
    timetable = OrderedDict()
    for turn, key, names in rows:
        label = "Turn %d (%s)" % (turn, oob.turn_label(turn))
        timetable.setdefault(label, []).extend(n if n else oob.unit_name(side, key) for n in names)
    return ["%s: %s" % (label, "; ".join(units)) for label, units in timetable.items()]


def build():
    oob.check()
    key_positions = [o[0] for o in oob.OBJECTIVES]
    buildings = [
        {
            "name": HEADQUARTERS,
            "isNationalWonder": True,
            "cost": 0,
            "production": 3,
            "gold": 3,
            # Strong enough that only a real assault takes it: the other cities get no "tech" strength in this mod
            # (cityStrengthFromTechsFullMultiplier 0), so their defence is base + buildings + garrison.
            "cityStrength": 40,
            "cityHealth": 300,
            "uniques": ["Indicates the capital city", "[+25]% Production when constructing [Military] units [in this city]", NO_OCCUPATION_UNHAPPINESS],
            "civilopediaText": [
                {"text": "The army's headquarters, with its staff, signals and guard. Losing it means losing the army: in the "
                         "D-Day scenario, capturing the German headquarters at Saint-Lô wins a Breakout victory."},
                {"text": "It is far stronger than any other city: taking it needs a deliberate assault with artillery and "
                         "several regiments. The Allied headquarters is aboard ship, out of reach of the German army."},
            ]
        },
        {
            "name": "Supply Depot",
            "cost": 50,
            "production": 2,
            "food": 1,
            "gold": 2,
            "cityStrength": 5,
            "cityHealth": 25,
            "uniques": ["[+15]% Production when constructing [Military] units [in this city]", NO_OCCUPATION_UNHAPPINESS,
                        "Never destroyed when the city is captured"],
            "civilopediaText": [{"text": "Dumps of ammunition, fuel and rations, with the trucks and the repair shops."}]
        },
        {
            "name": oob.OBJECTIVE_BUILDING,
            "cost": 1,
            "cityStrength": 4,
            "cityHealth": 25,
            "uniques": [SCENARIO_TAG, "Unbuildable", "Unsellable", "Never destroyed when the city is captured", NO_OCCUPATION_UNHAPPINESS],
            "civilopediaText": [
                {"text": "One of the %d key positions of the D-Day scenario: %s." % (len(key_positions), _names(key_positions))},
                {"text": "Each is a city that cannot be razed. %s start in Allied hands - taken by the airborne in the "
                         "night; the rest are held by the Germans. At the end of turn %d (%s) the Allies win Hold the "
                         "Beachhead if they hold at least %d key positions; otherwise Germany wins Contain the Invasion." % (
                             _names(o[0] for o in oob.OBJECTIVES if o[2] == "Allies"), oob.LAST_TURN,
                             oob.turn_label(oob.LAST_TURN), oob.ALLIED_TARGET)},
            ]
        },
        {
            "name": oob.BEACH_BUILDING,
            "cost": 1,
            "cityStrength": 6,
            "cityHealth": 25,
            "uniques": [SCENARIO_TAG, "Unbuildable", "Unsellable", "Never destroyed when the city is captured", NO_OCCUPATION_UNHAPPINESS],
            "civilopediaText": [
                {"text": "A Widerstandsnest of the Atlantic Wall: concrete bunkers and casemates, machine-gun nests, a 50mm or "
                         "75mm gun sited to fire along the beach, trenches, wire and mines - and, below the high-water mark, "
                         "thousands of steel hedgehogs, stakes and ramps, many topped with mines."},
                {"text": "The five beaches - %s - are key positions. Once the Allies hold a beach, its follow-up waves "
                         "come ashore there instead of landing from the sea. If the Germans hold all five at the end of any "
                         "turn from turn %d (%s) onward, they win the Into the Sea victory." % (
                             _names(oob.BEACHES), INTO_THE_SEA_TURN, oob.turn_label(INTO_THE_SEA_TURN))},
            ]
        },
        {
            "name": TRANSPORT_AREA,
            "cost": 1,
            "uniques": [SCENARIO_TAG, "Unbuildable", "Unsellable", NO_OCCUPATION_UNHAPPINESS],
            "civilopediaText": [
                {"text": "An assault force anchored in the Transport Area, eleven miles out: transports, landing ships, "
                         "the headquarters ship and the bombarding warships."},
                {"text": "Follow-up waves are lowered into their landing craft here and appear embarked beside it at the "
                         "start of their turn. Landing craft move 5 tiles; landing on a beach takes the rest of the turn "
                         "(Rangers, Commandos and DD tanks land without stopping). Once ashore, troops cannot re-embark."},
            ]
        },
    ]

    # ---------------------------------------------------------------- arrivals
    by_entry = OrderedDict()
    for turn, side, entry, key, names in oob.ARRIVALS:
        by_entry.setdefault((side, entry), []).append((turn, key, names))
    entries = {e[0]: e for e in oob.ENTRIES}

    for (side, entry), rows in by_entry.items():
        rows.sort(key=lambda r: r[0])
        kind = entries[entry][5]
        uniques = [SCENARIO_TAG, "Unbuildable", "Unsellable"]
        landing_rows = []
        if kind == "fleet":
            beach = oob.BEACH_OF_FLEET[entry]
            for turn, key, names in rows:
                if key in oob.NAVAL_KEYS:
                    uniques.append(spawn_unique(len(names), oob.unit_name(side, key), turn, side))
                else:
                    uniques.append(spawn_unique(len(names), oob.unit_name(side, key), turn, side,
                                                "<if [%s] is not constructed>" % landing_point(beach)))
                    landing_rows.append((turn, key, names))
            text = ["Order of the follow-up waves for %s." % beach, entries[entry][6], ""]
            text += timetable_text(rows, side)
            text += ["", "They appear in their landing craft beside the fleet at the start of the listed turn and must "
                         "sail in and land. Once %s is in Allied hands, the troops (not the ships) come ashore there "
                         "instead - and if the Germans retake it, the waves land from the sea again." % beach]
        else:
            uniques.append("Destroyed when the city is captured")
            for turn, key, names in rows:
                uniques.append(spawn_unique(len(names), oob.unit_name(side, key), turn, side))
            what = "glider landings" if kind == "airhead" else "the order of march"
            text = ["%s for %s." % (what[0].upper() + what[1:], entry), entries[entry][6], ""]
            text += timetable_text(rows, side)
            text += ["", "Reinforcements appear in or next to this city at the start of the listed turn. If the enemy "
                         "captures the city, the reinforcements still due here are lost."]
        buildings.append({
            "name": arrivals_building(side, entry),
            "cost": 1,
            "uniqueTo": side,
            "uniques": uniques,
            "replacementTextForUniques": "\n".join(text),
        })
        if kind == "fleet":
            beach = oob.BEACH_OF_FLEET[entry]
            lp = [SCENARIO_TAG, "Unbuildable", "Unsellable", "Never destroyed when the city is captured"]
            for turn, key, names in landing_rows:
                lp.append(spawn_unique(len(names), oob.unit_name(side, key), turn, side))
            text = ["Follow-up waves for %s, while the Allies hold it." % beach, "",
                    *timetable_text(landing_rows, side), "",
                    "While the Allies hold %s, these troops come ashore here at the start of the listed turn instead "
                    "of appearing in their landing craft beside %s. While the Germans hold it, nothing happens here." % (beach, entry)]
            buildings.append({
                "name": landing_point(beach),
                "cost": 1,
                "uniques": lp,
                "replacementTextForUniques": "\n".join(text),
            })

    # ---------------------------------------------------------------- name groups
    groups = []
    keyed = OrderedDict()
    for turn, side, entry, key, names in oob.ARRIVALS:
        named = [n for n in names if n]
        if named:
            keyed.setdefault((side, key, turn), []).extend(named)
    for (side, key, turn), names in keyed.items():
        unit = oob.unit_name(side, key)
        groups.append({
            "name": "%s arriving on turn %d" % (unit, turn),
            "unitNames": names,
            "uniques": [unit,
                        "Only available <after turn number [%d]> <before turn number [%d]> <if [%s] is constructed>" % (turn, turn + 1, SCENARIO_TAG)],
        })
    us = [n for n in oob.FREE_PLAY_GENERALS["Allies"] if n in oob.US_GENERALS]
    for gen, names in (("US General", us), ("German General", oob.FREE_PLAY_GENERALS["Germany"])):
        groups.append({
            "name": "%ss" % gen,
            "unitNames": names,
            "uniques": [gen, "Unavailable <if [%s] is constructed>" % SCENARIO_TAG],
        })
    return buildings, groups


INTO_THE_SEA_TURN = 10     # from 4 PM on D-Day, holding all five beaches wins the Germans the Into the Sea victory

if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    b, g = build()
    with open(os.path.join(root, "jsons", "Buildings.json"), "w") as f:
        json.dump(b, f, indent=4, ensure_ascii=False)
    with open(os.path.join(root, "jsons", "UnitNameGroups.json"), "w") as f:
        json.dump(g, f, indent=4, ensure_ascii=False)
    print("Wrote %d buildings, %d unit name groups" % (len(b), len(g)))
