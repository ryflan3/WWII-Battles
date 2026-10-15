"""Order of battle and timetable for the D-Day scenario (the Normandy landings, June 6-8, 1944).

Turn numbers are Unciv's turn counter (shown in the top bar). Turn 0 = 6 AM, June 6: H-Hour on the American beaches.
June 6 is played hour by hour; June 7 and June 8 in two-hour turns; each night is compressed into two turns.

Everything else (Buildings.json arrival timetables, UnitNameGroups.json, the scenario saves, the docs, the briefings)
is generated from this file, so edit the battle here.

Positions are (latitude, longitude) in degrees, as on a modern map of Normandy.
"""

SIDES = ("Allies", "Germany")
OTHER = {"Allies": "Germany", "Germany": "Allies"}

# ---------------------------------------------------------------- time

DAY_START = {6: 0, 7: 19, 8: 30}      # first daylight turn of each day of June
LAST_TURN = 38                         # 9 PM, June 8 - "Hold the Beachhead" is decided from the end of this turn


def clock(t):
    """(day of June, hour on the 24-hour clock) at the start of turn t - the in-game clock in the top bar."""
    if t <= 16:
        return 6, 6 + t                # June 6, 6 AM - 10 PM, hourly
    if t in (17, 18):
        return (7, 0) if t == 17 else (7, 3)
    if t <= 27:
        return 7, 5 + 2 * (t - 19)     # June 7, 5 AM - 9 PM, every two hours
    if t in (28, 29):
        return (8, 0) if t == 28 else (8, 3)
    h = 5 + 2 * (t - 30)               # June 8 from 5 AM; past turn 38 the clock runs on
    return (8, h) if h < 24 else (9, h - 24)


def _hour(h):
    # no "7:00": Unciv reformats numbers in displayed text and would show it as "7:0"
    if h in (0, 12):
        return "Midnight" if h == 0 else "Noon"
    return "%d %s" % (h % 12, "AM" if h < 12 else "PM")


def turn_label(t):
    """Human readable time of day for a turn number."""
    if t in (17, 18):
        return "Night of June 6-7"
    if t in (28, 29):
        return "Night of June 7-8"
    day, h = clock(t)
    return "%s, June %d" % (_hour(h), day)


def is_night(t):
    return t in (17, 18, 28, 29)


# ---------------------------------------------------------------- unit type keys

A = {
    "USINF": "US Infantry", "BRINF": "British Infantry", "CDNINF": "Canadian Infantry", "RANGER": "US Rangers",
    "CDO": "Commandos", "USPARA": "US Paratroopers", "BRPARA": "British Paratroopers",
    "SHERMAN": "Sherman", "DD": "DD Sherman", "FIREFLY": "Sherman Firefly", "AVRE": "Churchill AVRE",
    "CROMWELL": "Cromwell", "M10": "M10 Tank Destroyer", "USART": "US Artillery", "BRART": "Royal Artillery",
    "AT": "Allied Anti-Tank Guns", "BB": "Battleship", "CRU": "Cruiser", "DES": "Destroyer",
    "USGEN": "US General", "BRGEN": "British General", "ENG": "Combat Engineers", "MED": "Medics",
    "HQSHIP": "Headquarters Ship",
}
G = {
    "GREN": "Grenadiers", "COAST": "Coastal Infantry", "OST": "Ost Battalion", "FJ": "Fallschirmjaeger",
    "PZGREN": "Panzergrenadiers", "PZIV": "Panzer IV", "PANTHER": "Panther", "STUG": "StuG III",
    "GART": "German Artillery", "WERFER": "Nebelwerfer", "FLAK": "88 Flak", "BATT": "Coastal Battery",
    "GGEN": "German General", "PION": "Pioniere",
}
NAVAL_KEYS = ("BB", "CRU", "DES", "HQSHIP")
CIVILIAN_KEYS = ("USGEN", "BRGEN", "GGEN", "MED")


def unit_name(side, key):
    return (A if side == "Allies" else G)[key]


# ---------------------------------------------------------------- entry points (cities)
# (name, side, lat, lon, is_capital, kind, description)
# kind "fleet": an Allied assault force anchored in the Channel - a city on a water tile that no German unit can reach.
#   Its follow-up waves are lowered into landing craft there and must sail in and land. Once the beach it serves
#   (BEACH_OF_FLEET) is in Allied hands, they come ashore at the beach instead.
# kind "airhead": an airborne position held at dawn - glider reinforcements land there; lost if the Germans take it.
# kind "road": a road into the battlefield for German reinforcements; lost if the Allies take the town.

