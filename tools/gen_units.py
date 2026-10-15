"""Generates jsons/Units.json - the unit roster of the WWII Battles mod.

Stats are on Unciv's relative scale: a standard infantry regiment or brigade has Strength 20.
Only the ratios between strengths matter in Unciv combat.
Run from the repository root:  python3 tools/gen_units.py
"""
import json, os, sys


def pedia(*lines):
    return [{"text": l} for l in lines]


NAME_FROM = lambda u: "[This Unit] gets a name from the [%s] group" % u
# Once ashore, troops do not go back to the ships: a land unit can sail only while it is still at sea.
ASHORE = "Cannot embark <in [Land] tiles>"
AMPHIBIOUS = ["Eliminates combat penalty for attacking across a coast", "[1] Movement point cost to disembark"]
ANTI_TANK = lambda pct: "[+%d]%% Strength <vs [Armor] units>" % pct
AURA = "[+15]% Strength bonus for [{Military} {Land}] units within [2] tiles"
# as in Civ V: only from friendly territory - and never in the D-Day scenario, where the airborne have already dropped
PARADROP = "May Paradrop to [Land] tiles up to [5] tiles away <in [{Friendly} {Land}] tiles> <if [Normandy Scenario] is not constructed>"

UNITS = [
    # ------------------------------------------------------------------ generic base units (free play, any army)
    {"name": "Rifle Infantry", "unitType": "Infantry", "movement": 2, "strength": 20, "cost": 50, "attackSound": "shot",
     "civilopediaText": pedia(
        "An infantry regiment or brigade of about 3,000 men: three battalions of riflemen with machine guns, mortars "
        "and anti-tank weapons.",
        "Infantry took and held the ground. In Normandy the hedgerows, sunken lanes and stone farms gave defenders "
        "cover every few hundred yards, so attacks across the open were costly.",
        "Infantry can dig Foxholes.")},
    {"name": "Paratroopers", "unitType": "Airborne", "movement": 2, "strength": 21, "cost": 60, "attackSound": "shot",
     "uniques": [PARADROP, "Ignores Zone of Control"],
     "civilopediaText": pedia(
        "Lightly armed infantry who jump from transport aircraft or land in gliders behind the enemy's front.",
        "Scattered by the night drop, small groups fought their way to their objectives and held them until the "
        "seaborne troops arrived. Paratroopers slip past enemy positions (they ignore zones of control) and, from "
        "a city of their own, can be dropped up to five hexes away.")},
    {"name": "Medium Tank", "unitType": "Armor", "movement": 4, "strength": 30, "cost": 90, "attackSound": "tankshot",
     "civilopediaText": pedia(
        "A regiment or battalion of fifty-odd medium tanks.",
        "Tanks are fast and hit hard in open country, but the hedgerows hid anti-tank guns and infantry with "
        "Panzerfausts at a few yards' range.")},
    {"name": "Heavy Tank", "unitType": "Armor", "movement": 3, "strength": 40, "cost": 130, "attackSound": "tankshot",
     "civilopediaText": pedia("Heavily armoured tanks with long-barrelled high-velocity guns.")},
    {"name": "Tank Destroyer", "unitType": "Armor", "movement": 4, "strength": 26, "cost": 80, "attackSound": "tankshot",
     "uniques": [ANTI_TANK(50)],
     "civilopediaText": pedia("Self-propelled anti-tank guns, built to knock out tanks rather than to lead an assault.")},
    {"name": "Field Artillery", "unitType": "Artillery", "movement": 2, "strength": 10, "rangedStrength": 24, "range": 2,
     "cost": 70, "attackSound": "artillery",
     "uniques": ["Must set up to ranged attack"],
     "civilopediaText": pedia(
        "Battalions of 105mm howitzers or 25-pounder gun-howitzers firing at targets their forward observers can see.")},
    {"name": "Anti-Tank Gun", "unitType": "Anti-Tank", "movement": 2, "strength": 16, "cost": 50, "attackSound": "cannon",
     "uniques": [ANTI_TANK(100)],
     "civilopediaText": pedia("Towed anti-tank guns, dug in and camouflaged to ambush tanks at close range.")},
    {"name": "Destroyer", "unitType": "Warship", "movement": 6, "strength": 22, "rangedStrength": 20, "range": 2,
     "cost": 100, "attackSound": "shipguns",
     "civilopediaText": pedia(
        "Fast escorts with 4.7- or 5-inch guns. Off Omaha Beach on the morning of D-Day, a dozen American and British "
        "destroyers steamed in so close that their keels scraped the bottom and shot up the German strongpoints at "
        "point-blank range.")},
    {"name": "Cruiser", "unitType": "Warship", "movement": 5, "strength": 30, "rangedStrength": 26, "range": 3,
     "cost": 160, "attackSound": "shipCannonVolley",
     "civilopediaText": pedia("Light and heavy cruisers with six-inch or eight-inch guns.")},
    {"name": "Battleship", "unitType": "Warship", "movement": 4, "strength": 40, "rangedStrength": 30, "range": 3,
     "cost": 240, "attackSound": "shipCannonVolley",
     "civilopediaText": pedia(
        "Battleships and monitors with 14- and 15-inch guns. Their shells could reach twenty miles inland, and German "
        "counterattacks near the coast were broken up by naval gunfire again and again.")},
    {"name": "Headquarters Ship", "unitType": "Warship", "uniqueTo": "Allies", "movement": 0, "strength": 25, "cost": 200,
     "uniques": ["Unbuildable", "Cannot move", "Cannot attack"],
     "civilopediaText": pedia(
        "The command ship of an assault force, packed with radios and staff officers - USS Bayfield (Utah), USS Ancon "
        "(Omaha), HMS Bulolo (Gold), HMS Hilary (Juno), HMS Largs (Sword). From here the naval and army commanders "
        "ran the landings.",
        "It lies at anchor in its fleet's Transport Area for the whole battle and cannot move or fight.")},
    {"name": "General", "unitType": "Commander", "movement": 4,
     "uniques": [AURA, "[+1] Sight", "Can be earned through combat <for [Land] units>", "Is part of Great Person group [General]",
                 "Great Person - [War]", "Unbuildable", "Uncapturable"],
     "civilopediaText": pedia(
        "A corps or division commander with his staff, signallers and jeeps.",
        "A general inspires the troops near him (the best bonus in range applies; bonuses do not stack). Generals "
        "cannot be captured - if the enemy reaches one, he is lost.")},
    {"name": "Engineers", "unitType": "Infantry", "movement": 2, "strength": 16, "cost": 50, "attackSound": "shot",
     "uniques": ["[+50]% Strength <vs cities>", "Can build [Foxholes] improvements on tiles", "Can build [Road] improvements on tiles"],
     "civilopediaText": pedia(
        "Combat engineers with demolition charges, Bangalore torpedoes, mine detectors and bulldozers.",
        "They blew gaps in the beach obstacles and the wire, cleared the minefields and built the roads off the "
        "beaches. Engineers fight at +50% against cities and build Foxholes and Roads.")},
    {"name": "Medics", "unitType": "Support", "movement": 3, "cost": 40,
     "uniques": ["All adjacent units heal [+15] HP when healing"],
     "civilopediaText": pedia(
        "Aid men, stretcher bearers, ambulances and a field hospital. Adjacent units heal faster.")},
    {"name": "Supply Column", "unitType": "Support", "movement": 3, "cost": 70, "attackSound": "wagon",
     "uniques": ["Founds a new city"],
     "civilopediaText": pedia(
        "Trucks with ammunition, fuel and rations. It sets up a supply dump (a new city) where the army can raise and "
        "refit units.")},

    # ------------------------------------------------------------------ the Allies
    {"name": "US Infantry", "unitType": "Infantry", "uniqueTo": "Allies", "replaces": "Rifle Infantry",
     "movement": 2, "strength": 20, "cost": 50, "attackSound": "shot",
     "uniques": ["[+10]% Strength", NAME_FROM("US Infantry")],
     "civilopediaText": pedia(
        "An American infantry regiment, armed with the M1 Garand - the only semi-automatic rifle issued to a whole "
        "army - and the Browning Automatic Rifle: +10% Strength.",
        "On D-Day the 4th Division landed at Utah almost unopposed, while the 1st and 29th Divisions fought for six "
        "hours to get off Omaha Beach.")},
    {"name": "British Infantry", "unitType": "Infantry", "uniqueTo": "Allies", "movement": 2, "strength": 20, "cost": 50,
     "attackSound": "machinegun",
     "uniques": ["Unbuildable", "[+15]% Strength <when defending>", NAME_FROM("British Infantry")],
     "civilopediaText": pedia(
        "A British infantry brigade of three battalions, with Lee-Enfield rifles and the Bren light machine gun at the "
        "heart of every section. Steady and dogged in defence: +15% Strength when defending.",
        "The 50th (Northumbrian) Division landed on Gold Beach and the 3rd Division on Sword.")},
    {"name": "Canadian Infantry", "unitType": "Infantry", "uniqueTo": "Allies", "movement": 2, "strength": 20, "cost": 50,
     "attackSound": "shot",
     "uniques": ["Unbuildable", "[+15]% Strength <when attacking>", NAME_FROM("Canadian Infantry")],
     "civilopediaText": pedia(
        "A brigade of the 3rd Canadian Division - all volunteers. On D-Day they stormed the seafront towns of Juno "
        "Beach under heavy fire, and by evening their tanks had driven further inland than any other Allied force: "
        "+15% Strength when attacking.")},
    {"name": "US Rangers", "unitType": "Infantry", "uniqueTo": "Allies", "movement": 2, "strength": 23, "cost": 70,
     "attackSound": "shot",
     "uniques": ["Unbuildable", "[+20]% Strength <when attacking>", "[+33]% Strength <when fighting in [Cliffs] tiles>",
                 NAME_FROM("US Rangers")] + AMPHIBIOUS,
     "civilopediaText": pedia(
        "The 2nd and 5th Ranger Battalions, trained on the cliffs of the Isle of Wight. At 7:10 AM, three companies "
        "under Lt. Col. James Rudder fired rocket-propelled grapnels up the hundred-foot cliffs of Pointe du Hoc and "
        "climbed them under fire. 'Rangers, lead the way!' - General Cota's words to the 5th Rangers on Omaha Beach.",
        "Rangers land without penalty (they disembark for one movement point and attack from the sea at full "
        "strength) and fight at +33% on cliffs.")},
    {"name": "Commandos", "unitType": "Infantry", "uniqueTo": "Allies", "movement": 2, "strength": 22, "cost": 70,
     "attackSound": "shot",
     "uniques": ["Unbuildable", "[+25]% Strength <vs cities>", "Ignores Zone of Control", NAME_FROM("Commandos")] + AMPHIBIOUS,
     "civilopediaText": pedia(
        "British Army and Royal Marine Commandos in their green berets, and Commandant Philippe Kieffer's 177 Free "
        "French commandos, the only French troops to land on D-Day.",
        "Lord Lovat's 1st Special Service Brigade marched from Sword Beach to Pegasus Bridge behind his piper, Bill "
        "Millin; 47 Royal Marine Commando marched ten miles behind the German lines to take Port-en-Bessin. Commandos "
        "land without penalty, slip through enemy lines (they ignore zones of control) and fight at +25% against cities.")},
    {"name": "US Paratroopers", "unitType": "Airborne", "uniqueTo": "Allies", "replaces": "Paratroopers",
     "movement": 2, "strength": 21, "cost": 60, "attackSound": "shot",
     "uniques": [PARADROP, "Ignores Zone of Control", "[+10]% Strength <when defending>", NAME_FROM("US Paratroopers")],
     "civilopediaText": pedia(
        "Parachute and glider infantry regiments of the 82nd and 101st Airborne Divisions - 13,000 men dropped over "
        "the Cotentin in the night. Scattered across miles of hedgerows and flooded fields, they gathered in small "
        "bands with their 'cricket' clickers and took Sainte-Mère-Église, the Utah causeways and the Merderet bridges.")},
    {"name": "British Paratroopers", "unitType": "Airborne", "uniqueTo": "Allies", "movement": 2, "strength": 21,
     "cost": 60, "attackSound": "shot",
     "uniques": ["Unbuildable", PARADROP, "Ignores Zone of Control", "[+15]% Strength <when defending>",
                 NAME_FROM("British Paratroopers")],
     "civilopediaText": pedia(
        "The 6th Airborne Division - the 'Red Devils' of the 3rd and 5th Parachute Brigades and the 6th Airlanding "
        "Brigade - with the 1st Canadian Parachute Battalion. They seized the Orne bridges, silenced the Merville "
        "battery, blew the Dives bridges and held the high ground east of the Orne against every counterattack.")},
    {"name": "Sherman", "unitType": "Armor", "uniqueTo": "Allies", "replaces": "Medium Tank", "movement": 4,
     "strength": 27, "cost": 90, "attackSound": "tankshot",
     "uniques": ["[+10]% Strength <vs [Infantry] units>", NAME_FROM("Sherman")],
     "civilopediaText": pedia(
        "The M4 Sherman, the Allies' standard tank: reliable, fast and easy to repair, with a 75mm gun that fired a "
        "good high-explosive shell against infantry and guns (+10% vs infantry) but struggled against the front armour "
        "of the Panther.")},
    {"name": "DD Sherman", "unitType": "Armor", "uniqueTo": "Allies", "movement": 4, "strength": 24, "cost": 90,
     "attackSound": "tankshot",
     "uniques": ["Unbuildable", NAME_FROM("DD Sherman")] + AMPHIBIOUS,
     "civilopediaText": pedia(
        "Duplex Drive 'swimming' Shermans, one of Major General Percy Hobart's 'Funnies': a canvas screen raised round "
        "the hull kept the tank afloat while two propellers drove it ashore from miles out.",
        "Off Utah the 70th Tank Battalion's DD tanks were launched close in and nearly all landed. Off Omaha, launched "
        "far out into a heavy sea, 27 of the 741st Tank Battalion's 32 tanks sank. Afloat, a DD Sherman is as "
        "helpless as any landing craft; once ashore it drops its screen, fights as a Sherman and cannot go back to sea.")},
    {"name": "Sherman Firefly", "unitType": "Armor", "uniqueTo": "Allies", "movement": 4, "strength": 30, "cost": 100,
     "attackSound": "tankshot",
     "uniques": ["Unbuildable", ANTI_TANK(50), NAME_FROM("Sherman Firefly")],
     "civilopediaText": pedia(
        "A British Sherman rearmed with the long 17-pounder gun, the only Allied tank gun that could reliably knock out "
        "a Panther or a Tiger: +50% vs armour. One in four British Shermans was a Firefly.",
        "On the afternoon of D-Day the Staffordshire Yeomanry's Fireflies stopped the 21st Panzer Division's drive on "
        "the Périers ridge.")},
    {"name": "Churchill AVRE", "unitType": "Armor", "uniqueTo": "Allies", "movement": 3, "strength": 30, "cost": 110,
     "attackSound": "artillery",
     "uniques": ["Unbuildable", "[+100]% Strength <vs cities>", "[+33]% Strength <vs [Fortification] units>",
                 NAME_FROM("Churchill AVRE")],
     "civilopediaText": pedia(
        "Armoured Vehicle Royal Engineers: heavily armoured Churchill tanks carrying a 290mm Petard spigot mortar "
        "that threw a 40-pound 'flying dustbin' against concrete, plus bridges, fascines and mat-layers.",
        "Hobart's Funnies breached the sea wall and cracked the strongpoints on the British and Canadian beaches: "
        "+100% vs cities and +33% vs fortifications.")},
    {"name": "Cromwell", "unitType": "Armor", "uniqueTo": "Allies", "movement": 5, "strength": 28, "cost": 90,
     "attackSound": "tankshot",
     "uniques": ["Unbuildable", NAME_FROM("Cromwell")],
     "civilopediaText": pedia(
        "The fastest tank in Normandy, equipping the 7th Armoured Division - the 'Desert Rats' of North Africa, who "
        "began landing on Gold Beach on the evening of D-Day.")},
    {"name": "M10 Tank Destroyer", "unitType": "Armor", "uniqueTo": "Allies", "replaces": "Tank Destroyer", "movement": 4,
     "strength": 26, "cost": 80, "attackSound": "tankshot",
     "uniques": [ANTI_TANK(50), NAME_FROM("M10 Tank Destroyer")],
     "civilopediaText": pedia(
        "The open-topped M10 Wolverine with a three-inch gun. The 899th Tank Destroyer Battalion landed on Utah Beach on "
        "D-Day.")},
    {"name": "US Artillery", "unitType": "Artillery", "uniqueTo": "Allies", "replaces": "Field Artillery", "movement": 2,
     "strength": 10, "rangedStrength": 25, "range": 2, "cost": 70, "attackSound": "artillery",
     "uniques": ["Must set up to ranged attack", "Ranged attacks may be performed over obstacles", NAME_FROM("US Artillery")],
     "civilopediaText": pedia(
        "Battalions of 105mm howitzers with forward observers and the American fire direction centre, which could mass "
        "every gun in range on one target within minutes. Fires over obstacles.",
        "On Omaha most of the divisional artillery was lost when the overloaded DUKWs carrying it swamped in the surf.")},
    {"name": "Royal Artillery", "unitType": "Artillery", "uniqueTo": "Allies", "movement": 3, "strength": 12,
     "rangedStrength": 24, "range": 2, "cost": 75, "attackSound": "artillery",
     "uniques": ["Unbuildable", "Ranged attacks may be performed over obstacles", NAME_FROM("Royal Artillery")],
     "civilopediaText": pedia(
        "Field regiments of the Royal Artillery and Royal Canadian Artillery. The assault divisions' guns were "
        "self-propelled - Sextons with 25-pounders and Priests with 105mm howitzers - and fired 'run-in shoots' from "
        "their landing craft as they approached the beaches. Self-propelled: no set-up needed. Fires over obstacles.")},
    {"name": "Allied Anti-Tank Guns", "unitType": "Anti-Tank", "uniqueTo": "Allies", "replaces": "Anti-Tank Gun",
     "movement": 2, "strength": 16, "cost": 50, "attackSound": "cannon",
     "uniques": [ANTI_TANK(100), NAME_FROM("Allied Anti-Tank Guns")],
     "civilopediaText": pedia(
        "Anti-tank regiments with 6-pounder and 17-pounder guns. Brought ashore early, they and the Fireflies broke "
        "the 21st Panzer Division's counterattack on D-Day.")},
    {"name": "US General", "unitType": "Commander", "uniqueTo": "Allies", "replaces": "General", "movement": 4,
     "uniques": [AURA, "[+1] Sight", "Can be earned through combat <for [Land] units>",
                 "Is part of Great Person group [General]", "Great Person - [War]", "Unbuildable", "Uncapturable",
                 NAME_FROM("US General")],
     "civilopediaText": pedia(
        "An American corps or division commander. Named generals have personal abilities - see their promotions (for "
        "example Roosevelt, Cota, Gavin or Ridgway).")},
    {"name": "British General", "unitType": "Commander", "uniqueTo": "Allies", "movement": 4,
     "uniques": [AURA, "[+1] Sight", "Unbuildable", "Uncapturable", NAME_FROM("British General")],
     "civilopediaText": pedia(
        "A British or Canadian corps, division or brigade commander. Named generals have personal abilities - see "
        "their promotions (for example Montgomery, Gale or Lovat).")},
    {"name": "Combat Engineers", "unitType": "Infantry", "uniqueTo": "Allies", "replaces": "Engineers", "movement": 2,
     "strength": 16, "cost": 50, "attackSound": "shot",
     "uniques": ["[+50]% Strength <vs cities>", "Can build [Foxholes] improvements on tiles", "Can build [Road] improvements on tiles",
                 NAME_FROM("Combat Engineers")],
     "civilopediaText": pedia(
        "Engineer Special Brigades, Special Engineer Task Forces, Royal Engineers and Royal Canadian Engineers: the men "
        "who blew paths through the beach obstacles under fire, cleared the mines and bulldozed the exits off the beaches.",
        "+50% vs cities; they build Foxholes and Roads.")},

    # ------------------------------------------------------------------ Germany
    {"name": "Grenadiers", "unitType": "Infantry", "uniqueTo": "Germany", "replaces": "Rifle Infantry", "movement": 2,
     "strength": 22, "cost": 50, "attackSound": "machinegun",
     "uniques": ["[+15]% Strength <when defending>", NAME_FROM("Grenadiers")],
     "civilopediaText": pedia(
        "A German grenadier regiment. Every section was built around the MG 42 machine gun, which fired twenty rounds a "
        "second: +15% Strength when defending.",
        "The 352nd Division, a field division with many veterans of the Eastern Front, had moved up to the coast behind "
        "Omaha in March - Allied intelligence did not know it was there.")},
    {"name": "Coastal Infantry", "unitType": "Infantry", "uniqueTo": "Germany", "movement": 2, "strength": 18, "cost": 40,
     "attackSound": "machinegun",
     "uniques": ["Unbuildable", "[+33]% Strength <when defending>", "[-20]% Strength <when attacking>", NAME_FROM("Coastal Infantry")],
     "civilopediaText": pedia(
        "The garrisons of the Atlantic Wall: static divisions like the 709th and 716th, made up of older men, convalescents "
        "and conscripts, with few vehicles and a mixed bag of captured weapons.",
        "They manned the Widerstandsnester - 'resistance nests' of bunkers, trenches, mines and wire - every half mile "
        "along the coast. Stubborn behind concrete (+33% when defending), poor in the attack (-20%).")},
    {"name": "Ost Battalion", "unitType": "Infantry", "uniqueTo": "Germany", "movement": 2, "strength": 15, "cost": 35,
     "attackSound": "shot",
     "uniques": ["Unbuildable", "Withdraws before melee combat <with [40]% chance>", NAME_FROM("Ost Battalion")],
     "civilopediaText": pedia(
        "Battalions of Soviet prisoners of war - Georgians, Armenians, Azerbaijanis, Russians and others - who had joined "
        "the German army, many simply to escape the starvation of the prison camps, and were posted to the West.",
        "Some fought hard; many surrendered at the first chance. They often fall back before an assault.")},
    {"name": "Fallschirmjaeger", "unitType": "Airborne", "uniqueTo": "Germany", "replaces": "Paratroopers", "movement": 2,
     "strength": 25, "cost": 70, "attackSound": "shot",
     "uniques": [PARADROP, "Ignores Zone of Control", "[+15]% Strength <when defending>", NAME_FROM("Fallschirmjaeger")],
     "civilopediaText": pedia(
        "German paratroopers - the Fallschirmjäger - who had not made a combat jump since Crete in 1941 but were among "
        "the best infantry in the German army.",
        "Major Friedrich von der Heydte's 6th Fallschirmjäger Regiment, young and well armed, fought the 101st Airborne "
        "for Carentan for a week.")},
    {"name": "Panzergrenadiers", "unitType": "Infantry", "uniqueTo": "Germany", "movement": 4, "strength": 24, "cost": 70,
     "attackSound": "machinegun",
     "uniques": ["Unbuildable", "[+15]% Strength <when attacking>", NAME_FROM("Panzergrenadiers")],
     "civilopediaText": pedia(
        "Motorised and armoured infantry of the panzer divisions, riding half-tracks and trucks. They move like tanks "
        "and attack hard (+15%).",
        "The 12th SS Panzer Division's grenadiers were mostly eighteen-year-olds of the Hitler Youth, led by veterans of "
        "the Eastern Front; they fought the Canadians around Caen with great ferocity, and some of them murdered Canadian "
        "prisoners at Authie and the Abbaye d'Ardenne.")},
    {"name": "Panzer IV", "unitType": "Armor", "uniqueTo": "Germany", "replaces": "Medium Tank", "movement": 4,
     "strength": 34, "cost": 95, "attackSound": "tankshot",
     "uniques": [ANTI_TANK(15), NAME_FROM("Panzer IV")],
     "civilopediaText": pedia(
        "The Panzer IV with the long 75mm gun - the workhorse of the panzer divisions, slightly better armed than the "
        "Sherman: +15% vs armour. The 21st Panzer Division's 22nd Panzer Regiment, the only armour close to the beaches, "
        "had about 100 of them.")},
    {"name": "Panther", "unitType": "Armor", "uniqueTo": "Germany", "replaces": "Heavy Tank", "movement": 4,
     "strength": 44, "cost": 130, "attackSound": "tankshot",
     "uniques": [ANTI_TANK(25), NAME_FROM("Panther")],
     "civilopediaText": pedia(
        "The Panzer V Panther: thick sloped frontal armour and a long, high-velocity 75mm gun that could destroy a "
        "Sherman at well over a mile. The 12th SS and Panzer Lehr Divisions each had a battalion of them.")},
    {"name": "StuG III", "unitType": "Armor", "uniqueTo": "Germany", "replaces": "Tank Destroyer", "movement": 3,
     "strength": 30, "cost": 80, "attackSound": "tankshot",
     "uniques": [ANTI_TANK(33), "[+20]% Strength <when defending>", NAME_FROM("StuG III")],
     "civilopediaText": pedia(
        "Turretless assault guns and tank destroyers - StuG IIIs, Marders and Major Alfred Becker's home-made conversions "
        "of captured French tanks. Low and hard to spot, they were deadly ambushers in the hedgerows: +33% vs armour and "
        "+20% when defending.")},
    {"name": "German Artillery", "unitType": "Artillery", "uniqueTo": "Germany", "replaces": "Field Artillery",
     "movement": 2, "strength": 10, "rangedStrength": 26, "range": 2, "cost": 70, "attackSound": "artillery",
     "uniques": ["Must set up to ranged attack", "Ranged attacks may be performed over obstacles", NAME_FROM("German Artillery")],
     "civilopediaText": pedia(
        "Battalions of 105mm leFH 18 field howitzers. On D-Day the 352nd Division's guns had every exit off Omaha Beach "
        "registered. Major Werner Pluskat, watching from his bunker at dawn, saw the whole invasion fleet appear out of "
        "the mist. Fires over obstacles.")},
    {"name": "Nebelwerfer", "unitType": "Artillery", "uniqueTo": "Germany", "movement": 2, "strength": 8,
     "rangedStrength": 28, "range": 2, "cost": 70, "attackSound": "missile",
     "uniques": ["Unbuildable", "Can move after attacking", "[-25]% Strength <vs cities>",
                 "Ranged attacks may be performed over obstacles", NAME_FROM("Nebelwerfer")],
     "civilopediaText": pedia(
        "Six-barrelled rocket launchers that fired a ripple of 150mm rockets with a terrifying howl - the Allied troops "
        "called them 'Moaning Minnies'. Devastating against troops in the open but inaccurate (-25% vs cities). They "
        "fired and moved off before the counter-battery fire arrived.")},
    {"name": "88 Flak", "unitType": "Anti-Tank", "uniqueTo": "Germany", "replaces": "Anti-Tank Gun", "movement": 2,
     "strength": 20, "cost": 60, "attackSound": "cannon",
     "uniques": [ANTI_TANK(100), "[+1] Sight", NAME_FROM("88 Flak")],
     "civilopediaText": pedia(
        "The 88mm anti-aircraft gun, used in the ground role as the most feared anti-tank gun of the war: it could pierce "
        "any Allied tank at long range. III Flak Corps sent its batteries to Normandy as anti-tank screens.")},
    {"name": "Coastal Battery", "unitType": "Fortification", "uniqueTo": "Germany", "movement": 0, "strength": 22,
     "rangedStrength": 30, "range": 3, "cost": 100, "attackSound": "artillery",
     "uniques": ["Unbuildable", "Cannot move", "Can only attack [Water] tiles", "[+50]% Strength <vs [Warship] units>",
                 "[+25]% Strength <when defending>",
                 NAME_FROM("Coastal Battery")],
     "civilopediaText": pedia(
        "Heavy coast-defence guns in concrete casemates: the navy's 150mm guns at Longues, the 210mm guns of the Crisbecq "
        "battery, the army's 155mm guns at Pointe du Hoc, the 100mm howitzers at Merville. Their casemates faced the sea: they fire "
        "only at ships and landing craft, three hexes out, and fight at +50% against warships. They cannot move.")},
    {"name": "German General", "unitType": "Commander", "uniqueTo": "Germany", "replaces": "General", "movement": 4,
     "uniques": [AURA, "[+1] Sight", "Can be earned through combat <for [Land] units>",
                 "Is part of Great Person group [General]", "Great Person - [War]", "Unbuildable", "Uncapturable",
                 NAME_FROM("German General")],
     "civilopediaText": pedia(
        "A German corps, division or regiment commander. Named commanders have personal abilities - see their "
        "promotions (for example Marcks, von der Heydte, von Luck or Bayerlein).")},
    {"name": "Pioniere", "unitType": "Infantry", "uniqueTo": "Germany", "replaces": "Engineers", "movement": 2,
     "strength": 16, "cost": 50, "attackSound": "shot",
     "uniques": ["[+50]% Strength <vs cities>", "Can build [Foxholes] improvements on tiles", "Can build [Road] improvements on tiles",
                 NAME_FROM("Pioniere")],
     "civilopediaText": pedia(
        "German combat engineers with mines, flamethrowers and demolition charges. +50% vs cities; they build Foxholes "
        "and Roads.")},
]

