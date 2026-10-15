package cwtool

import com.unciv.Constants
import com.unciv.UncivGame
import com.unciv.logic.civilization.Civilization
import com.unciv.logic.civilization.PlayerType
import com.unciv.logic.civilization.managers.TurnManager
import com.unciv.logic.civilization.managers.UnitManager
import com.unciv.logic.files.FileConversions
import com.unciv.logic.files.UncivFiles
import com.unciv.logic.map.mapunit.MapUnit
import java.io.File
import kotlin.random.Random

/**
 * Balance test: plays one whole battle and prints a one-line RESULT.
 *
 * Unciv's combat luck depends only on the turn and the tile, so the same scenario file always plays out the same way.
 * To sample different battles, [seed] gives the cities and the game fresh random ids and shuffles the order in which
 * each army's units act: neutral changes that alter the AI's choices (and from then on where and when fights happen)
 * without favouring either side.
 *
 * [mode] "AI": both armies are run by Unciv's AI (a Spectator watches).
 *        "Allies" / "Germany": that side is the human seat, played by Unciv's unit automation, as in [simulateScenario].
 *        Its units choose their promotions like the AI's do, as a player would: by default Unciv's automation never
 *        promotes a human player's units, and over a whole battle that alone makes the automated side lose most games.
 */
fun balanceRun(scenarioFile: File, mode: String, seed: Int, lastTurn: Int = 40) {
    initUnciv()
    UncivGame.Current.settings.automatedUnitsChoosePromotions = true
    val rng = Random(seed)
    // Fresh random ids (cities, game) for every seed, replaced in the saved text so all references stay consistent:
    // Unciv uses them in some combat rolls and AI tie-breaks, so each build of a scenario otherwise plays its own way.
    val uuid = Regex("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
    val fresh = HashMap<String, String>()
    val json = uuid.replace(FileConversions.unzip(scenarioFile.readText().trim())) { m ->
        fresh.getOrPut(m.value) { java.util.UUID(rng.nextLong(), rng.nextLong()).toString() }
    }
    val game = UncivFiles.gameInfoFromString(json)
    UncivGame.Current.gameInfo = game
    val unitListField = UnitManager::class.java.getDeclaredField("unitList").apply { isAccessible = true }
    for (civ in game.civilizations) {
        @Suppress("UNCHECKED_CAST")
        val units = unitListField.get(civ.units) as List<MapUnit>
        unitListField.set(civ.units, units.shuffled(rng))
    }

    val human: Civilization?
    if (mode == "AI") {
        // keep the Spectator as the only human: nextTurn() then plays both armies' turns
        for (civ in game.civilizations) if (!civ.isSpectator()) civ.playerType = PlayerType.AI
        human = null
    } else {
        game.civilizations.removeIf { it.civID == Constants.spectator }
        for (civ in game.civilizations) { civ.playerType = PlayerType.AI; civ.diplomacy.remove(Constants.spectator) }
        human = game.getCivilization(mode).apply { playerType = PlayerType.Human }
        if (game.currentPlayer == Constants.spectator) { game.currentPlayer = ""; game.nextTurn(); game.turns-- }
    }

    val allies = game.getCivilization(ALLIES)
    val germany = game.getCivilization(GERMANY)
    val startUnits = mapOf(ALLIES to allies.units.getCivUnitsSize(), GERMANY to germany.units.getCivUnitsSize())
    val arrived = HashMap<String, Int>()
    val keysAt = LinkedHashMap<Int, String>()
    val firstBeach = LinkedHashMap<String, Int>()
    var hqLost: String? = null
    var prevNames = mapOf(ALLIES to unitIds(allies), GERMANY to unitIds(germany))
    val lost = HashMap<String, Int>()
    val started = System.currentTimeMillis()
    // LOSSES=1: also print who killed the German units, by attacker type (diagnostics for balancing)
    val logLosses = System.getenv("LOSSES") == "1"
    var germanAt = germany.units.getCivUnits().associate { it.id to (it.baseUnit.name to it.currentTile.position) }
    val killers = HashMap<String, Int>()
    val victims = HashMap<String, Int>()

    while (game.turns < lastTurn && game.victoryData == null) {
        if (human != null) TurnManager(human).automateTurn()
        try { game.nextTurn() } catch (e: Exception) {
            // an exception inside Unciv's own turn processing: report it on one line, so batches can count them
            println("CRASH mode=$mode seed=$seed turn=${game.turns}: $e")
            throw e
        }
        for (civ in listOf(allies, germany)) {
            val now = unitIds(civ)
            arrived[civ.civID] = (arrived[civ.civID] ?: 0) + (now - prevNames[civ.civID]!!).size
            lost[civ.civID] = (lost[civ.civID] ?: 0) + (prevNames[civ.civID]!! - now).size
        }
        if (logLosses) {
            val alive = unitIds(germany)
            for ((id, info) in germanAt) {
                if (id in alive) continue
                val (type, pos) = info
                victims[type] = (victims[type] ?: 0) + 1
                val by = allies.units.getCivUnits().filter { pos in it.attacksSinceTurnStart }.map { it.baseUnit.name } +
                    allies.attacksSinceTurnStart.filter { it.target == pos }.map { it.attackingUnit ?: "City" }
                val k = by.lastOrNull() ?: "own attack/moved"
                killers[k] = (killers[k] ?: 0) + 1
            }
            germanAt = germany.units.getCivUnits().associate { it.id to (it.baseUnit.name to it.currentTile.position) }
        }
        prevNames = mapOf(ALLIES to unitIds(allies), GERMANY to unitIds(germany))
        // WATCH=<city name>: print the fight around that city every turn (diagnostics for balancing)
        System.getenv("WATCH")?.let { name ->
            val city = game.civilizations.flatMap { it.cities }.firstOrNull { it.name == name } ?: return@let
            val near = city.getCenterTile().getTilesInDistance(3).flatMap { it.getUnits() }
                .sortedBy { it.civ.civID }.joinToString(", ") { "${it.civ.civID.take(1)}:${it.instanceName ?: it.name}(${it.health}${if (it.isEmbarked()) ",sea" else ""})@${it.currentTile.aerialDistanceTo(city.getCenterTile())}" }
            println("WATCH t${game.turns} $name ${city.civ.civID} hp=${city.health} str=${com.unciv.logic.battle.CityCombatant(city).getDefendingStrength()} :: $near")
        }
        if (game.turns in setOf(2, 4, 8, 12, 16, 19, 23, 27, 32, 38)) keysAt[game.turns] = "${keys(allies)}-${keys(germany)}/b${beaches(allies)}"
        for (c in allies.cities) if (c.cityConstructions.isBuilt(BEACH_DEFENSES)) firstBeach.putIfAbsent(c.name.substringBefore(' '), game.turns)
        if (hqLost == null && germany.cities.none { it.isCapital() }) hqLost = "Germany@${game.turns}"
    }
    val v = game.victoryData
    fun mil(c: Civilization) = c.units.getCivUnits().count { it.isMilitary() }
    println("RESULT mode=$mode seed=$seed winner=${v?.winningCiv ?: "none"} by=${v?.victoryType?.replace(' ', '_') ?: "-"} turn=${v?.victoryTurn ?: game.turns}" +
        " keysA=${keys(allies)} keysG=${keys(germany)} keyTimeline=${keysAt.entries.joinToString(",") { "t${it.key}:${it.value}" }}" +
        " beachesTaken=${firstBeach.entries.joinToString(",") { "${it.key}@${it.value}" }} hqLost=${hqLost ?: "-"}" +
        " unitsA=${startUnits[ALLIES]}+${arrived[ALLIES] ?: 0}-${lost[ALLIES] ?: 0} milA=${mil(allies)} embarkedA=${allies.units.getCivUnits().count { it.isEmbarked() }}" +
        " unitsG=${startUnits[GERMANY]}+${arrived[GERMANY] ?: 0}-${lost[GERMANY] ?: 0} milG=${mil(germany)}" +
        " heldA=${keyPositions(allies).joinToString("|").replace(' ', '_')} heldG=${keyPositions(germany).joinToString("|").replace(' ', '_')}" +
        " secs=${(System.currentTimeMillis() - started) / 1000}")
    if (logLosses) println("LOSSES seed=$seed killers=${killers.entries.sortedByDescending { it.value }.joinToString(",") { "${it.key}:${it.value}" }}" +
        " victims=${victims.entries.sortedByDescending { it.value }.joinToString(",") { "${it.key}:${it.value}" }}")
}

private fun unitIds(civ: Civilization) = civ.units.getCivUnits().map { it.id }.toSet()
private fun keys(civ: Civilization) = civ.cities.count { it.cityConstructions.isBuilt(KEY_POSITION) }
