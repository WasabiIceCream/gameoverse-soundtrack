# Gameoverse Soundtrack

Music by **Soybean_56** ([YouTube](https://www.youtube.com/channel/UCNfDsbAKPmUo0xFZxf2YjQQ),
[SoundCloud](https://soundcloud.com/soybean56)), licensed under Creative Commons Attribution (CC BY): credit them by
name and link their channel. Composed for Minecraft Infinite; most track names there differ from the titles on their
channel. The code here is MIT.

Two parts:

- **The mod** (both sides, small): 29 music discs, each a jukebox song "Soybean_56 - <title>". Every structure chest
  has a 2% chance to hold one (Locked Chests included, since they roll their structure's own table), they join the
  discs a creeper drops when a skeleton kills it, and they're in the Tools tab in creative.
- **The resource pack** `Gameoverse-Soundtrack-<v>.zip` (client, all the audio, ~100 MB): the discs in mono (so a
  jukebox fades with distance), and background music in stereo added to existing pools: sky tracks to Aerial Hell's
  dimension music, the void track to the outer End and Enderscape's biome pools, an extra Nether track to every Nether
  biome. Night tracks play on the Overworld surface at night through a Music and Melody event, and a Music and Melody
  album "Minecraft Infinite, by Soybean_56" lists everything. The pack must load **above** Music and Melody's own pack
  (it replaces several of those pools), so it goes last in `resourcepackoverrides.json`.
  Music and Melody's replaced pools also drop three tracks other mods add (Enderscape's Lullaby, Legacies and
  Legends' Worn Away and If We Could Reverse Time); `RESTORE` in `tools/build.py` adds them back.

The upstream files (github.com/VesuviusVenox/Classic-Resources) have Valley of Spirits under both its own name and
Heavenly Flight's (the file matches the Valley of Spirits video, 351.98 s). The real Heavenly Flight is taken from
Soybean_56's YouTube video (NDu_3wdvNmk, marked CC BY) and kept in `tools/extra/`, since upstream doesn't have it. The rest of that repo's music is Mojang's C418 soundtrack
under old names and is not used.

## Building

    python3 tools/fetch.py   # downloads the tracks into tools/cache/ (not committed), checks tools/tracks.json
    python3 tools/build.py   # builds the pack zip and the mod's generated data (jukebox songs, disc art, lang)
    JAVA_HOME=/usr/lib/jvm/java-25-openjdk sh ./gradlew build

Disc art is drawn by `tools/build.py` (our own; nothing taken from Minecraft Infinite).