ENTRIES = [
    ("Force U", "Allies", 49.500, -1.070, False, "fleet",
     "Rear Admiral Don P. Moon's Force U, flagship USS Bayfield: the transports, landing ships and gunfire support "
     "ships for Utah Beach, anchored in the Transport Area about eleven miles off the Cotentin shore."),
    ("Force O", "Allies", 49.468, -0.880, False, "fleet",
     "Rear Admiral John L. Hall's Force O, flagship USS Ancon, for Omaha Beach. General Omar Bradley, commanding the "
     "US First Army, watched the landings from the cruiser USS Augusta nearby."),
    ("Force G", "Allies", 49.438, -0.560, True, "fleet",
     "Commodore C. E. Douglas-Pennant's Force G, headquarters ship HMS Bulolo, carrying the British 50th Division to "
     "Gold Beach, in the middle of the five beaches. This is the Allied headquarters."),
    ("Force J", "Allies", 49.432, -0.432, False, "fleet",
     "Commodore G. N. Oliver's Force J, headquarters ship HMS Hilary, carrying the 3rd Canadian Division to Juno Beach."),
    ("Force S", "Allies", 49.398, -0.282, False, "fleet",
     "Rear Admiral Arthur Talbot's Force S, headquarters ship HMS Largs, carrying the British 3rd Division to Sword Beach."),
    ("Saint-Lô", "Germany", 49.116, -1.091, True, "road",
     "Headquarters of General Erich Marcks's LXXXIV Corps, which defended the whole invasion coast, and the hub of the "
     "roads from Brittany and the south. The German headquarters."),
    ("Valognes Road", "Germany", 49.503, -1.430, False, "road",
     "The highway from Cherbourg and Valognes, down which the 709th and 243rd Divisions sent their reserves against "
     "the American airborne."),
    ("Villers-Bocage", "Germany", 49.083, -0.656, False, "road",
     "The market town on the road from Le Mans and Alençon. The Panzer Lehr Division, bombed and strafed every mile "
     "of its march from Chartres, came up this way on June 8."),
    ("Falaise Road", "Germany", 49.086, -0.340, False, "road",
     "The road north from Falaise to Caen. The 21st Panzer Division's tanks and the 12th SS Panzer Division came "
     "up it to the battle for Caen."),
    ("Lisieux Road", "Germany", 49.160, -0.092, False, "road",
     "The road from Lisieux, east of the Dives. The 711th and 346th Infantry Divisions came this way to attack the "
     "British airborne bridgehead east of the Orne."),
    ("Sainte-Mère-Église", "Allies", 49.408, -1.317, False, "airhead",
     "The first town in France liberated by the Americans: Lt. Col. Edward Krause's 3rd Battalion, 505th Parachute "
     "Infantry, raised the flag over the town hall at 4:30 AM. Gliders of the 82nd Airborne land here."),
    ("Pegasus Bridge", "Allies", 49.242, -0.274, False, "airhead",
     "The bridges over the Caen Canal and the Orne at Bénouville and Ranville, taken intact by Major John Howard's "
     "glider-borne company at 12:16 AM. The 6th Airlanding Brigade's gliders land beside them."),
]

FLEETS = [e[0] for e in ENTRIES if e[5] == "fleet"]
BEACH_OF_FLEET = {"Force U": "Utah Beach", "Force O": "Omaha Beach", "Force G": "Gold Beach",
                  "Force J": "Juno Beach", "Force S": "Sword Beach"}

