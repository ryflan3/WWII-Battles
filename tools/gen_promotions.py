"""Generates jsons/UnitPromotions.json.

Two kinds of promotions:
  * promotions that units earn in combat (per arm of service),
  * personal abilities of named commanders. Unciv automatically grants a promotion whose name equals the name a unit
    receives from a UnitNameGroup, so 'Norman D. Cota' gets his. The scenario builder grants them to commanders on the
    field at the start.
Run from the repository root:  python3 tools/gen_promotions.py
"""
import json, os

INF, AIR, ARM, AT, ART, FORT, SEA = "Infantry", "Airborne", "Armor", "Anti-Tank", "Artillery", "Fortification", "Warship"
FOOT = [INF, AIR]
ALL = [INF, AIR, ARM, AT, ART, FORT, SEA]


def p(name, uniques, types, col, row, prereq=None, text=None):
    d = {"name": name, "uniques": uniques, "unitTypes": types, "column": col, "row": row}
    if prereq:
        d["prerequisites"] = prereq
    if text:
        d["civilopediaText"] = [{"text": text}]
    return d


PROMOS = [
    p("Rally", ["[This Unit] heals [50] HP", "Doing so will consume this opportunity to choose a Promotion"], ALL, 0, 0,
      text="Replacements come forward, the wounded are evacuated and the survivors are reorganised."),

    # infantry and airborne
    p("Dug In I", ["[+15]% Strength <when defending>"], FOOT + [AT], 1, 1, text="Slit trenches, fields of fire and wire."),
    p("Dug In II", ["[+15]% Strength <when defending>"], FOOT + [AT], 1, 2, ["Dug In I"]),
    p("Dug In III", ["[+15]% Strength <when defending>"], FOOT + [AT], 1, 3, ["Dug In II"]),
    p("Assault I", ["[+15]% Strength <when attacking>"], FOOT, 2, 1, text="Fire and movement: one section pins the enemy down while the other works round his flank."),
    p("Assault II", ["[+15]% Strength <when attacking>"], FOOT, 2, 2, ["Assault I"]),
    p("Assault III", ["[+15]% Strength <when attacking>"], FOOT, 2, 3, ["Assault II"]),
    p("Hedgerow Fighting", ["[+20]% Strength <when fighting in [Rough terrain] tiles>"], FOOT, 3, 1,
      text="Every field in the bocage was a fortress: banks of earth topped with hedges, entered only by a gate the "
           "enemy had already covered. Units learned to blast holes in the banks and clear one field at a time."),
    p("Street Fighting", ["[+25]% Strength <vs cities>"], FOOT, 3, 2, ["Hedgerow Fighting"],
      text="Clearing a town house by house, going through the walls rather than down the street."),
    p("Bazooka Teams", ["[+33]% Strength <vs [Armor] units>"], FOOT, 4, 1,
      text="Bazookas, PIATs and Panzerfausts: infantry that can stand up to tanks."),
    p("Forced March", ["[+1] Movement"], FOOT, 4, 2, ["Dug In I", "Assault I"],
      text="Fit, hardened troops who can march all night and fight at dawn."),
    p("Veterans", ["No damage penalty for wounded units"], FOOT + [ARM], 5, 3, ["Dug In II", "Assault II", "Gunnery II"],
      text="Units that keep fighting at half strength without breaking."),
    p("Battalion Aid Station", ["All adjacent units heal [+5] HP when healing"], FOOT, 5, 1, ["Dug In I", "Assault I"]),

    # armour
    p("Gunnery I", ["[+15]% Strength <when attacking>"], [ARM], 6, 1, text="Fast, accurate tank gunnery: the first hit wins."),
    p("Gunnery II", ["[+15]% Strength <when attacking>"], [ARM], 6, 2, ["Gunnery I"]),
    p("Gunnery III", ["[+15]% Strength <when attacking>"], [ARM], 6, 3, ["Gunnery II"]),
    p("Hull Down", ["[+25]% Strength <when defending>"], [ARM], 7, 1, text="Firing from behind a crest or a bank with only the turret showing."),
    p("Tank Killers", ["[+25]% Strength <vs [Armor] units>"], [ARM, AT], 7, 2, ["Gunnery I"]),
    p("Exploitation", ["[+1] Movement"], [ARM], 7, 3, ["Gunnery II"], text="Pushing through the gap before the enemy can close it."),
    p("Infantry Support", ["[+25]% Strength <vs [Infantry] units>"], [ARM], 8, 1,
      text="Tanks and infantry trained together, the tanks shooting the infantry onto their objectives."),

    # artillery and coast batteries
    p("Fire Direction I", ["[+15]% Strength <when attacking>"], [ART, FORT], 9, 1, text="Forward observers with radios, and a fire direction centre that plots every shot."),
    p("Fire Direction II", ["[+15]% Strength <when attacking>"], [ART, FORT], 9, 2, ["Fire Direction I"]),
    p("Fire Direction III", ["[+15]% Strength <when attacking>"], [ART, FORT], 9, 3, ["Fire Direction II"]),
    p("Counter-Battery", ["[+33]% Strength <vs [Artillery] units>"], [ART, FORT], 10, 1, ["Fire Direction I"]),
    p("Air Observation Post", ["[+1] Sight"], [ART], 10, 2, ["Fire Direction I"],
      text="Little Auster and Piper Cub spotter planes, flown by artillery officers, adjusting fire from above."),
    p("Long Range", ["[+1] Range"], [ART, FORT, SEA], 10, 3, ["Fire Direction III", "Naval Gunfire II"]),
    p("Shoot and Scoot", ["Can move after attacking"], [ART], 11, 2, ["Fire Direction II"], text="Fire, limber up and move before the counter-battery fire lands."),

    # anti-tank guns
    p("Ambush", ["[+25]% Strength <when defending> <when fighting in [Rough terrain] tiles>"], [AT], 12, 1,
      text="Guns dug in behind a hedgerow, held until the tanks are a hundred yards away."),

    # warships
    p("Naval Gunfire I", ["[+20]% Strength <vs [Land] units>"], [SEA], 13, 1,
      text="Shore fire control parties landed with the assault troops call down the ships' guns by radio."),
    p("Naval Gunfire II", ["[+20]% Strength <vs [Land] units>"], [SEA], 13, 2, ["Naval Gunfire I"]),
    p("Damage Control", ["[+25]% Strength <when defending>", "[+10] HP when healing"], [SEA], 14, 1),
]


