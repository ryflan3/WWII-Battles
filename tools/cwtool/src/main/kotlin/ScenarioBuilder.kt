package cwtool

import com.badlogic.gdx.files.FileHandle
import com.unciv.Constants
import com.unciv.UncivGame
import com.unciv.logic.GameInfo
import com.unciv.logic.GameStarter
import com.unciv.logic.city.City
import com.unciv.logic.city.managers.CityFounder
import com.unciv.logic.civilization.AlertType
import com.unciv.logic.civilization.Civilization
import com.unciv.logic.civilization.PlayerType
import com.unciv.logic.civilization.PopupAlert
import com.unciv.logic.files.UncivFiles
import com.unciv.logic.map.HexCoord
import com.unciv.models.metadata.GameParameters
import com.unciv.models.metadata.GameSetupInfo
import com.unciv.models.metadata.Player
import com.unciv.models.ruleset.PerpetualConstruction
import com.unciv.models.ruleset.RulesetCache
import java.io.File
import java.text.Normalizer

val VICTORIES = arrayListOf("Hold the Beachhead", "Contain the Invasion", "Breakout", "Into the Sea")
const val ALLIES = "Allies"
const val GERMANY = "Germany"
const val KEY_POSITION = "Key Position"      // the building that marks an objective city (dday_oob.OBJECTIVE_BUILDING)
const val BEACH_DEFENSES = "Beach Defenses"  // in the five beach cities (dday_oob.BEACH_BUILDING)
const val TRANSPORT_AREA = "Transport Area"  // in the Allied fleet cities (gen_buildings.TRANSPORT_AREA)
/** The clock in the top bar (gen_events.py DAY and HOUR): the day of June and the hour. gen_events.py sets it at the end
 *  of every turn for the next one; the builder starts it at turn 0, 6 AM on June 6 (dday_oob.clock(0)). */
const val CLOCK_DAY = "June"
const val CLOCK_HOUR = "Hour"
/** Each side's opening briefing (gen_events.opening_event), shown when its first turn starts */
fun openingBriefing(civ: String) = "D-Day: $civ briefing"

/** One scenario file per difficulty. While a scenario is selected, Unciv's New Game screen locks the game options and
 *  uses the difficulty saved in the scenario, so the difficulty (the AI army's strength) is chosen from the scenario list. */
val SCENARIOS = linkedMapOf(
    // No four-digit year in the names: Unciv's New Game screen would display "1944" as "1,944"
    "D-Day" to "Veteran",
    "D-Day (Easiest - Recruit)" to "Recruit",
    "D-Day (Easier - Regular)" to "Regular",
    "D-Day (Harder - Elite)" to "Elite",
    "D-Day (Hardest - Bloody Omaha)" to "Bloody Omaha",
)

/** Ruleset object names are plain ASCII (they double as image file names): "Sainte-Mère-Église" -> "Sainte-Mere-Eglise" */
fun asciiName(text: String) = Normalizer.normalize(text, Normalizer.Form.NFKD).replace(Regex("[^\\p{ASCII}]"), "")