# ---------------------------------------------------------------- key positions (objective cities)
# The scenario founds a city on each of these landmarks. Cities cannot be razed. At the end of turn LAST_TURN (9 PM,
# June 8) the Allies win "Hold the Beachhead" if they hold at least ALLIED_TARGET of them; otherwise Germany wins
# "Contain the Invasion". The five beaches are also the landing points
# for the follow-up waves once taken, and the German "Into the Sea" victory needs all five of them.
# By nightfall on June 8, 1944 the Allies held 10 of the 13 (everything but Carentan, Carpiquet and Caen), so with
# ALLIED_TARGET = 10 the Allies win by matching history and Germany by doing better than it did. ALLIED_TARGET and the
# German "+10% Strength" in Nations.json are the balance levers: the share of Allied wins in AI-vs-AI battles
# (tools/cwtool Balance.kt) - see README "How it was checked".
ALLIED_TARGET = 10
GERMAN_TARGET = 14 - ALLIED_TARGET      # 13 key positions: exactly one side reaches its target
HISTORICAL_ALLIED = 10
OBJECTIVE_BUILDING = "Key Position"
BEACH_BUILDING = "Beach Defenses"     # in the five beach cities only: the German "Into the Sea" victory counts it
OBJECTIVES = [  # (city name, landmark, side at the start, why it mattered)
    ("Utah Beach", "La Madeleine", "Germany",
     "Strongpoint WN 5 at La Madeleine, guarding the causeway (Exit 2) across the flooded fields behind the beach."),
    ("Sainte-Mère-Église", "Sainte-Mere-Eglise", "Allies",
     "The crossroads town on the Cherbourg highway, taken by the 505th Parachute Infantry in the night."),
    ("Carentan", "Carentan", "Germany",
     "The town on the causeway between Utah and Omaha. Until it fell, the two American beachheads could not join."),
    ("Pointe du Hoc", "Pointe du Hoc", "Germany",
     "The clifftop battery that could fire on both American beaches. Three companies of Rangers climbed the cliffs to take it."),
    ("Omaha Beach", "Les Moulins", "Germany",
     "The Les Moulins draw at Saint-Laurent, one of the five gullies up the bluffs that were the only ways off Omaha Beach."),
    ("Port-en-Bessin", "Port-en-Bessin", "Germany",
     "The fishing harbour between Omaha and Gold, where the American and British beachheads were to meet."),
    ("Gold Beach", "Le Hamel", "Germany",
     "The fortified seafront village of Le Hamel, whose 75mm gun swept Gold Beach until the afternoon."),
    ("Bayeux", "Bayeux", "Germany",
     "The old cathedral town on the Caen-Cherbourg highway, the British 50th Division's objective for D-Day."),
    ("Juno Beach", "Courseulles", "Germany",
     "The harbour town of Courseulles at the mouth of the Seulles, the heart of Juno Beach."),
    ("Carpiquet", "Carpiquet Airfield", "Germany",
     "The airfield west of Caen, the 3rd Canadian Division's final objective on D-Day."),
    ("Caen", "Caen", "Germany",
     "The great road and rail hub of Lower Normandy. Montgomery hoped to take it on D-Day; it took six weeks."),
    ("Sword Beach", "La Breche", "Germany",
     "Strongpoint WN 20 'Cod' at La Brèche d'Hermanville, in the middle of Sword Beach."),
    ("Pegasus Bridge", "Pegasus Bridge", "Allies",
     "The canal and river bridges that linked the beaches to the airborne bridgehead east of the Orne."),
]
BEACHES = [o[0] for o in OBJECTIVES if o[0].endswith(" Beach")]
FLEET_OF_BEACH = {b: f for f, b in BEACH_OF_FLEET.items()}

# ---------------------------------------------------------------- units on the field at 6 AM, June 6
# (side, type key, instance name, lat, lon[, health]). A unit placed on a water tile starts embarked (Allies only).
# The airborne divisions have been on the ground since the night. The first assault waves have just touched down on
# the beaches, below the strongpoints; the DD tanks are swimming in, and the Rangers and two Royal Marine Commandos
# are still in their landing craft. A tile holds one military and one civilian unit (generals are civilians).

