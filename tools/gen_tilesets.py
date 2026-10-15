"""Generates jsons/TileSets/HexaRealm.json and FantasyHex.json: layering rules ('ruleVariants') so the mod's
terrain features (Ridge, Bocage, Orchard, Town, Beach, Bluffs, Cliffs, Flooded) combine with each tileset's own hill
and forest art. Run from the repository root:  python3 tools/gen_tilesets.py
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
EXTRAS = [None, "Bocage", "Orchard", "Town", "Beach", "Bluffs", "Cliffs", "Flooded"]


def combos():
    for base in ("Grassland", "Plains"):
        for elev in (None, "Hill", "Ridge"):
            for forest in (False, True):
                for extra in EXTRAS:
                    if not (elev == "Hill" or forest):
                        continue          # plain layering already works for these
                    feats = [f for f in (elev, "Forest" if forest else None, extra) if f]
                    yield base, elev, forest, extra, "+".join([base] + feats)


def hexarealm():
    rv = {}
    for base, elev, forest, extra, key in combos():
        layers = [base + "+Hill" if elev == "Hill" else base]
        if elev == "Ridge":
            layers.append("Ridge")
        if extra:
            layers.append(extra)
        if forest:
            layers.append("Forest" + ("G" if base == "Grassland" else "P") + ("H" if elev == "Hill" else ""))
        rv[key] = layers
    return {"ruleVariants": rv}


def fantasyhex():
    rv = {}
    for base, elev, forest, extra, key in combos():
        layers = [base]
        if elev:
            layers.append(elev)
        if extra:
            layers.append(extra)
        if forest:
            layers.append("Forest" if elev == "Hill" else base + "Forest")
        rv[key] = layers
    return {"ruleVariants": rv}


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "jsons", "TileSets"), exist_ok=True)
    for name, data in (("HexaRealm", hexarealm()), ("FantasyHex", fantasyhex())):
        with open(os.path.join(ROOT, "jsons", "TileSets", name + ".json"), "w") as f:
            json.dump(data, f, indent=4)
        print(name, len(data["ruleVariants"]), "rule variants")
