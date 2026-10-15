"""Generates docs/ORDER_OF_BATTLE.md and docs/UNITS.md from the game data, so the docs always match the mod.
Run from the repository root:  python3 tools/gen_docs.py
"""
import json, os, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import dday_oob as oob
import gen_promotions


def start_groups():
    """The START list grouped under its '# -----' comment headers in dday_oob.py (one unit per source line)."""
    src = open(os.path.join(HERE, "dday_oob.py"), encoding="utf-8").read().splitlines()
    groups, label, i = OrderedDict(), "", 0
    for line in src[src.index("START = [") + 1:]:
        s = line.strip()
        if line.startswith("]"):
            break
        if s.startswith("# -----"):
            label = s.lstrip("#- ").strip()
        elif s.startswith('("'):
            groups.setdefault((oob.START_LISTED[i][0], label), []).append(oob.START_LISTED[i])
            i += 1
    assert i == len(oob.START_LISTED)
    for u in oob.OPENING:
        groups.setdefault((u[0], "due at %s: waiting at their entry point" % oob.turn_label(oob.OPENING_TURN)), []).append(u)
    return groups


def unit_label(side, key, name):
    if name:
        return name
    return oob.unit_name(side, key)


def order_of_battle():
    out = ["# D-Day scenario - order of battle and arrival timetable", "",
           "Generated from `tools/dday_oob.py`. Turn numbers are Unciv's turn counter (top bar); the in-game clock "
           "shows the date and hour. June 6 is played hour by hour, June 7 and June 8 in two-hour turns, and each "
           "night is two turns.", "",
           "| Turns | Time |", "|---|---|",
           "| 0-16 | June 6, 6 AM to 10 PM, one hour each |",
           "| 17-18 | Night of June 6-7 (Midnight, 3 AM) |",
           "| 19-27 | June 7, 5 AM to 9 PM, two hours each |",
           "| 28-29 | Night of June 7-8 (Midnight, 3 AM) |",
           "| 30-%d | June 8, 5 AM to 9 PM, two hours each |" % oob.LAST_TURN, "",
           "## Key positions", "",
           "Thirteen cities founded on landmarks at the start. They cannot be razed. At the end of turn %d (%s) the "
           "Allies win **Hold the Beachhead** if they hold at least %d of them; otherwise Germany wins **Contain the "
           "Invasion**. Historically the Allies held %d by then. The five beaches are also where the follow-up waves come "
           "ashore once they are in Allied hands." % (oob.LAST_TURN, oob.turn_label(oob.LAST_TURN), oob.ALLIED_TARGET,
                                                      oob.HISTORICAL_ALLIED), "",
           "| Key position | Landmark | Held at the start by | Why it mattered |", "|---|---|---|---|"]
    for name, landmark, side, why in oob.OBJECTIVES:
        out.append("| %s | %s | %s | %s |" % (name, landmark, side, why))
    out += ["", "## Entry points", "",
            "| Entry | Side | Kind | Notes |", "|---|---|---|---|"]
    kinds = {"fleet": "assault force (city at sea)", "road": "road", "airhead": "airhead"}
    for name, side, lat, lon, cap, kind, desc in oob.ENTRIES:
        extra = " Its waves land on %s." % oob.BEACH_OF_FLEET[name] if kind == "fleet" else ""
        out.append("| %s%s | %s | %s | %s%s |" % (name, " (headquarters)" if cap else "", side, kinds[kind], desc, extra))
    out += ["", "## On the field at the start (turn 0, 6 AM June 6)", "",
            "The airborne divisions have been on the ground since the night. The first assault waves have just touched "
            "down below the strongpoints, the DD tanks are swimming in, and the Rangers and two Royal Marine Commandos "
            "are still in their landing craft. Units marked with a percentage start damaged.", "",
            "| Side | Group | Units |", "|---|---|---|"]
    for (side, label), rows in start_groups().items():
        names = []
        for r in rows:
            n = unit_label(side, r[1], r[2])
            if len(r) > 5:
                n += " (%d%%)" % r[5]
            names.append(n)
        out.append("| %s | %s | %s |" % (side, label[0].upper() + label[1:], "; ".join(names)))
    out += ["", "## Reinforcements", "",
            "They appear at the start of the turn, in or next to their entry city. Allied waves appear at their fleet in "
            "landing craft and must sail in and land - unless their beach is already in Allied hands, when they come "
            "ashore there. Warships always appear at the fleet. If the enemy has captured an airhead or a road town, the "
            "reinforcements due there are lost.", "",
            "| Turn | Time | Side | Entry | Arrives |", "|---|---|---|---|---|"]
    rows = OrderedDict()
    for turn, side, entry, key, names in sorted(oob.ARRIVALS, key=lambda a: (a[0], a[1] != "Allies")):
        rows.setdefault((turn, side, entry), []).extend(unit_label(side, key, n) for n in names)
    for (turn, side, entry), names in rows.items():
        out.append("| %d | %s | %s | %s | %s |" % (turn, oob.turn_label(turn), side, entry, "; ".join(names)))
    totals = {}
    for side in oob.SIDES:
        totals[side] = (sum(1 for s in oob.START if s[0] == side), sum(len(a[4]) for a in oob.ARRIVALS if a[1] == side))
    out += ["", "Totals: Allies %d units (%d at the start, %d arriving), Germany %d units (%d at the start, %d arriving)." % (
        sum(totals["Allies"]), totals["Allies"][0], totals["Allies"][1],
        sum(totals["Germany"]), totals["Germany"][0], totals["Germany"][1]),
            "Historically about 156,000 Allied soldiers landed on June 6 alone, against roughly 50,000 Germans in the "
            "invasion area that morning. One unit is a regiment, brigade or battalion; one warship stands for a "
            "bombardment group.", ""]
    return "\n".join(out)


