"""Generates the D-Day scenario's clock and its historical messages:
  jsons/TileResources.json  the clock in the top bar: the day of June and the hour, as two counters
  jsons/Events.json         the pop-up messages: each side's opening briefing and orders, and the history of the
                            invasion hour by hour
  jsons/GlobalUniques.json  the uniques that run them (the rest of that file is hand-written and kept as it is)

How it works: at the end of each turn, every side sets its clock to the next turn's time and queues the next turn's
messages, which pop up when that turn starts. Turn 0 is set up by the scenario builder (tools/cwtool
ScenarioBuilder.kt): it starts the clock at 6 AM, June 6 and queues each side's opening briefing. Unciv's New Game
screen starts a scenario with an odd turn count, so nothing here runs at turn start.

The history messages can be switched off from any of them (the [History off] counter); the last-light reminder always
shows. Everything only runs in the scenario (the [Normandy Scenario] buildings exist there only). Night turns also cost
every unit one tile of sight.
Run from the repository root:  python3 tools/gen_events.py
"""
import json, os, sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import dday_oob as oob
from gen_buildings import SCENARIO_TAG, INTO_THE_SEA_TURN

DAY, HOUR, HISTORY_OFF = "June", "Hour", "History off"   # counters; DAY and HOUR are also in ScenarioBuilder.kt
IN_SCENARIO = "<if [%s] is constructed>" % SCENARIO_TAG
HISTORY_ON = "<when number of [%s] is less than [1]>" % HISTORY_OFF
LAST_CLOCK_TURN = 60     # the scenario's maxTurns
NIGHTS = [(17, 19), (28, 30)]


def event_name(key):
    return "D-Day: " + key


def opening_event(side):   # queued by ScenarioBuilder.kt for turn 0: "D-Day: Allies briefing"
    return event_name("%s briefing" % side)


# ---------------------------------------------------------------- facts taken from the order of battle

def hq(side):
    return next(e[0] for e in oob.ENTRIES if e[1] == side and e[4])


def versus_history():
    """How the Allied target compares with what the Allies actually held at nightfall on June 8, 1944."""
    t, h = oob.ALLIED_TARGET, oob.HISTORICAL_ALLIED
    if t > h:
        return "more than the %d the Allies actually held in 1944" % h
    if t == h:
        return "as many as the Allies actually held in 1944"
    return "even though the Allies actually held %d in 1944" % h


def positions(side):
    return [o[0] for o in oob.OBJECTIVES if o[2] == side]


