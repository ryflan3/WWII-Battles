package cwtool

import com.badlogic.gdx.graphics.Texture
import com.badlogic.gdx.tools.texturepacker.TexturePacker
import java.io.File

/** Packs <mod>/Images into <mod>/game.atlas + game.png with the same settings Unciv's desktop ImagePacker uses. */
fun packAtlas(modDir: File) {
    val settings = TexturePacker.Settings().apply {
        maxWidth = 2048
        maxHeight = 2048
        combineSubdirectories = true
        pot = true
        fast = true
        paddingX = 8
        paddingY = 8
        duplicatePadding = true
        filterMin = Texture.TextureFilter.MipMapLinearLinear
        filterMag = Texture.TextureFilter.MipMapLinearLinear
    }
    for (old in modDir.listFiles()!!.filter { it.name.matches(Regex("game\\d*\\.(png|atlas)")) }) old.delete()
    TexturePacker.process(settings, File(modDir, "Images").path, modDir.path, "game")
    File(modDir, "Atlases.json").writeText("[game]")
    val pages = modDir.listFiles()!!.filter { it.name.matches(Regex("game\\d*\\.png")) }.map { it.name }
    val regions = File(modDir, "game.atlas").readLines().count { it.isNotEmpty() && !it.startsWith(" ") && !it.contains(":") && !it.endsWith(".png") }
    println("Packed atlas pages=$pages regions=$regions")
}