fun buildScenario(tilesJson: File, mapFile: File, outFile: File, difficulty: String = "Veteran") {
    initUnciv()
    val ruleset = RulesetCache[MOD]!!
    val data = com.badlogic.gdx.utils.JsonReader().parse(tilesJson.readText())

    val params = GameParameters().apply {
        baseRuleset = MOD
        mods = LinkedHashSet()
        this.difficulty = difficulty
        speed = "Battle Pace"
        startingEra = "Second World War"
        numberOfCityStates = 0
        minNumberOfCityStates = 0
        maxNumberOfCityStates = 0
        noBarbarians = true
        noCityRazing = true  // key positions must be held, not burned
        espionageEnabled = false
        nuclearWeaponsEnabled = false
        noStartBias = false
        victoryTypes = ArrayList(VICTORIES)
        maxTurns = 60
        // The Spectator is the scenario builder's seat: NewGameScreen removes it and hands the first turn to the right side
        players = arrayListOf(Player(ALLIES, PlayerType.Human), Player(GERMANY, PlayerType.Human), Player(Constants.spectator, PlayerType.Human))
    }
    val setup = GameSetupInfo(params)
    setup.mapParameters.name = "Normandy"
    setup.mapFile = FileHandle(mapFile)
    val game: GameInfo = GameStarter.startNewGame(setup)
    UncivGame.Current.gameInfo = game

    val allies = game.getCivilization(ALLIES)
    val germany = game.getCivilization(GERMANY)
    val sides = listOf(allies, germany)

    // 1. remove the default starting armies GameStarter placed on the starting locations
    for (civ in sides) for (u in civ.units.getCivUnits().toList()) u.destroy()

    // 2. found the cities, each side's headquarters (capital) first: the first city a civ founds becomes its capital.
    //    The Allied fleets are cities on water tiles, out of the German army's reach.
    val cities = data.get("cities").sortedByDescending { it.getBoolean("capital") }
    for (c in cities) {
        val civ = game.getCivilization(c.getString("civ"))
        val city: City = CityFounder().foundCity(civ, HexCoord.of(c.getInt("x"), c.getInt("y")))
        city.name = c.getString("name")
        val kind = c.getString("kind")
        val addBuilding = { b: String -> require(ruleset.buildings.containsKey(b)) { "no building $b" }; city.cityConstructions.addBuilding(b) }
        if (c.getBoolean("objective")) addBuilding(KEY_POSITION)
        when (kind) {
            "fleet" -> { addBuilding(TRANSPORT_AREA); addBuilding("Allied Arrivals: ${city.name}") }
            "beach" -> { addBuilding(BEACH_DEFENSES); addBuilding("Landing Point: ${city.name}") }
            "airhead" -> addBuilding("Allied Arrivals: ${asciiName(city.name)}")
            "road" -> addBuilding("German Arrivals: ${asciiName(city.name)}")
        }
        // headquarters, fleets, roads and inland towns have supply dumps; a beach strongpoint is only its bunkers
        if (kind == "beach") city.cityConstructions.removeBuilding("Supply Depot")
        else if (!city.cityConstructions.isBuilt("Supply Depot")) city.cityConstructions.addBuilding("Supply Depot")
        // nothing can be raised in the scenario: produce "Nothing", so the game never stops to ask "Pick construction"
        city.cityConstructions.editQueue { clear(); add(PerpetualConstruction.Idle.name) }
        println("City ${city.name} (${civ.civID}, $kind) capital=${city.isCapital()} water=${city.getCenterTile().isWater} " +
            "buildings=${city.cityConstructions.getBuiltBuildings().map { it.name }.toList()}")
    }
    val wantCapitals = cities.filter { it.getBoolean("capital") }.associate { it.getString("civ") to it.getString("name") }
    require(allies.getCapital()?.name == wantCapitals[ALLIES] && germany.getCapital()?.name == wantCapitals[GERMANY]) {
        "wrong capitals: ${allies.getCapital()?.name}, ${germany.getCapital()?.name} - expected $wantCapitals"
    }

    // 3. at war from the first shot, and a war that cannot end in peace (minimumWarDuration in ModOptions).
    //    Declared before the armies are placed: Unciv only lets units into enemy territory once at war.
    allies.diplomacyFunctions.makeCivilizationsMeet(germany)
    allies.getDiplomacyManager(germany)!!.declareWar()

    // 4. the armies on the field at 6 AM: the airborne in their drop zones, the first waves in their landing craft,
    //    the bombarding warships, and the German defenders
    for (u in data.get("startUnits")) {
        val civ = game.getCivilization(u.getString("civ"))
        val wanted = HexCoord.of(u.getInt("x"), u.getInt("y"))
        val unit = civ.units.placeUnitNearTile(wanted, u.getString("unit"))
            ?: error("could not place ${u.getString("name")}")
        val name = u.getString("name", null)
        if (name != null) {
            unit.instanceName = name
            game.unitNamesTaken.add(name)
            if (ruleset.unitPromotions.containsKey(name)) unit.promotions.addPromotion(name, true)
        }
        unit.health = u.getInt("health", 100)
        unit.currentMovement = unit.getMaxMovement().toFloat()
        if (unit.currentTile.position != wanted) error("${unit.name} '${unit.instanceName}' landed on ${unit.currentTile.position}, not $wanted")
        if (unit.isEmbarked() != u.getBoolean("embarked")) error("${unit.instanceName}: embarked=${unit.isEmbarked()}")
    }
    println("Placed ${data.get("startUnits").size} units: ${sides.joinToString { "${it.civID} ${it.units.getCivUnitsSize()}" }}, " +
        "embarked ${allies.units.getCivUnits().count { it.isEmbarked() }}")

    // 5. both commanders have maps of the country: reveal the terrain (units stay hidden by fog of war)
    for (tile in game.tileMap.values) for (civ in sides) tile.setExplored(civ, true)

    game.gameParameters.victoryTypes = ArrayList(VICTORIES)
    // Default seats on the New Game screen: you command the Allies against a computer-run German army (the Human/AI
    // buttons swap sides). Set only now: Unciv records the explored area (the camera's scroll limits) for human players
    // only, and either side may end up human.
    germany.playerType = PlayerType.AI
    game.gameParameters.players.first { it.chosenCiv == GERMANY }.playerType = PlayerType.AI
    game.currentPlayer = Constants.spectator
    // Update sight first, then clear: updating adds first-contact messages. The Spectator seat must meet both armies
    // here too, or it meets them when the New Game screen loads the file and the Allies are told "We have encountered Spectator!"
    for (civ in game.civilizations) civ.cache.updateSightAndResources()
    for (civ in game.civilizations) {
        civ.popupAlerts.clear()
        civ.notifications.clear()
    }
    // Turn 0's clock and briefings are set here, not by "upon turn start" uniques: when the New Game screen starts a
    // scenario, the first turn starts with the turn counter still at 1.
    for (civ in sides) {
        civ.resourceStockpiles.add(CLOCK_DAY, 6)
        civ.resourceStockpiles.add(CLOCK_HOUR, 6)
        civ.popupAlerts.add(PopupAlert(AlertType.Event, openingBriefing(civ.civID)))
    }
    outFile.parentFile.mkdirs()
    outFile.writeText(UncivFiles.gameInfoToString(game, forceZip = true))
    println("Scenario written: ${outFile.path} (${outFile.length()} bytes, $difficulty). Civs: ${game.civilizations.map { it.civID }}, current=${game.currentPlayer}, turn=${game.turns}")
}

