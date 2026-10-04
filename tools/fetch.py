#!/usr/bin/env python3
"""Download Soybean_56's Minecraft Infinite music (CC BY, see README) from the mod author's resources repo into
tools/cache/ (not committed). Records each file's SHA-256 in tools/tracks.json the first time, and checks it after."""
import hashlib, json, pathlib, urllib.parse, urllib.request

HERE = pathlib.Path(__file__).parent
CACHE = HERE / 'cache'
BASE = 'https://raw.githubusercontent.com/VesuviusVenox/Classic-Resources/main/'
BACKGROUND = {
    'sky': [f'skymusic/sky{i}.ogg' for i in range(1, 6)],
    'night': [f'nightmusic/night{i}.ogg' for i in range(1, 5)],
    'void': ['voidmusic/void1.ogg'],
    'nether': ['nethermusic/hell5.ogg'],
}
DISCS = ['Afterlife', 'Castaway', 'Classic Blues', 'Cobble Man', 'Disc VIII', 'Disc XV', 'Dreamscape', 'Eclipsed',
         'Endgame', 'Eternal Suspense', 'Fearless', 'Flight School', 'Heartbreaker', 'Heavenly Flight',
         "Hero's Journey", 'Home', 'Indevia', 'Jank Zone', 'Kingslayer', 'Magnetic Circuit', 'Mytheria',
         'Queue the Madness', 'Ruins', 'Snowshoe', 'Spaced Out', 'The Traveler', 'Tunnel Vision', 'Valley of Spirits',
         'Washed Away']


def main():
    CACHE.mkdir(exist_ok=True)
    meta_path = HERE / 'tracks.json'
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    paths = [p for group in BACKGROUND.values() for p in group] + [f'streaming/{t}.ogg' for t in DISCS]
    for path in paths:
        local = CACHE / path
        if not local.exists():
            local.parent.mkdir(parents=True, exist_ok=True)
            url = BASE + urllib.parse.quote(path)
            print('downloading', path)
            urllib.request.urlretrieve(url, local)
        digest = hashlib.sha256(local.read_bytes()).hexdigest()
        if path in meta and meta[path] != digest:
            raise SystemExit(f'{path}: checksum changed upstream ({meta[path]} -> {digest}); check before using it')
        meta[path] = digest
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + '\n')
    print(len(paths), 'tracks in', CACHE)


main()