START = [
    # ----- the assault forces' headquarters ships, anchored in the Transport Area (each fleet city's tile)
    ("Allies", "HQSHIP", "USS Bayfield", 49.500, -1.070),
    ("Allies", "HQSHIP", "USS Ancon", 49.468, -0.880),
    ("Allies", "HQSHIP", "HMS Bulolo", 49.438, -0.560),
    ("Allies", "HQSHIP", "HMS Hilary", 49.432, -0.432),
    ("Allies", "HQSHIP", "HMS Largs", 49.398, -0.282),
    # ----- US airborne, Cotentin
    ("Allies", "USPARA", "505th Parachute Infantry", 49.408, -1.317),
    ("Allies", "USGEN", "Matthew B. Ridgway", 49.408, -1.317),
    ("Allies", "USPARA", "507th Parachute Infantry", 49.412, -1.392, 70),
    ("Allies", "USPARA", "508th Parachute Infantry", 49.383, -1.378, 70),
    ("Allies", "USGEN", "James M. Gavin", 49.402, -1.345),
    ("Allies", "USPARA", "502nd Parachute Infantry", 49.428, -1.248),
    ("Allies", "USPARA", "506th Parachute Infantry", 49.372, -1.230),
    ("Allies", "USPARA", "501st Parachute Infantry", 49.336, -1.228, 80),
    ("Allies", "USGEN", "Maxwell D. Taylor", 49.372, -1.230),
    # ----- British 6th Airborne, east of the Orne
    ("Allies", "BRPARA", "Ox and Bucks Coup de Main (Howard)", 49.242, -0.274),
    ("Allies", "BRPARA", "5th Parachute Brigade (Poett)", 49.229, -0.252),
    ("Allies", "BRGEN", "Richard N. Gale", 49.229, -0.252),
    ("Allies", "BRPARA", "9th Parachute Battalion (Otway)", 49.262, -0.214, 45),
    ("Allies", "BRPARA", "1st Canadian Parachute Battalion", 49.246, -0.160, 80),
    ("Allies", "BRPARA", "8th Parachute Battalion (Pearson)", 49.192, -0.196, 80),
    ("Allies", "BRGEN", "James Hill", 49.246, -0.160),
    # ----- Utah Beach: the first wave has touched down (H-Hour 6:30)
    ("Allies", "USINF", "8th Infantry (Van Fleet)", 49.399, -1.176),
    ("Allies", "USGEN", "Theodore Roosevelt Jr.", 49.399, -1.176),
    ("Allies", "ENG", "1st Engineer Special Brigade", 49.381, -1.176),
    ("Allies", "DD", "70th Tank Battalion (DD)", 49.396, -1.150),
    ("Allies", "BB", "USS Nevada", 49.448, -1.118),
    ("Allies", "DES", "USS Corry", 49.470, -1.200, 60),
    # ----- Pointe du Hoc: the Ranger Group in its landing craft under the cliffs
    ("Allies", "RANGER", "2nd Ranger Battalion (Rudder)", 49.408, -0.992),
    ("Allies", "DES", "USS Satterlee", 49.425, -1.000),
    # ----- Omaha Beach
    ("Allies", "USINF", "116th Infantry (29th Division)", 49.372, -0.913),
    ("Allies", "USINF", "16th Infantry (1st Division)", 49.354, -0.865),
    ("Allies", "SHERMAN", "743rd Tank Battalion", 49.345, -0.842),
    ("Allies", "DD", "741st Tank Battalion (DD)", 49.360, -0.835, 30),
    ("Allies", "ENG", "Special Engineer Task Force", 49.372, -0.880),
    ("Allies", "BB", "USS Texas", 49.425, -0.925),
    ("Allies", "BB", "USS Arkansas", 49.415, -0.835),
    # ----- Gold Beach (H-Hour 7:25)
    ("Allies", "BRINF", "231st Brigade (Stanier)", 49.327, -0.603),
    ("Allies", "BRINF", "69th Brigade (Knox)", 49.327, -0.555),
    ("Allies", "AVRE", "6th Assault Regiment RE (AVREs)", 49.336, -0.531),
    ("Allies", "DD", "4th/7th Royal Dragoon Guards (DD)", 49.345, -0.545),
    ("Allies", "CDO", "47 Royal Marine Commando", 49.350, -0.627),
    ("Allies", "CRU", "HMS Ajax", 49.385, -0.690),
    # ----- Juno Beach (H-Hour 7:45)
    ("Allies", "CDNINF", "7th Canadian Brigade (Foster)", 49.336, -0.484),
    ("Allies", "CDNINF", "8th Canadian Brigade (Blackader)", 49.336, -0.436),
    ("Allies", "SHERMAN", "Fort Garry Horse", 49.327, -0.508),
    ("Allies", "DD", "1st Hussars (DD)", 49.348, -0.460),
    ("Allies", "CDO", "48 Royal Marine Commando", 49.342, -0.405),
    ("Allies", "CRU", "HMS Belfast", 49.392, -0.425),
    # ----- Sword Beach (H-Hour 7:25)
    ("Allies", "BRINF", "8th Brigade (Cass)", 49.282, -0.293),
    ("Allies", "AVRE", "5th Assault Regiment RE (AVREs)", 49.300, -0.341),
    ("Allies", "CDO", "41 Royal Marine Commando", 49.309, -0.364),
    ("Allies", "CDO", "No. 4 Commando and Kieffer's French Commandos", 49.273, -0.269),
    ("Allies", "DD", "13th/18th Royal Hussars (DD)", 49.300, -0.300),
    ("Allies", "BB", "HMS Warspite", 49.352, -0.235),
    ("Allies", "BB", "HMS Ramillies", 49.365, -0.300),

    # ----- German 709th Division and 91st Air Landing Division, Cotentin
    ("Germany", "COAST", "919th Grenadier Regiment (WN 5)", 49.408, -1.199),
    ("Germany", "COAST", "919th Grenadier Regiment (Saint-Marcouf)", 49.455, -1.252),
    ("Germany", "BATT", "Crisbecq Battery", 49.474, -1.279),
    ("Germany", "GART", "Brécourt Manor Guns", 49.390, -1.199),
    ("Germany", "OST", "795th Georgian Battalion", 49.397, -1.268),
    ("Germany", "GREN", "1058th Grenadier Regiment (91st Division)", 49.442, -1.330),
    ("Germany", "GREN", "1057th Grenadier Regiment (91st Division)", 49.400, -1.430),
    ("Germany", "GGEN", "Wilhelm Falley", 49.383, -1.420),
    ("Germany", "GART", "191st Artillery Regiment (91st Division)", 49.360, -1.330),
    ("Germany", "FJ", "6th Fallschirmjaeger Regiment (von der Heydte)", 49.333, -1.270),
    ("Germany", "FJ", "III Battalion, 6th Fallschirmjaeger", 49.303, -1.248),
    ("Germany", "GGEN", "Friedrich von der Heydte", 49.333, -1.270),
    # ----- German 352nd Division: Isigny, Pointe du Hoc, Omaha
    ("Germany", "COAST", "Pointe du Hoc Garrison", 49.399, -0.985),
    ("Germany", "BATT", "Pointe du Hoc Guns", 49.381, -0.985),
    ("Germany", "GREN", "914th Grenadier Regiment", 49.350, -1.050),
    ("Germany", "COAST", "726th Grenadier Regiment (WN 66)", 49.363, -0.889),
    ("Germany", "GREN", "916th Grenadier Regiment (Vierville)", 49.363, -0.937),
    ("Germany", "GREN", "916th Grenadier Regiment (Colleville)", 49.345, -0.889),
    ("Germany", "GART", "352nd Artillery (Pluskat)", 49.336, -0.840),
    ("Germany", "GART", "352nd Artillery Regiment", 49.336, -0.913),
    ("Germany", "GREN", "Kampfgruppe Meyer (915th Grenadier)", 49.290, -1.060),
    ("Germany", "STUG", "352nd Panzerjaeger Battalion", 49.260, -0.880),
    ("Germany", "GGEN", "Dietrich Kraiss", 49.245, -0.870),
    ("Germany", "COAST", "726th Grenadier Regiment (Port-en-Bessin)", 49.345, -0.746),
    ("Germany", "BATT", "Longues Battery", 49.345, -0.698),
    # ----- German 716th Division: Gold, Juno, Sword
    ("Germany", "COAST", "726th Grenadier Regiment (Le Hamel)", 49.336, -0.579),
    ("Germany", "OST", "441st Ost Battalion", 49.318, -0.531),
    ("Germany", "COAST", "736th Grenadier Regiment (Courseulles)", 49.327, -0.460),
    ("Germany", "COAST", "736th Grenadier Regiment (Saint-Aubin)", 49.327, -0.412),
    ("Germany", "COAST", "Douvres Radar Station", 49.287, -0.400),
    ("Germany", "COAST", "736th Grenadier Regiment (WN 20)", 49.291, -0.317, 60),
    ("Germany", "COAST", "736th Grenadier Regiment (Hillman)", 49.273, -0.317),
    ("Germany", "OST", "642nd Ost Battalion", 49.264, -0.293),
    ("Germany", "BATT", "Merville Battery", 49.271, -0.197, 35),
    ("Germany", "GART", "1716th Artillery Regiment", 49.273, -0.364),
    ("Germany", "COAST", "716th Division Reserve", 49.183, -0.370),
    ("Germany", "GGEN", "Wilhelm Richter", 49.183, -0.370),
    # ----- German 21st Panzer Division, around Caen
    ("Germany", "PZGREN", "125th Panzergrenadier Regiment (von Luck)", 49.208, -0.215),
    ("Germany", "GGEN", "Hans von Luck", 49.208, -0.215),
    ("Germany", "PZGREN", "192nd Panzergrenadier Regiment (Rauch)", 49.205, -0.405),
    ("Germany", "STUG", "200th Assault Gun Battalion (Becker)", 49.200, -0.300),
    # ----- LXXXIV Corps headquarters
    ("Germany", "GGEN", "Erich Marcks", 49.116, -1.091),
    ("Germany", "GREN", "LXXXIV Corps Reserve", 49.116, -1.091),
]