/** Loads the scenario exactly like NewGameScreen does, then plays [turns] turns. The human side's moves are made by the AI too. */
fun simulateScenario(scenarioFile: File, turns: Int, humanSide: String = ALLIES, historyOff: Boolean = false) {
    initUnciv()
    val game = UncivFiles.gameInfoFromString(scenarioFile.readText())
    UncivGame.Current.gameInfo = game
    // --- same steps as NewGameScreen.startNewGame for scenarios
    game.civilizations.removeIf { it.civID == Constants.spectator }
    for (civ in game.civilizations) { civ.playerType = PlayerType.AI; civ.diplomacy.remove(Constants.spectator) }
    game.getCivilization(humanSide).playerType = PlayerType.Human
    // as if the player chose "no history messages" in the opening orders (gen_events.HISTORY_OFF)
    if (historyOff) game.getCivilization(humanSide).resourceStockpiles.add("History off", 1)
    if (game.currentPlayer == Constants.spectator) { game.currentPlayer = ""; game.nextTurn(); game.turns-- }
    val human = game.getCivilization(humanSide)
    println("Start: current=${game.currentPlayer} turn=${game.turns} human=$humanSide" +
        " clock=June ${human.resourceStockpiles[CLOCK_DAY]}, ${human.resourceStockpiles[CLOCK_HOUR]}:00" +
        " popups=${human.popupAlerts.map { "${it.type}(${it.value})" }}")
    val allies = game.getCivilization(ALLIES)
    val germany = game.getCivilization(GERMANY)
    println("  at war: ${allies.isAtWarWith(germany)}, barbarians in game: ${game.civilizations.any { it.isBarbarian }}, razing allowed: ${!game.gameParameters.noCityRazing}")
    for (civ in listOf(allies, germany)) {
        val explored = game.tileMap.values.count { it.isExplored(civ) }
        val enemy = if (civ == allies) germany else allies
        val enemyUnitsSeen = enemy.units.getCivUnits().count { civ.viewableTiles.contains(it.currentTile) }
        println("  ${civ.civID}: ${civ.units.getCivUnits().count()} units, explored ${explored}/${game.tileMap.values.size} tiles, sees ${enemyUnitsSeen}/${enemy.units.getCivUnits().count()} enemy units, key positions ${keyPositions(civ)}")
        println("  ${civ.civID} happiness: ${civ.stats.getHappinessBreakdown().filterValues { it != 0f }}")
    }
    var lastNames = game.civilizations.associate { it.civID to it.units.getCivUnits().map { u -> u.instanceName ?: u.name }.toList() }
    val totalLost = HashMap<String, Int>()
    val keysHeld = game.civilizations.associate { it.civID to keyPositions(it) }.toMutableMap()
    for (t in 1..turns) {
        com.unciv.logic.civilization.managers.TurnManager(human).automateTurn()
        game.nextTurn()
        // the pop-ups the human player would have to click through this turn
        if (human.popupAlerts.isNotEmpty()) println("  popups for $humanSide: ${human.popupAlerts.map { "${it.type}(${it.value.take(30)})" }}")
        human.popupAlerts.clear()
        val line = StringBuilder("Turn ${game.turns} (June ${human.resourceStockpiles[CLOCK_DAY]}, ${human.resourceStockpiles[CLOCK_HOUR]}:00):")
        for (civ in game.civilizations.filter { it.isMajorCiv() }) {
            val names = civ.units.getCivUnits().map { u -> u.instanceName ?: u.name }.toList()
            val new = names.toMutableList().apply { lastNames[civ.civID].orEmpty().forEach { remove(it) } }
            val lost = lastNames[civ.civID].orEmpty().toMutableList().apply { names.forEach { remove(it) } }
            totalLost[civ.civID] = (totalLost[civ.civID] ?: 0) + lost.size
            val mil = civ.units.getCivUnits().count { it.isMilitary() }
            val emb = civ.units.getCivUnits().count { it.isEmbarked() }
            line.append(" | ${civ.civID}: units=${names.size} mil=$mil embarked=$emb lost=${lost.size} (total ${totalLost[civ.civID]}) cities=${civ.cities.size} keys=${keyPositions(civ).size}" +
                " happiness=${civ.getHappiness()}")
            if (new.isNotEmpty()) line.append(" NEW=${new.size}")
        }
        println(line)
        if (System.getenv("SHOW_EMBARKED") != null && t % 3 == 1)
            println("    at sea: " + allies.units.getCivUnits().filter { it.isEmbarked() }.joinToString { u ->
                val p = u.currentTile.position
                "${u.instanceName ?: u.name}@(${com.unciv.logic.map.HexMath.getColumn(p)},${com.unciv.logic.map.HexMath.getRow(p)})"
            })
        for (civ in game.civilizations.filter { it.isMajorCiv() })
            for (n in civ.notifications.map { it.text }.filter { listOf("destroyed", "disband", "killed", "captured", "lost", "defeated").any { k -> it.contains(k, true) } }.distinct().take(12))
                println("    [${civ.civID}] $n")
        lastNames = game.civilizations.associate { it.civID to it.units.getCivUnits().map { u -> u.instanceName ?: u.name }.toList() }
        for (civ in game.civilizations.filter { it.isMajorCiv() }) {
            val now = keyPositions(civ)
            val gained = now - keysHeld[civ.civID].orEmpty().toSet()
            if (gained.isNotEmpty()) println("    ${civ.civID} took $gained")
            keysHeld[civ.civID] = now
        }
        val victory = game.victoryData
        if (victory != null) {
            println("VICTORY: ${victory.winningCiv} by ${victory.victoryType} on turn ${victory.victoryTurn}; key positions " +
                game.civilizations.filter { it.isMajorCiv() }.joinToString { "${it.civID} ${keyPositions(it)}" })
            break
        }
    }
}

/** Names of the key positions (objective cities) [civ] holds. */
fun keyPositions(civ: Civilization) =
    civ.cities.filter { it.cityConstructions.isBuilt(KEY_POSITION) }.map { it.name }.sorted()

fun beaches(civ: Civilization) = civ.cities.count { it.cityConstructions.isBuilt(BEACH_DEFENSES) }