def g(name, uniques, text):
    return {"name": name, "uniques": uniques, "innerColor": [255, 255, 255], "outerColor": [60, 70, 50],
            "civilopediaText": [{"text": text}]}


MIL = "{Military} {Land}"


def aura(pct, filt, radius, cond=""):
    return "[+%d]%% Strength bonus for [%s] units within [%d] tiles%s" % (pct, filt, radius, (" " + cond) if cond else "")


GENERALS = [
    # ----- United States
    g("Matthew B. Ridgway", [aura(25, "Airborne", 2)],
      "Commanding the 82nd Airborne Division. He jumped with his men and spent D-Day in an orchard outside Sainte-Mère-Église, "
      "cut off from the beaches and from half his division. Airborne troops within 2 tiles get +25%."),
    g("James M. Gavin", [aura(25, MIL, 1), "[+1] Movement"],
      "'Jumping Jim', assistant commander of the 82nd Airborne, aged 37. He led the fight for the La Fière causeway over "
      "the Merderet in person, rifle in hand."),
    g("Maxwell D. Taylor", [aura(20, "Airborne", 2)],
      "Commanding the 101st Airborne Division ('Screaming Eagles'). Landing alone in a field, he gathered a scratch force of "
      "officers - 'Never were so few led by so many' - and took Pouppeville, the southern exit from Utah Beach."),
    g("Theodore Roosevelt Jr.", [aura(25, MIL, 2, "<when attacking>")],
      "Assistant commander of the 4th Division, 56 years old, the oldest man - and the only general - in the first wave. "
      "Finding the 8th Infantry had landed a mile south of its target, he walked the beach with his cane and decided: 'We'll "
      "start the war from right here!' He received the Medal of Honor and died of a heart attack five weeks later."),
    g("Raymond O. Barton", [aura(15, MIL, 2)],
      "Commanding the 4th Infantry Division, which landed on Utah Beach with fewer than 200 casualties."),
    g("Norman D. Cota", [aura(25, MIL, 1), "[+1] Movement"],
      "'Dutch' Cota, assistant commander of the 29th Division, landed on Omaha at 7:30 AM and walked the beach under fire "
      "rallying the pinned-down troops. To the 5th Rangers he said: 'Rangers, lead the way!' - and led them up the bluff."),
    g("Charles H. Gerhardt", [aura(15, MIL, 2)],
      "'Uncle Charlie', the exacting commander of the 29th Division ('Twenty-nine, let's go!'), who came ashore on Omaha in "
      "the evening of D-Day."),
    g("Clarence R. Huebner", [aura(20, MIL, 2, "<when defending>")],
      "Commanding the 1st Infantry Division - 'the Big Red One' - which had already made assault landings in North Africa "
      "and Sicily before Omaha."),
    g("Leonard T. Gerow", [aura(15, MIL, 3)],
      "Commanding V Corps at Omaha. At 1:30 PM he signalled Bradley: 'Troops formerly pinned down on beaches Easy Red, Easy "
      "Green, Fox Red advancing up heights behind beaches.'"),
    g("J. Lawton Collins", [aura(15, MIL, 3), "[+1] Movement"],
      "'Lightning Joe', commanding VII Corps at Utah Beach, the fastest-driving corps commander in the US Army."),
    g("Omar N. Bradley", [aura(20, MIL, 3)],
      "Commanding the US First Army. Watching Omaha from the cruiser Augusta, he considered diverting the follow-up waves "
      "to Utah and the British beaches."),
    # ----- Britain and Canada
    g("Bernard L. Montgomery", [aura(20, MIL, 3)],
      "Commanding the 21st Army Group - all Allied ground forces in Normandy. He came ashore on June 8 and set up his "
      "tactical headquarters at Creullet, near Creully."),
    g("Miles Dempsey", [aura(15, MIL, 3)],
      "Commanding the British Second Army, which landed the British and Canadian divisions on Gold, Juno and Sword."),
    g("John Crocker", [aura(15, MIL, 3)],
      "Commanding I Corps: the British 3rd and 3rd Canadian Divisions and the 6th Airborne."),
    g("Gerard Bucknall", [aura(15, MIL, 2)],
      "Commanding XXX Corps, whose 50th Division landed on Gold Beach."),
    g("G. W. E. J. Erskine", [aura(20, "Armor", 2)],
      "Commanding the 7th Armoured Division, the 'Desert Rats', veterans of El Alamein and Tunisia."),
    g("Douglas Graham", [aura(15, MIL, 2)],
      "Commanding the 50th (Northumbrian) Division on Gold Beach. By nightfall its patrols were on the edge of Bayeux."),
    g("Tom Rennie", [aura(15, MIL, 2)],
      "Commanding the British 3rd Division on Sword Beach, whose objective for D-Day was Caen."),
    g("Rod Keller", [aura(15, MIL, 2, "<when attacking>")],
      "Commanding the 3rd Canadian Division on Juno Beach. One Canadian troop of tanks reached the Caen-Bayeux railway, "
      "the deepest Allied penetration of D-Day."),
    g("Richard N. Gale", [aura(20, "Airborne", 2, "<when defending>")],
      "'Windy' Gale, commanding the 6th Airborne Division, landed by glider at 3:30 AM. His orders were to seize the Orne "
      "bridges and hold the left flank of the whole invasion."),
    g("James Hill", [aura(20, "Airborne", 2)],
      "Brigadier commanding the 3rd Parachute Brigade. Wounded in the night by a stray Allied bomb, he still made it to his "
      "headquarters and ran his brigade's battle: 'Gentlemen, in spite of your excellent orders and training, do not be "
      "daunted if chaos reigns. It undoubtedly will.'"),
    g("Lord Lovat", [aura(25, "Infantry", 1), "[+1] Movement"],
      "Brigadier Simon Fraser, Lord Lovat, commanding the 1st Special Service Brigade. He waded ashore on Sword with his "
      "piper, Bill Millin, playing, marched his commandos inland and reached Pegasus Bridge at 1:30 PM - 'two and a half "
      "minutes late'."),
    # ----- Germany
    g("Erich Marcks", [aura(20, MIL, 3, "<when defending>")],
      "Commanding LXXXIV Corps from Saint-Lô. One of the few German commanders who expected the landings in Normandy; on "
      "D-Day he was preparing a map exercise for the next morning. He had lost a leg in Russia and was killed by an Allied "
      "fighter-bomber on June 12."),
    g("Erwin Rommel", [aura(20, MIL, 3, "<when defending>")],
      "Field Marshal commanding Army Group B. He had spent five months fortifying the coast - 'the first twenty-four "
      "hours of the invasion will be decisive' - but on June 6 he was at home in Germany for his wife's birthday, and did "
      "not get back to his headquarters until evening."),
    g("Friedrich Dollmann", [aura(15, MIL, 3)],
      "Commanding the Seventh Army, which defended Normandy and Brittany."),
    g("Dietrich Kraiss", [aura(20, MIL, 2, "<when defending>")],
      "Commanding the 352nd Infantry Division, which held Omaha Beach and very nearly threw the Americans back into the sea."),
    g("Wilhelm Richter", [aura(15, MIL, 2, "<when defending>")],
      "Commanding the 716th Static Division, spread along 21 miles of coast from Gold to the Orne. By the end of D-Day it had "
      "practically ceased to exist."),
    g("Karl-Wilhelm von Schlieben", [aura(15, MIL, 2)],
      "Commanding the 709th Static Division in the Cotentin. He later surrendered Cherbourg on June 26."),
    g("Wilhelm Falley", [aura(15, MIL, 2)],
      "Commanding the 91st Air Landing Division. Driving back from Rennes in the night, he was ambushed by American "
      "paratroopers near Picauville and killed - the first German general to die in the invasion."),
    g("Friedrich von der Heydte", [aura(25, "Airborne", 2)],
      "Major commanding the 6th Fallschirmjäger Regiment. From the church tower of Saint-Côme-du-Mont he watched the "
      "invasion fleet lying off Utah Beach, then fought the 101st Airborne for Carentan."),
    g("Edgar Feuchtinger", [aura(15, "Armor", 2)],
      "Commanding the 21st Panzer Division - the only panzer division near the beaches. He was away in Paris on the night of "
      "June 5, and his division waited for hours for orders that came too late."),
    g("Hans von Luck", [aura(25, MIL, 1, "<when attacking>"), "[+1] Movement"],
      "Major commanding the 125th Panzergrenadier Regiment east of the Orne. He had his men ready from 1 AM but was forbidden "
      "to attack the British paratroopers without orders from above."),
    g("Hermann von Oppeln-Bronikowski", [aura(20, "Armor", 2)],
      "Colonel commanding the 22nd Panzer Regiment, a gold medallist in dressage at the 1936 Olympics. His tanks struck at "
      "the gap between Juno and Sword in the afternoon of D-Day."),
    g("Kurt Meyer", [aura(20, MIL, 2, "<when attacking>")],
      "Commanding the 25th SS Panzergrenadier Regiment of the 12th SS Panzer Division, which attacked the Canadians at Authie "
      "and Buron on June 7. After the war a Canadian military court convicted him of responsibility for the murder of "
      "Canadian prisoners by his troops."),
    g("Fritz Witt", [aura(15, MIL, 2)],
      "Commanding the 12th SS Panzer Division 'Hitlerjugend'. He was killed by naval gunfire at his headquarters on June 14."),
    g("Sepp Dietrich", [aura(15, MIL, 3)],
      "Commanding I SS Panzer Corps, sent to drive the British and Canadians back into the sea around Caen. A veteran Nazi "
      "party member, he was later convicted of war crimes for the Malmedy massacre of December 1944."),
    g("Fritz Bayerlein", [aura(20, "Armor", 2)],
      "Commanding the Panzer Lehr Division. Ordered to march by day on June 7, it lost scores of vehicles to Allied "
      "fighter-bombers on the road - the troops called it the 'fighter-bomber racetrack'."),
]

if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    names = [x["name"] for x in PROMOS + GENERALS]
    assert len(names) == len(set(names))
    with open(os.path.join(root, "jsons", "UnitPromotions.json"), "w") as f:
        json.dump(PROMOS + GENERALS, f, indent=4, ensure_ascii=False)
    print("Wrote %d promotions" % (len(PROMOS) + len(GENERALS)))