# ---------------------------------------------------------------- arrivals
# (turn, side, entry, type key, [instance names]) - one list entry per unit, appearing at the START of the turn.
# Allied waves appear at their fleet, embarked, about five hexes out, so they land a turn or two later - unless the
# beach is already in Allied hands, when they come ashore there.
# Rule: a given (side, unit type, turn) may only arrive at ONE entry, because the unit names for each turn are drawn
# from one shared name group.

ARRIVALS = [
    # ===== June 6, D-Day
    # Utah
    (1, "Allies", "Force U", "USINF", ["22nd Infantry (Tribolet)"]),
    (2, "Allies", "Force U", "USGEN", ["Raymond O. Barton"]),
    (3, "Allies", "Force U", "USINF", ["12th Infantry (Reeder)"]),
    (4, "Allies", "Force U", "SHERMAN", ["746th Tank Battalion"]),
    (5, "Allies", "Force U", "USART", ["4th Division Artillery"]),
    (8, "Allies", "Force U", "M10", ["899th Tank Destroyer Battalion"]),
    (10, "Allies", "Force U", "USINF", ["359th Infantry (90th Division)"]),
    (12, "Allies", "Force U", "MED", [None]),
    # Omaha
    (1, "Allies", "Force O", "RANGER", ["5th Ranger Battalion (Schneider)"]),
    (1, "Allies", "Force O", "USGEN", ["Norman D. Cota"]),
    (2, "Allies", "Force O", "USINF", ["18th Infantry (1st Division)"]),
    (3, "Allies", "Force O", "DES", ["USS McCook", "USS Carmick"]),
    (4, "Allies", "Force O", "USINF", ["115th Infantry (29th Division)"]),
    (6, "Allies", "Force O", "USART", ["7th Field Artillery (1st Division)"]),
    (7, "Allies", "Force O", "ENG", ["5th Engineer Special Brigade"]),
    (8, "Allies", "Force O", "USINF", ["26th Infantry (1st Division)"]),
    (9, "Allies", "Force O", "USGEN", ["Charles H. Gerhardt"]),
    (11, "Allies", "Force O", "USART", ["29th Division Artillery"]),
    (13, "Allies", "Force O", "USGEN", ["Leonard T. Gerow"]),
    (14, "Allies", "Force O", "SHERMAN", ["745th Tank Battalion"]),
    # Gold
    (2, "Allies", "Force G", "SHERMAN", ["Sherwood Rangers Yeomanry"]),
    (3, "Allies", "Force G", "BRINF", ["151st Brigade (Senior)"]),
    (3, "Allies", "Force G", "BRGEN", ["Douglas Graham"]),
    (4, "Allies", "Force G", "BRINF", ["56th Brigade (Pepper)"]),
    (5, "Allies", "Force G", "BRART", ["50th Division Artillery"]),
    (6, "Allies", "Force G", "SHERMAN", ["24th Lancers"]),
    (7, "Allies", "Force G", "MED", [None]),
    (9, "Allies", "Force G", "AT", ["102nd Anti-Tank Regiment"]),
    # Juno
    (2, "Allies", "Force J", "BRGEN", ["Rod Keller"]),
    (3, "Allies", "Force J", "CDNINF", ["9th Canadian Brigade (Cunningham)"]),
    (4, "Allies", "Force J", "BRART", ["3rd Canadian Division Artillery"]),
    (5, "Allies", "Force J", "SHERMAN", ["Sherbrooke Fusiliers"]),
    (8, "Allies", "Force J", "AT", ["3rd Canadian Anti-Tank Regiment"]),
    (10, "Allies", "Force J", "ENG", ["Royal Canadian Engineers"]),
    # Sword
    (1, "Allies", "Force S", "CDO", ["1st Special Service Brigade (Lovat)"]),
    (1, "Allies", "Force S", "BRGEN", ["Lord Lovat"]),
    (2, "Allies", "Force S", "BRINF", ["185th Brigade (Smith)"]),
    (2, "Allies", "Force S", "FIREFLY", ["Staffordshire Yeomanry"]),
    (4, "Allies", "Force S", "BRGEN", ["Tom Rennie"]),
    (5, "Allies", "Force S", "BRINF", ["9th Brigade (Cunningham)"]),
    (6, "Allies", "Force S", "BRART", ["3rd Division Artillery"]),
    (7, "Allies", "Force S", "SHERMAN", ["East Riding Yeomanry"]),
    (11, "Allies", "Force S", "AT", ["20th Anti-Tank Regiment"]),
    # Airborne reinforcements, evening of D-Day: Operations Mallard and Elmira
    (15, "Allies", "Pegasus Bridge", "BRPARA", ["1st Royal Ulster Rifles", "2nd Ox and Bucks Light Infantry"]),
    (15, "Allies", "Sainte-Mère-Église", "USART", ["319th and 320th Glider Field Artillery"]),

    # ----- Germans, D-Day
    (1, "Germany", "Saint-Lô", "GREN", ["352nd Fusilier Battalion"]),
    (2, "Germany", "Falaise Road", "PZIV", ["22nd Panzer Regiment (I Battalion)"]),
    (2, "Germany", "Falaise Road", "GGEN", ["Hermann von Oppeln-Bronikowski"]),
    (3, "Germany", "Falaise Road", "PZIV", ["22nd Panzer Regiment (II Battalion)"]),
    (3, "Germany", "Valognes Road", "GGEN", ["Karl-Wilhelm von Schlieben"]),
    (4, "Germany", "Valognes Road", "GREN", ["Sturm-Bataillon AOK 7 (Messerschmidt)"]),
    (5, "Germany", "Falaise Road", "GGEN", ["Edgar Feuchtinger"]),
    (6, "Germany", "Falaise Road", "GART", ["155th Panzer Artillery Regiment"]),
    (7, "Germany", "Falaise Road", "FLAK", ["Panzerjaeger-Abteilung 200 (88s)"]),
    (6, "Germany", "Saint-Lô", "GREN", ["Schnelle Brigade 30"]),
    (7, "Germany", "Saint-Lô", "WERFER", ["Werfer-Regiment 84"]),
    (4, "Germany", "Falaise Road", "PZGREN", ["21st Panzer Reconnaissance Battalion"]),
    (8, "Germany", "Lisieux Road", "GREN", ["744th Grenadier Regiment (711th Division)"]),
    (10, "Germany", "Saint-Lô", "STUG", ["Sturmgeschuetz-Brigade 902"]),
    (9, "Germany", "Valognes Road", "STUG", ["Sturmgeschuetz-Abteilung 7"]),
    (12, "Germany", "Saint-Lô", "PION", [None]),
    (14, "Germany", "Lisieux Road", "GART", ["1711th Artillery Regiment"]),

    # ===== June 7
    (19, "Allies", "Force U", "USGEN", ["J. Lawton Collins"]),
    (19, "Allies", "Force O", "USINF", ["175th Infantry (29th Division)"]),
    (19, "Allies", "Force G", "BRGEN", ["Gerard Bucknall"]),
    (19, "Allies", "Sainte-Mère-Église", "USPARA", ["325th Glider Infantry"]),
    (20, "Allies", "Force G", "CROMWELL", ["22nd Armoured Brigade (7th Armoured)"]),
    (20, "Allies", "Force O", "SHERMAN", ["747th Tank Battalion"]),
    (20, "Allies", "Force U", "USPARA", ["327th Glider Infantry"]),
    (20, "Allies", "Force S", "CDO", ["46 Royal Marine Commando"]),
    (20, "Allies", "Force J", "BRGEN", ["John Crocker"]),
    (21, "Allies", "Force U", "USINF", ["357th Infantry (90th Division)"]),
    (21, "Allies", "Force G", "BRGEN", ["G. W. E. J. Erskine"]),
    (21, "Allies", "Force J", "BRINF", ["153rd Brigade (51st Highland)"]),
    (22, "Allies", "Force O", "USINF", ["9th Infantry (2nd Division)"]),
    (22, "Allies", "Force G", "CROMWELL", ["8th King's Royal Irish Hussars"]),
    (23, "Allies", "Force U", "USINF", ["358th Infantry (90th Division)"]),
    (23, "Allies", "Force G", "BRINF", ["131st Brigade (7th Armoured)"]),
    (24, "Allies", "Force O", "USINF", ["38th Infantry (2nd Division)"]),
    (24, "Allies", "Force S", "BRINF", ["152nd Brigade (51st Highland)"]),
    (25, "Allies", "Force U", "USART", ["90th Division Artillery"]),
    (25, "Allies", "Force O", "M10", ["635th Tank Destroyer Battalion"]),

    (19, "Germany", "Falaise Road", "PZGREN", ["25th SS Panzergrenadier Regiment (Meyer)"]),
    (19, "Germany", "Falaise Road", "GGEN", ["Kurt Meyer"]),
    (19, "Germany", "Valognes Road", "GREN", ["739th Grenadier Regiment (709th Division)"]),
    (20, "Germany", "Falaise Road", "PZIV", ["12th SS Panzer Regiment (II Battalion)"]),
    (20, "Germany", "Saint-Lô", "GREN", ["Kampfgruppe Heintz (275th Division)"]),
    (21, "Germany", "Lisieux Road", "GREN", ["857th Grenadier Regiment (346th Division)"]),
    (21, "Germany", "Falaise Road", "GART", ["12th SS Artillery Regiment"]),
    (21, "Germany", "Falaise Road", "FLAK", ["12th SS Flak Battalion (88s)"]),
    (22, "Germany", "Falaise Road", "GGEN", ["Fritz Witt"]),
    (22, "Germany", "Saint-Lô", "FLAK", ["Flak-Sturm-Regiment 1"]),
    (23, "Germany", "Falaise Road", "GGEN", ["Sepp Dietrich"]),
    (24, "Germany", "Valognes Road", "GART", ["1709th Artillery Regiment"]),
    (24, "Germany", "Falaise Road", "PZGREN", ["12th SS Reconnaissance Battalion (Bremer)"]),
    (25, "Germany", "Saint-Lô", "GREN", ["77th Infantry Division (advance guard)"]),
    (26, "Germany", "Falaise Road", "PION", ["12th SS Pioneer Battalion"]),

    # ===== June 8
    (30, "Allies", "Force O", "USINF", ["23rd Infantry (2nd Division)"]),
    (30, "Allies", "Force G", "BRGEN", ["Bernard L. Montgomery"]),
    (30, "Allies", "Force J", "BRART", ["I Corps Artillery"]),
    (31, "Allies", "Force G", "CROMWELL", ["11th Hussars"]),
    (31, "Allies", "Force O", "USART", ["2nd Division Artillery"]),
    (32, "Allies", "Force S", "BRGEN", ["Miles Dempsey"]),
    (32, "Allies", "Force U", "USART", ["VII Corps Artillery"]),
    (33, "Allies", "Force J", "SHERMAN", ["4th Armoured Brigade"]),

    (30, "Germany", "Falaise Road", "PZGREN", ["26th SS Panzergrenadier Regiment (Mohnke)"]),
    (30, "Germany", "Villers-Bocage", "GGEN", ["Fritz Bayerlein"]),
    (31, "Germany", "Falaise Road", "PANTHER", ["12th SS Panzer Regiment (I Battalion)"]),
    (31, "Germany", "Villers-Bocage", "PZGREN", ["901st Panzergrenadier-Lehr Regiment"]),
    (31, "Germany", "Lisieux Road", "GREN", ["858th Grenadier Regiment (346th Division)"]),
    (32, "Germany", "Villers-Bocage", "PZIV", ["Panzer-Lehr Regiment 130 (II Battalion)"]),
    (32, "Germany", "Falaise Road", "WERFER", ["12th SS Werfer Battalion"]),
    (33, "Germany", "Villers-Bocage", "PANTHER", ["Panzer Regiment 6 (I Battalion)"]),
    (33, "Germany", "Saint-Lô", "GREN", ["3rd Fallschirmjaeger Division (advance guard)"]),
    (34, "Germany", "Villers-Bocage", "PZGREN", ["902nd Panzergrenadier-Lehr Regiment"]),
    (35, "Germany", "Villers-Bocage", "GART", ["Panzer-Lehr Artillery Regiment 130"]),
    (30, "Germany", "Valognes Road", "GREN", ["922nd Grenadier Regiment (243rd Division)"]),
    (36, "Germany", "Villers-Bocage", "STUG", ["Panzerjaeger-Lehr-Abteilung 130"]),
]