# German infantry carried the Panzerfaust and the Panzerschreck, which made every hedgerow a tank trap
PANZERFAUST = "[+25]% Strength <vs [Armor] units>"
for _u in UNITS:
    if _u.get("uniqueTo") == "Germany" and _u["unitType"] in ("Infantry", "Airborne"):
        _u["uniques"].append(PANZERFAUST)
        _u["civilopediaText"].append({"text": "Panzerfausts and Panzerschrecks: +25% vs armour."})

# Ships carry no troops ashore; every land unit stays ashore once landed
for _u in UNITS:
    if _u["unitType"] not in ("Warship", "Fortification") and "Cannot embark" not in _u.get("uniques", []):
        _u.setdefault("uniques", []).append(ASHORE)

# In the D-Day scenario the armies follow the historical order of battle: cities cannot raise any new units (the
# scenario's cities all hold a building tagged "Normandy Scenario"). In free play everything is buildable.
SCENARIO_LOCK = "Unavailable <if [Normandy Scenario] is constructed>"
for _u in UNITS:
    _uniques = _u.setdefault("uniques", [])
    if "Unbuildable" not in _uniques:
        _uniques.append(SCENARIO_LOCK)

# Only units with a name group (historical names of timetabled arrivals, or the generals' free-play pools) keep their
# "gets a name" unique - Unciv's validator rejects a reference to a group that does not exist.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dday_oob as oob
_NAMED = {oob.unit_name(side, key) for turn, side, entry, key, names in oob.ARRIVALS if any(names)}
_NAMED |= {"US General", "British General", "German General"}
for _u in UNITS:
    if _u["name"] not in _NAMED:
        _u["uniques"] = [x for x in _u["uniques"] if x != NAME_FROM(_u["name"])]

if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    names = {u["name"] for u in UNITS}
    for side in oob.SIDES:
        for key, name in (oob.A if side == "Allies" else oob.G).items():
            assert name in names, name
    with open(os.path.join(root, "jsons", "Units.json"), "w") as f:
        json.dump(UNITS, f, indent=4, ensure_ascii=False)
    print("Wrote %d units" % len(UNITS))