def units_doc():
    units = json.load(open(os.path.join(ROOT, "jsons", "Units.json"), encoding="utf-8"))
    out = ["# Units", "",
           "Generated from `jsons/Units.json`. Strength is on Unciv's relative scale - a German grenadier regiment is 22.", ""]
    hidden = ("[This Unit] gets a name", "Unavailable <if", "Cannot embark <in [Land] tiles>")
    for side, title in ((None, "Base units (any army)"), ("Allies", "Allies"), ("Germany", "Germany")):
        out += ["## " + title, "", "| Unit | Type | Str | Ranged | Range | Move | Replaces | Abilities |",
                "|---|---|---|---|---|---|---|---|"]
        for u in units:
            if u.get("uniqueTo") != side:
                continue
            ab = [x for x in u.get("uniques", []) if not x.startswith(hidden)]
            out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                u["name"], u["unitType"], u.get("strength", "-"), u.get("rangedStrength", "-"),
                u.get("range", "-") if u.get("rangedStrength") else "-", u.get("movement", 0), u.get("replaces", ""),
                "<br>".join(ab).replace("|", "/")))
        out.append("")
    out += ["Every land unit except the fortifications also has *Cannot embark in Land tiles*: only units that start "
            "or arrive in landing craft are ever at sea.", "",
            "## Commanders' personal abilities", "",
            "A general gets the ability matching his name. Only the best bonus of each kind in range applies "
            "(they do not stack).", "",
            "| General | Ability | Notes |", "|---|---|---|"]
    for g in gen_promotions.GENERALS:
        out.append("| %s | %s | %s |" % (g["name"], "<br>".join(g["uniques"]), g["civilopediaText"][0]["text"]))
    out += ["", "## Promotions earned in battle", "", "| Promotion | Effect | For |", "|---|---|---|"]
    for p in gen_promotions.PROMOS:
        out.append("| %s | %s | %s |" % (p["name"], "<br>".join(p["uniques"]), ", ".join(p["unitTypes"])))
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    open(os.path.join(ROOT, "docs", "ORDER_OF_BATTLE.md"), "w", encoding="utf-8").write(order_of_battle())
    open(os.path.join(ROOT, "docs", "UNITS.md"), "w", encoding="utf-8").write(units_doc())
    print("wrote docs/ORDER_OF_BATTLE.md and docs/UNITS.md")