# Unciv starts a scenario from the New Game screen by running the first player's turn start once with the turn counter
# at 1, then setting the counter back to 0 (NewGameScreen.startNewGame). Anything due on turn 1 would arrive twice, so
# the arrivals due by OPENING_TURN start on the map instead, at their entry point (the Allied ones in their landing
# craft beside their fleet). START_LISTED is the START list as written above.
OPENING_TURN = 1
_ENTRY_POS = {e[0]: (e[2], e[3]) for e in ENTRIES}
OPENING = [(side, key, name) + _ENTRY_POS[entry] for turn, side, entry, key, names in ARRIVALS if turn <= OPENING_TURN
           for name in names]
START_LISTED = START
START = START_LISTED + OPENING
ARRIVALS = [a for a in ARRIVALS if a[0] > OPENING_TURN]

# Free-play name pools for generals (used outside the scenario)
FREE_PLAY_GENERALS = {
    "Allies": ["Bernard L. Montgomery", "Omar N. Bradley", "Miles Dempsey", "J. Lawton Collins", "Leonard T. Gerow",
               "Matthew B. Ridgway", "Maxwell D. Taylor", "James M. Gavin", "Theodore Roosevelt Jr.", "Norman D. Cota",
               "Clarence R. Huebner", "Raymond O. Barton", "Charles H. Gerhardt", "Richard N. Gale", "John Crocker",
               "Gerard Bucknall", "Rod Keller", "Tom Rennie", "Douglas Graham", "Lord Lovat", "James Hill",
               "G. W. E. J. Erskine"],
    "Germany": ["Erwin Rommel", "Erich Marcks", "Friedrich Dollmann", "Dietrich Kraiss", "Wilhelm Richter",
                "Karl-Wilhelm von Schlieben", "Wilhelm Falley", "Friedrich von der Heydte", "Edgar Feuchtinger",
                "Hans von Luck", "Hermann von Oppeln-Bronikowski", "Kurt Meyer", "Fritz Witt", "Fritz Bayerlein",
                "Sepp Dietrich"],
}
US_GENERALS = {"Matthew B. Ridgway", "James M. Gavin", "Maxwell D. Taylor", "Theodore Roosevelt Jr.",
               "Raymond O. Barton", "Norman D. Cota", "Charles H. Gerhardt", "Leonard T. Gerow", "J. Lawton Collins",
               "Clarence R. Huebner", "Omar N. Bradley"}


