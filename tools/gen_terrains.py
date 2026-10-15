"""Generates jsons/Terrains.json: the base terrains, the Normandy terrain features and the landmarks (natural wonders),
each with its Civilopedia history. Landmarks that carry a key position city in the scenario say so.
Run from the repository root:  python3 tools/gen_terrains.py
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dday_oob as oob

LAND_BASES = ["Grassland", "Plains"]
NOT_GENERATED = "Doesn't generate naturally"


def pedia(*lines):
    return [{"text": l} for l in lines]


def base(name, kind, rgb, text, food=0, production=0, gold=0, uniques=None):
    d = {"name": name, "type": kind, "food": food, "production": production, "gold": gold, "movementCost": 1, "RGB": rgb}
    if uniques:
        d["uniques"] = uniques
    d["civilopediaText"] = pedia(*text)
    return d


def feature(name, move, defence, rgb, uniques, text, food=0, production=0, gold=0, override=False):
    d = {"name": name, "type": "TerrainFeature", "food": food, "production": production, "gold": gold,
         "movementCost": move, "defenceBonus": defence, "RGB": rgb, "occursOn": LAND_BASES, "uniques": uniques,
         "civilopediaText": pedia(*text)}
    if override:
        d["overrideStats"] = True
    return d


GRASS_GEN = [  # the generic map-generator ranges (random maps only)
    "Occurs at temperature between [-0.4] and [0.1] and humidity between [0.2] and [0.4]",
    "Occurs at temperature between [-0.5] and [0.5] and humidity between [0.6] and [1]",
    "Occurs at temperature between [0.6] and [1] and humidity between [0.4] and [1]",
    "Occurs at temperature between [-1] and [-0.4] and humidity between [0] and [1]",
    "[+3] to Fertility for Map Generation", "Considered [Desirable] when determining start locations"]
PLAINS_GEN = [
    "Occurs at temperature between [-0.4] and [0.6] and humidity between [0] and [0.6]",
    "Occurs at temperature between [0.1] and [0.6] and humidity between [0.2] and [0.4]",
    "Occurs at temperature between [0.6] and [1] and humidity between [0] and [0.4]",
    "[+4] to Fertility for Map Generation", "Considered [Desirable] when determining start locations"]

TERRAINS = [
    base("Ocean", "Water", [36, 70, 120], ["Deep water. Only used on randomly generated maps - the invasion beaches lie on the shallow Bay of the Seine."], food=1, gold=1),
    base("Coast", "Water", [60, 104, 150], [
        "The Bay of the Seine, the shallow stretch of the Channel off the Normandy coast. On the morning of D-Day a "
        "north-west wind of force 4 to 5 raised waves of four to six feet; many men in the landing craft were seasick "
        "before they reached the beach.",
        "Allied land units can cross it embarked in landing craft. German units cannot enter it."],
         food=1, gold=1, uniques=["Coastal Water"]),
    base("Lakes", "Water", [0, 150, 150], ["Ponds and lakes."], food=2, gold=1, uniques=["Fresh water"]),
    base("Grassland", "Land", [86, 140, 62], [
        "Pasture: the lush, wet meadows of the Bessin and the Cotentin, where Normandy's cattle grazed among the apple "
        "trees. Almost every field is walled by hedgerows (see Bocage); the rest is open ground."], food=2, uniques=GRASS_GEN),
    base("Plains", "Land", [190, 176, 92], [
        "Fields: the open, rolling wheat and corn country of the Caen plain, between the Seulles and the Dives. Good "
        "going for tanks, with long fields of fire - and nowhere to hide from them."], food=1, production=1, uniques=PLAINS_GEN),

    feature("Hill", 2, 0.25, [110, 126, 76],
            ["Rough terrain", "[+5] Strength for cities built on this terrain", "Has an elevation of [1] for visibility calculations",
             "Occurs in groups around high elevations", "Considered [Desirable] when determining start locations"],
            ["Hills and high ground - the Caumont ridge, Hill 112 above the Odon. Whoever holds them sees for miles across "
             "the bocage."], production=2, override=True),
    feature("Ridge", 1, 0.15, [128, 150, 84],
            ["Has an elevation of [1] for visibility calculations", NOT_GENERATED],
            ["Gentle ridges - the Périers ridge north of Caen, the Bréville ridge east of the Orne. Easy to cross, but the "
             "crest gives a view over the country around it."], production=1),
    feature("Forest", 2, 0.25, [44, 92, 44],
            ["Rough terrain", "Vegetation", "Blocks line-of-sight from tiles at same elevation", "Considered [Production] when determining start locations"],
            ["Woods: the Forêt de Cerisy, the Bois de Bavent, and woodlots everywhere. They hide troops from view and from "
             "the fighter-bombers."], production=1, food=1, override=True),
    feature("Bocage", 2, 0.33, [72, 112, 52],
            ["Rough terrain", "Blocks line-of-sight from tiles at same elevation", NOT_GENERATED],
            ["The bocage: a maze of small fields, each walled by a bank of earth three or four feet high and topped with a "
             "thick hedge and trees, with sunken lanes between them. Allied planners had studied the beaches for months but "
             "badly underestimated the hedgerows behind them.",
             "Every field was a fortress: a defender with a machine gun covered the gate, and tanks that tried to climb the "
             "banks showed their thin belly armour. The Americans called the fighting in it 'hedgerow hell'."], food=1),
    feature("Orchard", 1, 0.10, [120, 170, 70],
            ["Vegetation", NOT_GENERATED],
            ["Apple orchards - the cider and Calvados country. Some cover from view, little protection."], food=2),
    feature("Town", 2, 0.30, [150, 72, 56],
            ["Rough terrain", "Blocks line-of-sight from tiles at same elevation", NOT_GENERATED],
            ["Stone-built Norman towns and villages. Every house is a strongpoint for a defender; the Allied bombing that "
             "smashed many of them often only made better rubble to defend."], gold=2, production=1),
    feature("Beach", 1, -0.10, [226, 206, 150],
            [NOT_GENERATED],
            ["Wide, flat sand beaches backed by dunes or a sea wall. At low tide on D-Day the sand stretched hundreds of "
             "yards from the waterline to the shingle, studded with steel hedgehogs, wooden stakes and ramps tipped with "
             "mines, and swept by machine guns. There is no cover on a beach: -10% defence."]),
    feature("Bluffs", 2, 0.25, [150, 146, 104],
            ["Rough terrain", "Has an elevation of [1] for visibility calculations", NOT_GENERATED],
            ["The steep, grassy bluffs, a hundred to a hundred and fifty feet high, that rise behind the shingle of Omaha "
             "Beach. German strongpoints along the top looked straight down on the beach. The only ways up for vehicles "
             "were five narrow gullies - the 'draws'."]),
    feature("Cliffs", 3, 0.50, [120, 112, 100],
            ["Rough terrain", "Has an elevation of [1] for visibility calculations", NOT_GENERATED],
            ["Sheer limestone cliffs, like those from Pointe du Hoc to Vierville and from Port-en-Bessin to Arromanches. "
             "Almost impossible to land under or to climb - except for the Rangers."]),
    feature("Flooded", 3, -0.15, [96, 150, 160],
            [NOT_GENERATED],
            ["Rommel had the low meadows behind Utah Beach and along the Douve, the Merderet, the Aure and the Dives "
             "flooded. From the air they looked like fields; many paratroopers who came down in them drowned, weighed down "
             "by their equipment. The only ways across were narrow causeways - the roads."], food=-1),
    {"name": "River", "type": "TerrainFeature", "gold": 1, "movementCost": 0,
     "uniques": [NOT_GENERATED, "Excluded from map editor"],
     "civilopediaText": pedia(
        "Rivers and canals - the Douve, the Merderet, the Vire, the Aure, the Seulles, the Orne and the Caen Canal, the "
        "Dives. They run along tile edges.",
        "Crossing a river away from a bridge takes all remaining movement, and attacking across one costs -20%. Roads "
        "have bridges - which is why the airborne divisions were sent to seize them.")},
]

KEY_NOTE = ("KEY POSITION: in the D-Day scenario a city stands here at the start of the battle. At nightfall on June 8 "
            "the Allies win if they hold at least %d of the %d key positions; otherwise Germany wins." % (
                oob.ALLIED_TARGET, len(oob.OBJECTIVES)))
OBJECTIVE_LANDMARKS = {o[1]: o[0] for o in oob.OBJECTIVES}


def wonder(name, move, defence, elevation, text, rough=False, los=False, sight=0, base_turns="Grassland"):
    uniques = []
    if elevation:
        uniques.append("Has an elevation of [%d] for visibility calculations" % elevation)
    if rough:
        uniques.append("Rough terrain")
    if los:
        uniques.append("Blocks line-of-sight from tiles at same elevation")
    if sight:
        uniques.append("[+%d] Sight" % sight)
    uniques.append(NOT_GENERATED)
    pedia_text = pedia(*text)
    if name in OBJECTIVE_LANDMARKS:
        pedia_text.append({"text": KEY_NOTE, "color": "#FFD966"})
    return {"name": name, "type": "NaturalWonder", "movementCost": move, "defenceBonus": defence, "occursOn": LAND_BASES,
            "turnsInto": base_turns, "weight": 0, "uniques": uniques, "civilopediaText": pedia_text}


WONDERS = [
    wonder("La Madeleine", 1, 0.30, 0, [
        "Strongpoint WN 5 at La Madeleine, held by a company of the 919th Grenadier Regiment under 23-year-old Leutnant "
        "Arthur Jahnke, guarding Exit 2 - the causeway across the flooded fields behind Utah Beach.",
        "The current carried the first wave a mile south of its target, onto a stretch the bombers had smashed. Utah "
        "Beach cost the 4th Division fewer than 200 casualties - the lightest of all five beaches."]),
    wonder("Sainte-Mere-Eglise", 2, 0.30, 0, [
        "The little market town on the Cherbourg highway. A house fire had woken the townspeople and the German garrison "
        "when the first paratroopers of the 82nd Airborne came down into the square; Private John Steele hung from the "
        "church steeple for two hours, feigning death.",
        "At 4:30 AM the 505th Parachute Infantry took the town and raised the American flag over the town hall - the "
        "first town in France liberated by the Americans. The Germans counterattacked it from north and south all day "
        "and into June 7."], los=True),
    wonder("Carentan", 2, 0.35, 0, [
        "The town at the base of the Cotentin, where the highway from Cherbourg crosses the Douve marshes on a long "
        "causeway - 'Purple Heart Lane' to the 101st Airborne. Von der Heydte's paratroopers held it until June 12.",
        "Until Carentan fell, the Utah and Omaha beachheads could not join up."], los=True),
    wonder("Pointe du Hoc", 3, 0.55, 1, [
        "A promontory of hundred-foot cliffs between Utah and Omaha, with a battery of six 155mm guns in open pits and "
        "casemates that could fire on both beaches.",
        "At 7:10 AM, 225 men of the 2nd Ranger Battalion under Lt. Col. James Rudder fired grapnels to the top and climbed "
        "under fire. They found the gun positions empty: the guns had been moved inland, where a Ranger patrol found and "
        "destroyed them in an orchard. The Rangers then held the point for two days against counterattacks."], rough=True),
    wonder("Les Moulins", 2, 0.45, 1, [
        "The Les Moulins draw at Saint-Laurent-sur-Mer, one of the five gullies leading up the bluffs off Omaha Beach, "
        "guarded by strongpoints WN 66 and WN 68.",
        "On Omaha the bombers had missed, the DD tanks had sunk and the 352nd Division was waiting. By mid-morning "
        "Bradley thought of abandoning the beach - but small groups led by officers and NCOs were already working their "
        "way up the bluffs between the strongpoints. Omaha cost about 2,400 American casualties on D-Day."], rough=True),
    wonder("Port-en-Bessin", 2, 0.40, 1, [
        "The fishing harbour between Omaha and Gold, overlooked by cliffs and strongpoints on both sides. 47 Royal Marine "
        "Commando, landing on Gold, marched ten miles west behind the German lines and took it on the night of June 7-8 - "
        "linking the British and American beachheads. It later became the terminal of the PLUTO fuel pipeline."], rough=True),
    wonder("Le Hamel", 2, 0.40, 0, [
        "The fortified seafront village at the western end of Gold Beach. A 75mm gun in a casemate at WN 37, shielded "
        "from the sea and firing along the beach, knocked out tanks and landing craft until an AVRE's Petard silenced it "
        "in the afternoon. The 1st Hampshires lost their commanding officer and second-in-command on the beach."], los=True),
    wonder("Bayeux", 2, 0.30, 0, [
        "The cathedral town on the Caen-Cherbourg highway, home of the Bayeux Tapestry. The 50th Division entered it "
        "unopposed on the morning of June 7, making it the first town of any size to be liberated in France. It escaped "
        "the war almost undamaged, and on June 14 Charles de Gaulle made his first speech on French soil there."], los=True),
    wonder("Courseulles", 2, 0.40, 0, [
        "The harbour at the mouth of the Seulles, in the middle of Juno Beach. Offshore reefs delayed the landing until the "
        "rising tide had covered the beach obstacles, and the Royal Winnipeg Rifles and the Regina Rifles had to clear the "
        "strongpoints house by house. Juno cost the Canadians about 1,000 casualties, 359 of them killed."], los=True),
    wonder("Carpiquet Airfield", 1, 0.10, 0, [
        "The airfield on the plain west of Caen - the 3rd Canadian Division's final objective for D-Day. The North Nova "
        "Scotia Highlanders and the Sherbrooke Fusiliers were heading for it on June 7 when the 12th SS Panzer Division "
        "struck them at Authie and Buron. The Canadians finally took it on July 4."], base_turns="Plains"),
    wonder("Caen", 2, 0.45, 0, [
        "The capital of Lower Normandy, William the Conqueror's city, and the road and rail hub behind the British "
        "beaches - Montgomery's objective for D-Day. The 21st Panzer, 12th SS Panzer and Panzer Lehr Divisions all "
        "gathered round it, and the city was not taken until July, after it had been bombed into ruins."],
           los=True, base_turns="Plains"),
    wonder("La Breche", 1, 0.35, 0, [
        "Strongpoint WN 20, codenamed 'Cod', at La Brèche d'Hermanville in the middle of Sword Beach: bunkers, a 75mm "
        "gun, mortars and machine guns. The 1st South Lancashires and the 2nd East Yorkshires took it after a hard fight "
        "in the first hour, helped by the DD tanks and the AVREs."]),
    wonder("Pegasus Bridge", 1, 0.25, 0, [
        "The lifting bridge over the Caen Canal at Bénouville, and the bridge over the Orne at Ranville beside it. At "
        "12:16 AM three Horsa gliders carrying Major John Howard's company of the Oxfordshire and Buckinghamshire Light "
        "Infantry landed within yards of the canal bridge, and both bridges were taken intact in ten minutes.",
        "They held them until Lord Lovat's commandos arrived from Sword Beach at 1:30 PM, the bagpipes playing. The canal "
        "bridge was named after the 6th Airborne's emblem, the winged horse Pegasus."]),
    wonder("Iles Saint-Marcouf", 1, 0.50, 0, [
        "Two tiny islands four miles off Utah Beach. At 4:30 AM 132 men of the 4th and 24th Cavalry Squadrons landed on "
        "them, thinking they held a German observation post - the first Allied troops to land from the sea on D-Day. The "
        "islands were empty, but mined."]),
    wonder("Crisbecq Battery", 3, 0.60, 1, [
        "The Marcouf battery at Crisbecq: three Czech 210mm guns in huge casemates, the heaviest guns facing Utah. They "
        "sank the destroyer USS Corry and dueled with the battleship Nevada; the battery held out until June 12."], rough=True),
    wonder("La Fiere Causeway", 2, 0.30, 0, [
        "The bridge and causeway carrying the road from Sainte-Mère-Église across the flooded Merderet. For three days "
        "the 82nd Airborne fought for it against the 91st Division and its captured French tanks, until a bloody charge "
        "across the causeway on June 9 broke through."]),
    wonder("Brecourt Manor", 2, 0.30, 0, [
        "The farm near Sainte-Marie-du-Mont where four German 105mm guns were firing on Utah Beach. On the morning of D-Day "
        "Lieutenant Richard Winters led about a dozen men of Easy Company, 506th Parachute Infantry, against them and "
        "destroyed the guns - a textbook assault still taught at West Point."], los=True),
    wonder("Vierville Draw", 2, 0.45, 1, [
        "Exit D-1 at Vierville, the western end of Omaha Beach - 'Dog Green', where Company A of the 116th Infantry lost "
        "nearly all its men in minutes. The draw was blocked by a concrete wall and guarded by WN 72 and WN 73."], rough=True),
    wonder("Longues Battery", 2, 0.50, 1, [
        "Four 150mm naval guns in concrete casemates on the cliffs between Omaha and Gold, with a two-storey fire control "
        "post on the cliff edge. They dueled with HMS Ajax, HMS Argonaut and the French cruisers Georges Leygues and "
        "Montcalm until silenced; the garrison surrendered on June 7. The guns are still there today."]),
    wonder("Douvres Radar Station", 2, 0.60, 0, [
        "A Luftwaffe radar station of concrete bunkers, minefields and wire inland from Juno Beach, garrisoned by some "
        "230 men. Bypassed in the advance, it held out behind the Allied lines until June 17."], los=True),
    wonder("Merville Battery", 2, 0.50, 0, [
        "Four casemates on the coast east of the Orne, believed to hold guns that could fire on Sword Beach. Of the 600 "
        "men of Lt. Col. Terence Otway's 9th Parachute Battalion, only about 150 had gathered by 4:30 AM; they stormed the "
        "battery anyway, and found 75mm and 100mm guns. The Germans reoccupied it after the paratroopers left."]),
]

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import normandy_geo as geo
    assert {w["name"] for w in WONDERS} == set(geo.LANDMARKS), set(geo.LANDMARKS) ^ {w["name"] for w in WONDERS}
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    with open(os.path.join(root, "jsons", "Terrains.json"), "w") as f:
        json.dump(TERRAINS + WONDERS, f, indent=4, ensure_ascii=False)
    print("Wrote %d terrains (%d landmarks)" % (len(TERRAINS) + len(WONDERS), len(WONDERS)))
