#!/usr/bin/env bash
# Regenerates every generated file of the mod from the scripts in tools/:
#   jsons (Units, Promotions, Buildings, UnitNameGroups, Events, TileResources, Terrains, TileSets), all Images, the
#   texture atlas, the free-play map in maps/, the scenario saves, docs/normandy_map.png and preview.png - then runs
#   Unciv's validator.
# Needs: python3 with Pillow, Java 21, internet access (first run downloads Unciv.jar and Gradle/Kotlin).
# Usage:  tools/build_all.sh            (add  --simulate  to let the AI play the whole battle as a smoke test)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOL="$ROOT/tools/cwtool"
UNCIV_VERSION="${UNCIV_VERSION:-4.22.9}"
MOD_NAME="WWII Battles"
cd "$ROOT"

echo "== ruleset files"
python3 tools/dday_oob.py > /dev/null
python3 tools/gen_units.py
python3 tools/gen_promotions.py
python3 tools/gen_buildings.py
python3 tools/gen_events.py
python3 tools/gen_terrains.py
python3 tools/gen_tilesets.py
echo "== map geography"
python3 tools/normandy_geo.py > /dev/null
echo "== images"
python3 tools/art/make_art.py

echo "== Unciv engine tool"
mkdir -p "$TOOL/lib" "$TOOL/work/mods"
if [ ! -f "$TOOL/lib/Unciv.jar" ]; then
  curl -L --fail -o "$TOOL/lib/Unciv.jar" "https://github.com/yairm210/Unciv/releases/download/$UNCIV_VERSION/Unciv.jar"
fi
# the console launcher reads the built-in rulesets from ./jsons and mods from ./mods
(cd "$TOOL/work" && rm -rf jsons && unzip -q -o ../lib/Unciv.jar 'jsons/*')
ln -sfn "$ROOT" "$TOOL/work/mods/$MOD_NAME"
(cd "$TOOL" && ./gradlew --no-daemon -q run --args="build $ROOT")

python3 tools/render_map.py
python3 tools/gen_docs.py

if [ "${1:-}" = "--simulate" ]; then
  (cd "$TOOL" && ./gradlew --no-daemon -q run --args="simulate '$ROOT/scenarios/D-Day' 40 Allies")
fi
echo "== done"
