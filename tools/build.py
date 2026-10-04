#!/usr/bin/env python3
"""Build Gameoverse-Soundtrack-<version>.zip (resource pack) and the mod's generated data from tools/cache/ (run
tools/fetch.py first): Soybean_56's Minecraft Infinite music, CC BY (credit in the README, the album and the guide).

- 29 music discs (upstream's Heavenly Flight file is Valley of Spirits; the real Heavenly Flight is in tools/extra/),
  converted to mono so jukebox music fades with distance like vanilla discs.
- Background tracks, stereo as-is, added (replace: false) to existing pools: sky -> Aerial Hell's dimension music,
  void -> the outer End and Enderscape's biome pools, nether -> every Nether biome pool. Night tracks play through a
  Music and Melody event (Overworld, night, outside). The pack must load above Music and Melody's own pack, which
  replaces several of those pools.
- A Music and Melody album crediting Soybean_56, and our own disc art (drawn here, not taken from the mod).
- Mod side: src/main/resources/data/gameoverse_soundtrack/jukebox_song/*.json, the disc list for the mod, lang.
"""
import colorsys, json, pathlib, re, shutil, subprocess, zipfile
from PIL import Image

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
CACHE = HERE / 'cache'
OUT = ROOT / 'build' / 'pack'
MOD_RES = ROOT / 'src' / 'main' / 'resources'
NS = 'gameoverse_soundtrack'
VERSION = '1.0'
CHANNEL = 'https://www.youtube.com/channel/UCNfDsbAKPmUo0xFZxf2YjQQ'

DISCS = ['Afterlife', 'Castaway', 'Classic Blues', 'Cobble Man', 'Disc VIII', 'Disc XV', 'Dreamscape', 'Eclipsed',
         'Endgame', 'Eternal Suspense', 'Fearless', 'Flight School', 'Heartbreaker', 'Heavenly Flight',
         "Hero's Journey", 'Home', 'Indevia', 'Jank Zone', 'Kingslayer', 'Magnetic Circuit', 'Mytheria',
         'Queue the Madness', 'Ruins', 'Snowshoe', 'Spaced Out', 'The Traveler', 'Tunnel Vision', 'Valley of Spirits',
         'Washed Away']
# Upstream's "Heavenly Flight.ogg" is really Valley of Spirits (same file under both names, 351.98 s, matching the
# Valley of Spirits video); the real Heavenly Flight comes from Soybean_56's YouTube video (NDu_3wdvNmk, CC BY),
# kept in tools/extra/ since upstream doesn't have it.
SOURCES = {'Heavenly Flight': HERE / 'extra' / 'Heavenly Flight.ogg'}
BACKGROUND = {
    'sky': [f'skymusic/sky{i}' for i in range(1, 6)],
    'night': [f'nightmusic/night{i}' for i in range(1, 5)],
    'void': ['voidmusic/void1'],
    'nether': ['nethermusic/hell5'],
}
APPEND = {
    'sky': {'aerialhell': ['aerialhell.dimension_music']},
    'void': {'minecraft': ['music.end'],
             'enderscape': ['music.enderscape.biome.default_end', 'music.enderscape.biome.celestial_grove',
                            'music.enderscape.biome.corrupt_barrens', 'music.enderscape.biome.magnia_fields',
                            'music.enderscape.biome.veiled_woodlands']},
    'nether': {'minecraft': ['music.nether.nether_wastes', 'music.nether.crimson_forest', 'music.nether.warped_forest',
                             'music.nether.soul_sand_valley', 'music.nether.basalt_deltas']},
}


def slug(title):
    return re.sub(r'[^a-z0-9]+', '_', title.lower().replace("'", '')).strip('_')


def duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def disc_art(index, total):
    """A 16x16 disc: dark vinyl with two grooves and a coloured label, one hue per disc."""
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    hue = index / total
    label = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.65, 0.95))
    label_dark = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.75, 0.6))
    for y in range(16):
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            r = (dx * dx + dy * dy) ** 0.5
            if r > 7.3:
                continue
            if r > 6.6:
                c = (24, 24, 30)
            elif r < 1.0:
                c = (12, 12, 16)
            elif r < 3.1:
                c = label if (dx + dy) < 1 else label_dark
            elif abs(r - 4.6) < 0.45 or abs(r - 5.9) < 0.3:
                c = (58, 58, 70)
            else:
                c = (36, 36, 44)
            if 3.1 <= r <= 6.6 and -dx > 0 and -dy > 0 and abs(dx - dy) < 1.2:
                c = (92, 92, 108)  # light catching the top-left
            img.putpixel((x, y), c + (255,))
    return img


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    assets = OUT / 'assets' / NS
    sounds = {}
    # Discs: mono, so a jukebox fades with distance
    discs = []
    for i, title in enumerate(DISCS):
        s = slug(title)
        dst = assets / 'sounds' / 'disc' / f'{s}.ogg'
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(SOURCES.get(title, CACHE / 'streaming' / f'{title}.ogg')), '-ac', '1',
                        '-c:a', 'libvorbis', '-q:a', '5', str(dst)], check=True)
        sounds[f'music_disc.{s}'] = {'sounds': [{'name': f'{NS}:disc/{s}', 'stream': True}]}
        discs.append({'slug': s, 'title': title, 'seconds': round(duration(dst), 1), 'comparator': i % 15 + 1})
    # Background: stereo, as-is
    for pool, files in BACKGROUND.items():
        entries = []
        for f in files:
            name = f.split('/')[-1]
            dst = assets / 'sounds' / 'music' / pool / f'{name}.ogg'
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(CACHE / f'{f}.ogg', dst)
            entries.append({'name': f'{NS}:music/{pool}/{name}', 'stream': True})
        sounds[f'music.{pool}'] = {'sounds': entries}
        for namespace, keys in APPEND.get(pool, {}).items():
            path = OUT / 'assets' / namespace / 'sounds.json'
            data = json.loads(path.read_text()) if path.exists() else {}
            for key in keys:
                data[key] = {'replace': False, 'sounds': [dict(e, weight=1) for e in entries]}
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2) + '\n')
    (assets / 'sounds.json').write_text(json.dumps(sounds, indent=2) + '\n')

    # Music and Melody: Overworld nights outside, and an album crediting Soybean_56
    events = assets / 'events'
    events.mkdir(parents=True)
    (events / 'overworld_night.json').write_text(json.dumps({
        'name': 'Overworld Night (Soybean_56)',
        'description': 'Night music by Soybean_56 for the Overworld surface',
        'icon': f'{NS}:textures/album/soybean_56.png',
        'entries': [{
            'category': 'pool',
            'music': f'{NS}:music.night',
            'conditions': [
                {'type': 'dimension', 'value': 'overworld'},
                {'type': 'time', 'value': 'night'},
                {'type': 'not', 'value': [{'type': 'player', 'value': 'under_ground'}]},
            ],
        }],
    }, indent=2) + '\n')
    albums = assets / 'albums'
    albums.mkdir(parents=True)
    (albums / 'soybean_56.json').write_text(json.dumps({
        'name': {'translate': f'album.{NS}.soybean_56'},
        'icon': f'{NS}:textures/album/soybean_56.png',
        'tracks': [f'{NS}:music/{p}/{f.split("/")[-1]}' for p, fs in BACKGROUND.items() for f in fs],
        'discs': [f'{NS}:{d["slug"]}' for d in discs],
    }, indent=2) + '\n')
    tex = assets / 'textures' / 'album'
    tex.mkdir(parents=True)
    disc_art(0, 1).save(tex / 'soybean_56.png')
    lang = {f'album.{NS}.soybean_56': 'Minecraft Infinite, by Soybean_56'}
    (assets / 'lang').mkdir(parents=True)
    (assets / 'lang' / 'en_us.json').write_text(json.dumps(lang, indent=2) + '\n')

    (OUT / 'pack.mcmeta').write_text(json.dumps({'pack': {
        'description': f'Gameoverse: music by Soybean_56 (CC BY, {CHANNEL})',
        'pack_format': 84, 'min_format': 75, 'max_format': 88}}, indent=2) + '\n')
    disc_art(5, 28).resize((64, 64), Image.NEAREST).save(OUT / 'pack.png')

    # Mod side: jukebox songs, disc list, disc art, item models and lang (small, committed)
    songs = MOD_RES / 'data' / NS / 'jukebox_song'
    shutil.rmtree(songs, ignore_errors=True)
    songs.mkdir(parents=True)
    item_tex = MOD_RES / 'assets' / NS / 'textures' / 'item'
    item_defs = MOD_RES / 'assets' / NS / 'items'
    models = MOD_RES / 'assets' / NS / 'models' / 'item'
    for d in (item_tex, item_defs, models):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
    mod_lang = {f'itemGroup.{NS}': 'Soundtrack'}
    for i, d in enumerate(discs):
        s = d['slug']
        (songs / f'{s}.json').write_text(json.dumps({
            'sound_event': {'sound_id': f'{NS}:music_disc.{s}'},
            'description': {'translate': f'jukebox_song.{NS}.{s}'},
            'length_in_seconds': d['seconds'],
            'comparator_output': d['comparator'],
        }, indent=2) + '\n')
        disc_art(i, len(discs)).save(item_tex / f'music_disc_{s}.png')
        (models / f'music_disc_{s}.json').write_text(json.dumps({
            'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:item/music_disc_{s}'}}) + '\n')
        (item_defs / f'music_disc_{s}.json').write_text(json.dumps({
            'model': {'type': 'minecraft:model', 'model': f'{NS}:item/music_disc_{s}'}}) + '\n')
        mod_lang[f'item.{NS}.music_disc_{s}'] = 'Music Disc'
        mod_lang[f'jukebox_song.{NS}.{s}'] = f'Soybean_56 - {d["title"]}'
    (MOD_RES / 'assets' / NS / 'lang').mkdir(parents=True, exist_ok=True)
    (MOD_RES / 'assets' / NS / 'lang' / 'en_us.json').write_text(json.dumps(mod_lang, indent=2, ensure_ascii=False) + '\n')
    (MOD_RES / NS / 'discs.json').parent.mkdir(parents=True, exist_ok=True)
    (MOD_RES / NS / 'discs.json').write_text(json.dumps([d['slug'] for d in discs], indent=2) + '\n')
    (HERE / 'discs.json').write_text(json.dumps(discs, indent=2, ensure_ascii=False) + '\n')

    zip_path = ROOT / f'Gameoverse-Soundtrack-{VERSION}.zip'
    zip_path.unlink(missing_ok=True)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_STORED) as z:
        for f in sorted(OUT.rglob('*')):
            if f.is_file():
                z.write(f, f.relative_to(OUT))
    print(f'{zip_path.name}: {zip_path.stat().st_size / 1e6:.1f} MB, {len(discs)} discs, '
          f'{sum(len(v) for v in BACKGROUND.values())} background tracks')


main()