def check():
    """Sanity checks on the order of battle and timetable. Returns the set of unit names."""
    entries = {e[0]: e for e in ENTRIES}
    seen, names = {}, set()
    for row in ARRIVALS:
        turn, side, entry, key, inst = row
        assert key in (A if side == "Allies" else G), (side, key)
        assert entry in entries and entries[entry][1] == side, (entry, side)
        if key in NAVAL_KEYS:
            assert entries[entry][5] == "fleet", ("ships arrive at a fleet", row)
        k = (side, key, turn)
        if k in seen and seen[k] != entry:
            raise ValueError("%s arrives at two entries on turn %d" % (k, turn))
        seen[k] = entry
        for n in inst:
            if n is None:
                continue
            assert n not in names, "duplicate name " + n
            names.add(n)
        assert OPENING_TURN < turn <= LAST_TURN, row
    for s in START:
        side, key, inst = s[0], s[1], s[2]
        assert key in (A if side == "Allies" else G), (side, key)
        assert inst not in names, inst
        names.add(inst)
    for o in OBJECTIVES:
        assert o[2] in SIDES, o
    assert set(BEACH_OF_FLEET) == set(FLEETS) and set(BEACH_OF_FLEET.values()) == set(BEACHES)
    return names


if __name__ == "__main__":
    n = check()
    print("OK - %d named units, %d arrival lines" % (len(n), len(ARRIVALS)))
    for side in SIDES:
        start = sum(1 for s in START if s[0] == side)
        later = sum(len(a[4]) for a in ARRIVALS if a[1] == side)
        print("%-8s %3d units: %3d on the field at the start, %3d arriving" % (side, start + later, start, later))
    for t in (0, 1, 16, 17, 18, 19, 27, 28, 29, 30, 38):
        print("  turn %2d: %s" % (t, turn_label(t)))
