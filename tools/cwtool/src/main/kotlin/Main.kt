package cwtool

import com.badlogic.gdx.Gdx
import com.badlogic.gdx.backends.headless.HeadlessFiles
import com.unciv.UncivGame
import com.unciv.logic.files.UncivFiles
import com.unciv.models.metadata.GameSettings
import com.unciv.models.ruleset.RulesetCache
import com.unciv.models.ruleset.validation.RulesetErrorSeverity
import java.io.File

/** Must match the mod's folder name as Unciv installs it from GitHub (dashes become spaces). */
const val MOD = "WWII Battles"

fun initUnciv() {
    Gdx.files = HeadlessFiles()
    UncivGame.Current = UncivGame(true)
    UncivGame.Current.files = UncivFiles(Gdx.files, File(".").absolutePath)
    UncivGame.Current.settings = GameSettings().apply { showTutorials = false }
    val errors = RulesetCache.loadRulesets(consoleMode = true, noMods = false)
    errors.forEach { println("LOAD: $it") }
}

/** Runs Unciv's own ruleset validator (the in-game "Locate mod errors" check). Returns the number of warnings+errors. */
fun validate(): Int {
    initUnciv()
    val mod = RulesetCache[MOD] ?: error("Mod not loaded: ${RulesetCache.keys}")
    var bad = 0
    for ((label, list) in listOf(
        "mod-only" to mod.getErrorList(tryFixUnknownUniques = false),
        "combined" to RulesetCache.checkCombinedModLinks(linkedSetOf(MOD), MOD).second)) {
        println("=== $label: ${list.size} entries")
        for (e in list.sortedByDescending { it.errorSeverityToReport }) {
            if (e.errorSeverityToReport == RulesetErrorSeverity.OK) continue
            // Unciv's built-in tutorials reference ExtraImages that only exist in a full game install
            if (e.text.startsWith("(Tutorial)") && e.text.contains("extraImage")) continue
            println("[${e.errorSeverityToReport}] ${e.text}")
            if (e.errorSeverityToReport >= RulesetErrorSeverity.Warning) bad++
        }
    }
    println("Problems (warning or worse): $bad")
    return bad
}

fun main(args: Array<String>) {
    when (args.firstOrNull()) {
        "validate" -> if (validate() > 0) System.exit(1)
        "pack" -> packAtlas(File(args[1]))
        "map" -> buildMap(File(args[1]), File(args[2]))
        "scenario" -> buildScenario(File(args[1]), File(args[2]), File(args[3]), args.getOrElse(4) { "Veteran" })
        "simulate" -> simulateScenario(File(args[1]), args[2].toInt(), args.getOrElse(3) { "Allies" }, args.getOrNull(4) == "history-off")
        "balance" -> balanceRun(File(args[1]), args[2], args[3].toInt())  // balance <scenario> <AI|Allies|Germany> <seed>
        "build" -> {  // build <modDir>: everything in one JVM
            val mod = File(args[1])
            val tiles = File(mod, "tools/build/normandy_tiles.json")
            val map = File(mod, "maps/$MAP_NAME")
            packAtlas(mod)
            buildMap(tiles, map)
            for ((name, difficulty) in SCENARIOS) buildScenario(tiles, map, File(mod, "scenarios/$name"), difficulty)
            if (validate() > 0) System.exit(1)
        }
        else -> println("usage: build <modDir> | validate | pack <modDir> | map <tiles.json> <out> | scenario <tiles.json> <map> <out> [difficulty] | simulate <scenario> <turns> [Allies|Germany] [history-off] | balance <scenario> <AI|Allies|Germany> <seed>")
    }
}
