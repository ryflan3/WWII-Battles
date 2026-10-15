// Command-line helper that drives the real Unciv engine (from the official Unciv.jar release) to
// validate the ruleset, pack the texture atlas, build the Gettysburg map and generate the scenario save.
// Run through tools/build_all.sh, which downloads lib/Unciv.jar and prepares the work/ directory first.
plugins {
    kotlin("jvm") version "2.4.20"
    application
}

repositories { mavenCentral() }

dependencies {
    implementation(files("lib/Unciv.jar"))
    implementation("com.badlogicgames.gdx:gdx-backend-headless:1.14.2")
}

kotlin { jvmToolchain(21) }

application { mainClass.set("cwtool.MainKt") }

tasks.named<JavaExec>("run") {
    workingDir = file("work")
    maxHeapSize = "3g"
    jvmArgs("-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8")
}