def names(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def turns(side, entry, first, last, keys=None):
    """'turns 3-6' for the arrivals of a side at an entry between two turns; fails if the timetable changed."""
    ts = sorted({a[0] for a in oob.ARRIVALS if a[1] == side and a[2] == entry and first <= a[0] <= last
                 and (keys is None or a[3] in keys)})
    assert ts and ts[0] == first and ts[-1] == last, (side, entry, first, last, ts)
    return "turn %d" % first if first == last else "turns %d-%d" % (first, last)


def first_turn(side, name):
    return next(a[0] for a in oob.ARRIVALS if a[1] == side and name in a[4])


def p(text, **kw):
    return dict(text=text, **kw)


def header(text):
    return p(text, header=3)


SEP = {"separator": True}
CONTINUE = {"text": "Continue"}
HISTORY_OFF_CHOICE = {"text": "Continue (no more history messages)",
                      "uniques": ["Set [%s] to [1] <hidden from users>" % HISTORY_OFF]}

# ---------------------------------------------------------------- turn 0: briefing and orders, one pair per side

COMMANDER = {"Allies": "General", "Germany": "Field Marshal"}

BRIEFING = {
    "Allies": [
        header("D-Day: the Normandy landings"),
        p("General Eisenhower: after a day's postponement for the weather, you gave the order - 'OK, let's go.' "
          "Operation Overlord, the invasion of German-occupied France, has begun."),
        p("In the night, three airborne divisions dropped behind the beaches. The American 82nd and 101st came down "
          "scattered across the Cotentin peninsula, but they hold Sainte-Mère-Église and parts of the Utah causeways. "
          "The British 6th Airborne seized the bridges over the Orne and the Caen Canal - Pegasus Bridge - and attacked "
          "the Merville battery."),
        p("Now it is 6 AM. The warships are bombarding the coast, and the first assault waves are in their landing "
          "craft off five beaches: the Americans at Utah and Omaha, the British at Gold and Sword, the Canadians at Juno."),
    ],
    "Germany": [
        header("D-Day: the Normandy landings"),
        p("Field Marshal Rommel: you are at home in Germany for your wife's birthday - the forecast promised days of "
          "storms, too rough for an invasion. Your army in Normandy must fight the first hours without you; you play "
          "General Marcks, commanding LXXXIV Corps from Saint-Lô."),
        p("In the night, enemy paratroopers came down all over the Cotentin and east of the Orne. They hold "
          "Sainte-Mère-Église and the bridges at Bénouville. Now, at dawn, the sea off the coast is covered with ships "
          "from horizon to horizon, and the bombardment has begun."),
        p("Your coast divisions are in their strongpoints. The 21st Panzer Division is south of Caen, waiting for orders. "
          "The other panzer divisions are held back on the Führer's orders - and the Führer is asleep."),
    ],
}

REINFORCEMENTS = {
    "Allies": "Follow-up waves arrive every hour at each fleet - Force U, O, G, J and S - and must sail in and land. "
              "Once you hold a beach, its waves come ashore there instead. Gliders land at Pegasus Bridge and "
              "Sainte-Mère-Église at 9 PM (%s). On June 7 and 8 come the 7th Armoured Division (Gold), the 2nd and "
              "90th Infantry Divisions (Omaha and Utah) and the 51st Highland Division." % (
                  turns("Allies", "Pegasus Bridge", 15, 15)),
    "Germany": "The 21st Panzer Division's tanks come up the Falaise Road on D-Day (%s), the 12th SS Panzer Division on "
               "June 7 (from %s) and the Panzer Lehr Division at Villers-Bocage on June 8 (%s). Infantry reserves come "
               "from Saint-Lô, the Valognes Road and the Lisieux Road." % (
                   turns("Germany", "Falaise Road", 2, 3, ("PZIV",)),
                   "turn %d" % first_turn("Germany", "25th SS Panzergrenadier Regiment (Meyer)"),
                   turns("Germany", "Villers-Bocage", 30, 35)),
}

ADVICE = {
    "Allies": "Advice: get off the beaches before the panzers come. Engineers and the AVREs crack strongpoints; the "
              "warships can shell anything within three tiles of the sea; Rangers and Commandos land without losing a "
              "turn. Once ashore, troops cannot re-embark.",
    "Germany": "Advice: every hour the enemy is held on the beaches, more of his waves pile up offshore. Hold the "
               "strongpoints, keep your panzers out of reach of the warships' guns, and strike where his troops are "
               "still landing.",
}


def orders(side):
    own, enemy = positions(side), positions(oob.OTHER[side])
    other_hq = hq(oob.OTHER[side])
    held = "You hold %s." % names(own)
    out = [
        header("Your orders, %s %s" % (COMMANDER[side], "Eisenhower" if side == "Allies" else "Rommel")),
        p("Hold the Beachhead" if side == "Allies" else "Contain the Invasion", header=4),
        p("Thirteen KEY POSITIONS decide the battle: %s. %s" % (names(o[0] for o in oob.OBJECTIVES), held)),
        p("At nightfall on June 8 - the end of turn %d - the Allies win if they hold at least %d of them, %s. "
          "Otherwise Germany has contained the invasion and wins." % (oob.LAST_TURN, oob.ALLIED_TARGET, versus_history()),
          link="Victory/Hold the Beachhead" if side == "Allies" else "Victory/Contain the Invasion"),
    ]
    if side == "Allies":
        out += [
            p("Breakout", header=4),
            p("Capture the German headquarters at %s and the battle is won at once - but it is far stronger than any "
              "other town. Your own headquarters is aboard ship, at %s, out of the enemy's reach." % (other_hq, hq(side)),
              link="Victory/Breakout"),
            p("Beware: if the Germans hold all five beaches at the end of any turn from turn %d (4 PM today) onward, "
              "the invasion has failed." % INTO_THE_SEA_TURN, link="Victory/Into the Sea"),
        ]
    else:
        out += [
            p("Into the Sea", header=4),
            p("Hold all five beaches - %s - at the end of any turn from turn %d (4 PM today) onward and the invasion has "
              "failed. The enemy cannot win by taking your headquarters at %s unless he storms it: it is far stronger "
              "than any other town." % (names(oob.BEACHES), INTO_THE_SEA_TURN, hq(side)),
              link="Victory/Into the Sea"),
        ]
    out += [
        SEP,
        p(REINFORCEMENTS[side]),
        p("The 'Arrivals' and 'Landing Point' buildings in the Civilopedia list every unit and its turn. If the enemy "
          "takes a town where reinforcements arrive by road or by glider, those still due there are lost."),
        p("The top bar shows the day of June (the calendar) and the hour on the 24-hour clock (the watch) next to the "
          "turn number. On D-Day each turn is one hour; on June 7 and 8, two hours. Click the turn number to see the "
          "victory status."),
        p(ADVICE[side]),
    ]
    return out


# ---------------------------------------------------------------- the battle, hour by hour (shown to both sides)
# (turn the message is shown, key, title, paragraphs)

HISTORY = [
    (1, "H-Hour", "H-Hour: Utah and Omaha", [
        "At 6:30 AM the first landing craft grounded on the American beaches.",
        "At Utah the tide and the smoke carried the 8th Infantry a mile south of its target, onto a stretch of beach the "
        "bombers had wrecked. Brigadier General Theodore Roosevelt Jr., 56 years old and walking with a cane, looked over "
        "the ground and decided: 'We'll start the war from right here!'",
        "At Omaha everything went wrong. The bombs had fallen inland, most of the DD tanks had sunk on the way in, and the "
        "352nd Division was waiting on the bluffs. On Dog Green, Company A of the 116th Infantry lost nearly every man "
        "within minutes of the ramps going down.",
    ]),
    (2, "Pointe du Hoc", "The Rangers at Pointe du Hoc", [
        "At 7:10 AM - forty minutes late, after the current had carried them toward the wrong headland - three companies "
        "of the 2nd Ranger Battalion under Lt. Col. James Rudder fired their rocket-propelled grapnels to the top of "
        "Pointe du Hoc and climbed a hundred feet of cliff under fire. They found the gun pits empty: the guns had been "
        "moved inland. A patrol found them in an orchard and destroyed them with thermite grenades.",
        "At 7:25 the British landed on Gold and Sword, behind Hobart's 'Funnies' - flail tanks, bridge-layers and AVREs; "
        "the Canadians followed on Juno, delayed by the offshore reefs, at 7:45.",
    ]),
    (3, "Bloody Omaha", "Bloody Omaha", [
        "By 8:30 AM the landings at Omaha had come to a standstill: the beach was jammed with wrecked vehicles and pinned "
        "men, and the beachmasters stopped sending in vehicles. Aboard the Augusta, General Bradley thought of diverting "
        "the follow-up waves to Utah and the British beaches.",
        "On the beach, officers and sergeants began to move men forward. 'Two kinds of people are staying on this "
        "beach,' said Colonel George Taylor of the 16th Infantry: 'the dead and those who are going to die. Now let's get "
        "the hell out of here!' General Norman Cota told the 5th Rangers: 'Rangers, lead the way!'",
    ]),
    (4, "The destroyers", "The destroyers go in", [
        "At 9:50 AM the destroyers off Omaha - USS McCook, Carmick, Doyle, Emmons, Thompson, Frankford, Harding, Baldwin "
        "and the British Talybont, Tanatside and Melbreak - steamed in so close to the beach that their keels scraped the "
        "sand, and fired over the heads of the infantry into the German strongpoints one by one.",
        "Inland, small groups of the 116th and 16th Infantry and the Rangers had climbed the bluffs between the "
        "strongpoints and were fighting their way toward Vierville, Saint-Laurent and Colleville.",
    ]),
    (5, "The panzers wait", "The panzers wait", [
        "The 21st Panzer Division, the only armoured division near the beaches, had been ready since the small hours. Its "
        "commander, General Feuchtinger, had spent the night in Paris. Its tanks were first sent east of the Orne against "
        "the British paratroopers, then, at 10:30 AM, ordered to turn round and attack west of the Orne - which meant "
        "driving through Caen.",
        "The 12th SS Panzer and Panzer Lehr Divisions waited for release by Hitler, who had gone to bed at 3 AM and whom "
        "nobody dared to wake.",
    ]),
    (7, "Lovat at the bridge", "The commandos reach Pegasus Bridge", [
        "At 1:30 PM the airborne men holding the Orne bridges heard bagpipes. Lord Lovat's 1st Special Service Brigade, "
        "led by his piper Bill Millin, had fought its way six miles from Sword Beach. 'Sorry we're two and a half minutes "
        "late,' Lovat is said to have told Brigadier Poett.",
        "On Omaha, at 1:30 PM, General Gerow signalled Bradley: 'Troops formerly pinned down on beaches Easy Red, Easy Green, "
        "Fox Red advancing up heights behind beaches.'",
    ]),
    (9, "Gold and Juno", "Gold and Juno", [
        "On Gold, the 50th Division was off the beach and pushing inland toward Bayeux. Company Sergeant Major Stanley "
        "Hollis of the 6th Green Howards had stormed two pillboxes on Mont Fleury and saved two of his men under fire - "
        "the only Victoria Cross of D-Day. 47 Royal Marine Commando was marching west behind the German lines toward "
        "Port-en-Bessin.",
        "On Juno the Canadians had fought through the seafront towns of Courseulles, Bernières and Saint-Aubin and were "
        "streaming inland, while the beach behind them jammed with traffic.",
    ]),
    (10, "21st Panzer attacks", "The 21st Panzer Division attacks", [
        "At about 4 PM some forty Panzer IVs of the 22nd Panzer Regiment attacked north from Caen toward the Périers ridge, "
        "into the gap between Sword and Juno. 'If you don't succeed in throwing the British into the sea,' General Marcks "
        "told Colonel von Oppeln-Bronikowski, 'we shall have lost the war.'",
        "They ran into the 2nd King's Shropshire Light Infantry, the Staffordshire Yeomanry's Fireflies and the "
        "anti-tank guns on the ridge at Biéville and lost thirteen tanks in minutes. Only the grenadiers of the "
        "192nd Panzergrenadier Regiment slipped through the gap.",
    ]),
    (14, "To the sea at Lion", "To the sea at Lion-sur-Mer", [
        "At 8 PM a battalion of the 192nd Panzergrenadier Regiment reached the coast at Lion-sur-Mer, between Juno and "
        "Sword, where a few German strongpoints still held out. For an hour it seemed the British and Canadian beaches "
        "might be split apart.",
    ]),
    (15, "Operation Mallard", "Operation Mallard", [
        "At 9 PM some 250 gliders and their tugs flew in over the coast and landed the 6th Airlanding Brigade beside the "
        "Orne bridges. Watching the sky fill with aircraft, the German commanders at Lion-sur-Mer feared being cut off "
        "and pulled the panzergrenadiers back from the coast.",
        "Near Sainte-Mère-Église the gliders of Operation Elmira brought the 82nd Airborne its artillery, crashing into "
        "the hedgerows in the dusk.",
    ]),
    (16, "Nightfall D-Day", "Nightfall, D-Day", [
        "By midnight about 156,000 Allied troops were ashore in Normandy. Some 4,400 had been killed. None of the "
        "beachheads had reached its D-Day objectives: Caen, Bayeux and Carentan were still in German hands, and only Gold "
        "and Juno had joined up.",
        "But the Atlantic Wall had been broken in a single day, and the German counterattack had failed. Rommel reached "
        "his headquarters at La Roche-Guyon at 10 PM.",
        "Your battle: click the turn number in the top bar to see who holds how many key positions.",
    ]),
    (17, "The first night", "The first night", [
        "Through the night the paratroopers of the 82nd and 101st, many still lost in the hedgerows and the flooded "
        "marshes, fought small battles in the dark. Behind the German lines the panzer divisions finally began to move "
        "toward the coast - the 12th SS from around Lisieux, Panzer Lehr from Chartres, a hundred miles away.",
    ]),
    (19, "June 7", "June 7: Bayeux", [
        "On the morning of June 7 the 50th Division entered Bayeux, undefended and almost untouched - the first town of "
        "any size liberated in France. The 7th Armoured Division, the 'Desert Rats', was coming ashore on Gold.",
        "The 12th SS Panzer Division 'Hitlerjugend', its grenadiers mostly eighteen years old, was arriving west of Caen. "
        "Its commander, Kurt Meyer, climbed a tower of the Abbaye d'Ardenne and watched the Canadians advancing across the "
        "plain toward Carpiquet.",
    ]),
    (22, "Pointe du Hoc holds", "Pointe du Hoc holds", [
        "On the cliffs at Pointe du Hoc, Rudder's Rangers - fewer than a hundred men still able to fight - beat off one "
        "German counterattack after another, short of ammunition and cut off from Omaha. They would be relieved on June 8.",
        "At Sainte-Mère-Église, the 82nd Airborne beat off the 1058th Grenadier Regiment's attack from the north with the "
        "help of tanks from Utah Beach.",
    ]),
    (23, "Authie and Buron", "Authie and Buron", [
        "In the afternoon of June 7 the 25th SS Panzergrenadier Regiment struck the North Nova Scotia Highlanders and the "
        "Sherbrooke Fusiliers at Authie and Buron, a few miles short of Carpiquet, and drove them back with heavy losses. "
        "That evening and over the next days, the Hitlerjugend murdered more than a hundred and fifty Canadian prisoners, "
        "among them eighteen at the Abbaye d'Ardenne.",
        "The Canadians dug in. Carpiquet and Caen would hold out for another month.",
    ]),
    (27, "Port-en-Bessin", "Port-en-Bessin", [
        "Night fell on June 7. At Port-en-Bessin, 47 Royal Marine Commando - having lost most of its radios and a good "
        "deal of its equipment in the landing - fought its way into the harbour between the clifftop strongpoints, and "
        "by the morning of June 8 the town was taken: the British and American beachheads touched.",
    ]),
    (30, "June 8", "June 8: Panzer Lehr", [
        "The Panzer Lehr Division reached the front around Tilly-sur-Seulles after a ninety-mile march by daylight, "
        "ordered against the advice of its commander, Fritz Bayerlein. Allied fighter-bombers had destroyed scores of its "
        "vehicles on the roads, and its soldiers called the highway the 'fighter-bomber racetrack'.",
        "General Montgomery came ashore and set up his tactical headquarters in the grounds of the Château de Creullet.",
    ]),
    (32, "Putot and Norrey", "Putot and Norrey", [
        "On June 8 the 26th SS Panzergrenadier Regiment attacked the Royal Winnipeg Rifles at Putot-en-Bessin and overran "
        "several companies; in the evening the Canadian Scottish counterattacked and retook the village. At Norrey and "
        "Bretteville the Regina Rifles held out through a night of Panther attacks.",
        "To the west, the Rangers at Pointe du Hoc were relieved, and the 29th Division fought its way toward Isigny.",
    ]),
    (38, "Nightfall June 8", "Nightfall, June 8", [
        "Three days after the landings the Allies held a strip of coast fifty miles long and up to ten miles deep. Isigny "
        "fell that night, and on June 12 the 101st Airborne took Carentan, joining Utah and Omaha into one beachhead.",
        "It took six more weeks of hedgerow fighting before the Americans reached Saint-Lô and the British and Canadians "
        "took Caen. On July 25 Operation Cobra broke the German front; Paris was liberated on August 25.",
        "Your battle: Hold the Beachhead is decided from the end of this turn.",
    ]),
]

# shown even with the history messages off
LAST_LIGHT = (37, "Last light", "Last light", [
    "Two turns are left: this one and turn %d (9 PM, June 8). At the end of turn %d the Allies win if they hold at least "
    "%d key positions; otherwise Germany wins. Click the turn number in the top bar to see the count." % (
        oob.LAST_TURN, oob.LAST_TURN, oob.ALLIED_TARGET),
])


def timed_event(turn, key, title, paragraphs, history=True):
    return {
        "name": event_name(key),
        "text": oob.turn_label(turn),
        "civilopediaText": [header(title)] + [p(x) for x in paragraphs],
        "choices": [CONTINUE, HISTORY_OFF_CHOICE] if history else [CONTINUE],
    }


def build():
    events, triggers = [], []
    for side in oob.SIDES:
        orders_name = event_name("%s orders" % side)
        events.append({
            "name": opening_event(side),
            "text": oob.turn_label(0),
            "civilopediaText": BRIEFING[side],
            "choices": [{"text": "Your orders, %s" % COMMANDER[side], "uniques": ["Triggers a [%s] event <hidden from users>" % orders_name]}],
        })
        events.append({
            "name": orders_name,
            "text": oob.turn_label(0),
            "civilopediaText": orders(side),
            "choices": [{"text": "Carry on"},
                        {"text": "Carry on (no history messages)", "uniques": ["Set [%s] to [1] <hidden from users>" % HISTORY_OFF]}],
        })
    for entry in HISTORY + [LAST_LIGHT]:
        turn, key, title, paragraphs = entry
        history = entry is not LAST_LIGHT
        events.append(timed_event(turn, key, title, paragraphs, history))
        when = "<upon turn end> <after turn number [%d]> <before turn number [%d]> %s" % (turn - 1, turn, IN_SCENARIO)
        triggers.append("Triggers a [%s] event %s%s" % (event_name(key), when, " " + HISTORY_ON if history else ""))
    # the clock: at the end of each turn, set it to the time of the next one
    last_day = None
    for t in range(1, LAST_CLOCK_TURN + 1):
        day, hour = oob.clock(t)
        when = "<upon turn end> <after turn number [%d]> <before turn number [%d]> %s" % (t - 1, t, IN_SCENARIO)
        if day != last_day:
            triggers.append("Set [%s] to [%d] %s" % (DAY, day, when))
            last_day = day
        triggers.append("Set [%s] to [%d] %s" % (HOUR, hour, when))
    # night: everyone sees a tile less
    for first, after_last in NIGHTS:
        assert all(oob.is_night(t) for t in range(first, after_last))
        triggers.append("[-1] Sight <after turn number [%d]> <before turn number [%d]> %s" % (first, after_last, IN_SCENARIO))
    assert len({e["name"] for e in events}) == len(events)
    return events, triggers


def resources():
    common = ["Stockpiled", "Cannot be traded"]
    return [
        {"name": DAY, "resourceType": "Strategic", "uniques": common, "civilopediaText": [
            p("The scenario's calendar: the day of June. It is shown in the top bar next to the turn number."),
            p("June 6, D-Day: turns 0-16, one hour each. The night of June 6-7: turns 17-18. June 7: turns 19-27, two "
              "hours each. The night of June 7-8: turns 28-29. June 8: turns 30-%d." % oob.LAST_TURN)]},
        {"name": HOUR, "resourceType": "Strategic", "uniques": common, "civilopediaText": [
            p("The scenario's clock: the hour at the start of this turn, on the 24-hour clock (13 is 1 PM). It is shown "
              "in the top bar next to the turn number."),
            p("D-Day runs hour by hour from 6 AM to 10 PM; June 7 and 8 in two-hour turns from 5 AM. Each night passes in "
              "two turns, at midnight and 3 AM.")]},
        {"name": HISTORY_OFF, "resourceType": "Strategic", "uniques": common + ["Not shown on world screen"],
         "civilopediaText": [p("1 when you have turned off the scenario's history messages, otherwise 0.")]},
    ]


def victories():
    keys = names(o[0] for o in oob.OBJECTIVES)
    count = "[[%s] Buildings]" % oob.OBJECTIVE_BUILDING
    end = "<after turn number [%d]>" % oob.LAST_TURN
    airborne = names(o[0] for o in oob.OBJECTIVES if o[2] == "Allies")
    return [
        {
            "name": "Hold the Beachhead",
            "victoryScreenHeader": "Allies only: hold at least %d of the %d KEY POSITIONS at nightfall on June 8 (the end of turn %d) - "
                                   "%s. The key positions: %s." % (
                                       oob.ALLIED_TARGET, len(oob.OBJECTIVES), oob.LAST_TURN, versus_history(), keys),
            "milestones": ["Have at least [%d] %s" % (oob.ALLIED_TARGET, count)],
            "uniques": ["Only available <for [Allies] Civilizations> %s" % end],
            "victoryString": "The beachhead is secure and ahead of schedule. The Allies are in France to stay - eleven months later, Germany surrenders.",
            "defeatString": "The Allies have broken through the Atlantic Wall and reached their objectives. The invasion has succeeded.",
            "civilopediaText": [
                {"text": "In the D-Day scenario each key position is a city. %s start in Allied hands - the airborne took them in "
                         "the night. The other %d, including all five beaches, start German. Cities cannot be razed, so a key "
                         "position, once taken, is always held by one side or the other." % (airborne, len(oob.OBJECTIVES) - 2)},
                {"text": "The check is made from turn %d onward, at the end of each side's turn. By nightfall on June 8, 1944, the "
                         "Allies held %d of the %d: everything but Carentan, Carpiquet and Caen. Montgomery had hoped for "
                         "Caen on D-Day itself. To win, you must hold %d - %s." % (
                             oob.LAST_TURN, oob.HISTORICAL_ALLIED, len(oob.OBJECTIVES), oob.ALLIED_TARGET, versus_history())},
            ],
        },
        {
            "name": "Contain the Invasion",
            "victoryScreenHeader": "Germany only: hold at least %d of the %d KEY POSITIONS at nightfall on June 8 (the end of turn %d), "
                                   "and the Allies are penned into a beachhead short of their objectives." % (
                                       oob.GERMAN_TARGET, len(oob.OBJECTIVES), oob.LAST_TURN),
            "milestones": ["Have at least [%d] %s" % (oob.GERMAN_TARGET, count)],
            "uniques": ["Only available <for [Germany] Civilizations> %s" % end],
            "victoryString": "The invasion has been contained. The Allies are penned into a strip of coast short of Caen, and the battle for Normandy will be long and bloody.",
            "defeatString": "The Allies are ashore but held short of their objectives. The battle for Normandy will be long and bloody.",
            "civilopediaText": [
                {"text": "The German counterpart of Hold the Beachhead: with %d or more key positions still German at the end of "
                         "turn %d, the Allies cannot have reached their %d. Historically the Germans still held Carentan, "
                         "Carpiquet and Caen on June 8 - %d by this count. Holding Caen bought them six weeks of hard fighting, "
                         "but they could not stop the build-up on the beaches." % (
                             oob.GERMAN_TARGET, oob.LAST_TURN, oob.ALLIED_TARGET, len(oob.OBJECTIVES) - oob.HISTORICAL_ALLIED)},
            ],
        },
        {
            "name": "Breakout",
            "victoryScreenHeader": "Allies only: capture the German headquarters at Saint-Lô (the German capital) to break the defence of Normandy at once.",
            "milestones": ["Capture all capitals"],
            "uniques": ["Only available <for [Allies] Civilizations>"],
            "victoryString": "Saint-Lô has fallen, and with it the German command in Normandy. The road to Paris is open.",
            "defeatString": "Saint-Lô has fallen. The front in Normandy has collapsed.",
            "civilopediaText": [
                {"text": "Only the Allies can win this way: the Allied headquarters is aboard ship, out of the German army's reach. "
                         "Saint-Lô, General Marcks's LXXXIV Corps headquarters, lies in the south-west corner of the map and is far "
                         "stronger than any other city."},
                {"text": "Historically it took until July 18 - six weeks of hedgerow fighting - before the Americans entered the "
                         "ruins of Saint-Lô; the breakout, Operation Cobra, began a week later."},
            ],
        },
        {
            "name": "Into the Sea",
            "victoryScreenHeader": "Germany only: hold all five beaches at the end of any turn from turn %d (%s) onward, and the invasion has failed." % (
                INTO_THE_SEA_TURN, oob.turn_label(INTO_THE_SEA_TURN)),
            "milestones": ["Have at least [%d] [[%s] Buildings]" % (len(oob.BEACHES), oob.BEACH_BUILDING)],
            "uniques": ["Only available <for [Germany] Civilizations> <after turn number [%d]>" % INTO_THE_SEA_TURN],
            "victoryString": "The landings have been thrown back into the sea. It will be a long time before the Allies try again.",
            "defeatString": "The landings have failed. Eisenhower's note takes the blame: 'If any blame or fault attaches to the attempt it is mine alone.'",
            "civilopediaText": [
                {"text": "Rommel's whole plan was to defeat the invasion on the beaches, in the first hours, before the Allies could "
                         "bring their strength ashore. The beaches are the cities of %s; this victory counts their %s." % (
                             names(oob.BEACHES), oob.BEACH_BUILDING)},
                {"text": "It came closest at Omaha, where by mid-morning General Bradley considered diverting the follow-up waves "
                         "to the other beaches. Eisenhower had written a note to be released if the landings failed."},
            ],
        },
    ]


def is_generated(unique):
    return any("[%s]" % n in unique for n in (DAY, HOUR, HISTORY_OFF)) or "[D-Day: " in unique or \
        (unique.startswith("[-1] Sight <after turn number") and IN_SCENARIO in unique)


def _hand_written_style(obj):
    """JSON in the layout of the hand-written files: one unique or one Civilopedia line per line."""
    def one(v):
        return json.dumps(v, ensure_ascii=False)
    out = []
    for k, v in obj.items():
        if isinstance(v, list):
            out.append('    %s: [\n%s\n    ]' % (one(k), ",\n".join("        " + one(x) for x in v)))
        else:
            out.append('    %s: %s' % (one(k), one(v)))
    return "{\n" + ",\n".join(out) + "\n}\n"


def write():
    events, triggers = build()
    with open(os.path.join(ROOT, "jsons", "Events.json"), "w") as f:
        json.dump(events, f, indent=4, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(ROOT, "jsons", "VictoryTypes.json"), "w") as f:
        json.dump(victories(), f, indent=4, ensure_ascii=False)
        f.write("\n")
    with open(os.path.join(ROOT, "jsons", "TileResources.json"), "w") as f:
        json.dump(resources(), f, indent=4, ensure_ascii=False)
        f.write("\n")
    # GlobalUniques.json is hand-written: keep its own uniques and replace the generated ones
    path = os.path.join(ROOT, "jsons", "GlobalUniques.json")
    glob = json.load(open(path), object_pairs_hook=OrderedDict)
    glob["uniques"] = [u for u in glob["uniques"] if not is_generated(u)] + triggers
    with open(path, "w") as f:
        f.write(_hand_written_style(glob))
    print("Wrote %d events, %d clock, night and message triggers" % (len(events), len(triggers)))


if __name__ == "__main__":
    write()
