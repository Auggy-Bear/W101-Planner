"""Generate a standalone HTML build planner from wizard101_items.db.

Writes wizard101_build.html: a single file with all item data embedded, no
server, no dependencies.  Open it by double-clicking.
"""
from __future__ import annotations

import argparse
import glob
import html
import json
import os
import re
import time
from pathlib import Path

from db_reader import iter_item_rows

import config

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'

GAME_SCHOOLS = ('Fire', 'Ice', 'Storm', 'Myth', 'Life', 'Death', 'Balance', 'Shadow')
TYPES = ('Hat', 'Robe', 'Boots', 'Wand', 'Athame', 'Amulet', 'Ring', 'Deck')

SEASONAL_KEYWORDS = ('deckathlete', 'yuletide', "hallow", 'spooky', 'holiday',
                     'birthday', 'festival', 'autumn', 'midsummer', 'festive',
                     'carnival')


def worlds_of(props):
    out = []
    for key in ('WorldDropped', 'WorldBought', 'WorldRewarded'):
        v = props.get(key)
        vals = v if isinstance(v, list) else ([v] if v else [])
        for x in vals:
            s = str(x)
            if s and s not in out:
                out.append(s)
    return out


def is_seasonal(name):
    low = str(name).lower()
    return 1 if any(k in low for k in SEASONAL_KEYWORDS) else 0



SOURCES = ['Card Pack', 'Creature Drop', 'Crafted', 'Vendor', 'Quest', 'Fishing',
           'Gift Card', 'Locked Chest', 'Promo Code', 'Unknown', 'Gardened', 'Raid']


RAID_NAMES = set()


def load_raid_names():
    names = set()
    folder = RAW_DIR / 'Raid'
    for path in glob.glob(os.path.join(folder, '*.html')):
        text = open(path, encoding='utf-8', errors='replace').read()
        m = re.search(r'<table\b[^>]*class="[^"]*smwtable[^"]*"[^>]*>', text)
        if not m:
            continue
        chunk = text[m.start():text.find('</table>', m.start())]
        for row in re.findall(r'<tr\b.*?</tr>', chunk, re.S):
            cells = re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.S)
            if cells:
                n = html.unescape(re.sub(r'<[^>]+>', '', cells[0])).strip()
                if n:
                    names.add(n)
    return names


def source_mask(props, name=None):
    a = props.get('Acquisition')
    if isinstance(a, list):
        a = ', '.join(str(x) for x in a)
    low = str(a or '').lower()
    mask = 0
    if 'card pack' in low:
        mask |= 1 << 0
    if 'creature' in low:
        mask |= 1 << 1
    if 'recipe' in low:
        mask |= 1 << 2
    if 'vendor' in low:
        mask |= 1 << 3
    if 'quest' in low:
        mask |= 1 << 4
    if 'fish chest' in low or config.as_bool(props.get('FishChestDrop')):
        mask |= 1 << 5
    if 'gift card' in low:
        mask |= 1 << 6
    if 'locked chest' in low:
        mask |= 1 << 7
    if 'promotional' in low or 'promo code' in low:
        mask |= 1 << 8
    if (name in RAID_NAMES or 'raid' in low
            or 'ghastly conspiracy' in str(props.get('WorldDropped') or '').lower()):
        mask |= 1 << 11
    if mask == 0:
        mask |= 1 << 9
    return mask


def num(props, key):
    return config.num(props.get(key))


def short(x):
    return int(x) if float(x).is_integer() else round(x, 2)


def dsum(*vals):
    """Sum distinct non-zero values.

    The wiki stores one stat in several properties (ArmorPiercing, GlobalArmorPiercing,
    LifeArmorPiercing; PipConversion, GlobalPipConversion, LifePipConversion) and fills
    the aliases with the same number. Summing every field double- or triple-counts it.
    Distinct values are genuinely different bonuses and do add.
    """
    seen = set()
    total = 0
    for v in vals:
        if v and v not in seen:
            seen.add(v)
            total += v
    return total


def normalize_family(school_vals, generic, universal, own):
    """Assign the generic field (ArmorPiercing / PipConversion) to its owner school.

    The wiki mirrors one school's value into the unprefixed property. On
    Theurgist's Mystic Sphere the generic 7 matches FireArmorPiercing, not the
    Life 8, so it belongs to Fire rather than every school. Unmatched globals are
    true universal bonuses.
    """
    universal_dup = bool(universal and generic and abs(universal - generic) < 1e-9)
    owners = [k for k, v in school_vals.items() if v and generic and abs(v - generic) < 1e-9]
    if universal_dup:
        owner = None          # Global matches the generic field: truly universal
    elif not generic:
        owner = None
    elif owners:
        owner = own if own in owners else owners[0]
    elif own in GAME_SCHOOLS:
        owner = own
    else:
        owner = None          # universal

    univ = 0
    if universal and not universal_dup:
        matches = any(v and abs(v - universal) < 1e-9 for v in school_vals.values())
        if not matches:
            univ = universal

    out = {}
    for k in GAME_SCHOOLS:
        parts = []
        if school_vals.get(k):
            parts.append(school_vals[k])
        if generic and (owner == k or owner is None):
            parts.append(generic)
        if univ:
            parts.append(univ)
        val = dsum(*parts)
        if val:
            out[k] = val
    return out


PIN_KEYS = ('PowerPins', 'SwordPins', 'ShieldPins')
SOCKET_KEYS = ('CircleSockets', 'SquareSockets', 'TriangleSockets', 'TearSockets')


def socket_shapes(props):
    out = []
    for key in SOCKET_KEYS:
        n = int(num(props, key))
        out += [key[:-7]] * max(0, min(n, 4))
    return out


def pin_shapes(props):
    out = []
    for key in PIN_KEYS:
        n = int(num(props, key))
        out += [key[:-4]] * max(0, min(n, 3))
    return out


def payload(name, itype, school, level, props):
    pierce_raw = {k: num(props, f'{k}ArmorPiercing') for k in GAME_SCHOOLS}
    pip_raw = {k: num(props, f'{k}PipConversion') for k in GAME_SCHOOLS}
    pierce = normalize_family(pierce_raw, num(props, 'ArmorPiercing'),
                              num(props, 'GlobalArmorPiercing'), school)
    pip = normalize_family(pip_raw, num(props, 'PipConversion'),
                           num(props, 'GlobalPipConversion'), school)
    pip.pop('Shadow', None)   # Shadow Pip Conversion does not exist

    sch = {}
    for s in GAME_SCHOOLS:
        vals = [
            num(props, f'{s}Damage'),
            num(props, f'{s}FlatDamage'),
            num(props, f'{s}Critical'),
            num(props, f'{s}CriticalBlock'),
            pierce.get(s, 0),
            num(props, f'{s}Resist'),
            num(props, f'{s}Accuracy'),
            pip.get(s, 0),
        ]
        if any(vals):
            sch[s] = [short(v) for v in vals]

    return {
        'n': name,
        't': TYPES.index(itype),
        's': GAME_SCHOOLS.index(school) if school in GAME_SCHOOLS else -1,
        'l': int(level) if level is not None else 0,
        'r': 1 if config.as_bool(props.get('Retired')) else 0,
        'hp': short(num(props, 'Health')),
        'mn': short(num(props, 'Mana')),
        'pp': short(num(props, 'PowerPipChance')),
        'sp': short(num(props, 'ShadowPipRating')),
        'am': short(num(props, 'Archmastery')),
        'ho': short(num(props, 'OutgoingHealBoost')),
        'hi': short(num(props, 'IncomingHealBoost')),
        'st': short(num(props, 'StunResist')),
        'ds': short(num(props, 'DeckSize')),
        'mc': short(num(props, 'MaxCopies')),
        'sb': short(num(props, 'Sideboard')),
        'gd': short(num(props, 'GlobalDamage')),
        'gc': short(num(props, 'GlobalCritical')),
        'gcb': short(num(props, 'GlobalCriticalBlock')),
        'acb': short(num(props, 'AllCriticalBlock')),
        'gpa': 0,
        'pa': 0,
        'gr': short(num(props, 'GlobalResist')),
        'ga': short(num(props, 'GlobalAccuracy')),
        'gpc': 0,
        'pc': 0,
        'sch': sch,
        'so': socket_shapes(props),
        'pi': pin_shapes(props),
        'src': source_mask(props, name),
        'w': worlds_of(props),
        'tr': 1 if config.as_bool(props.get('Trade')) else 0,
        'au': 1 if config.as_bool(props.get('Auction')) else 0,
        'seas': is_seasonal(name),
    }


def stat_sig(it):
    return (it.get('hp'), it.get('mn'), it.get('pp'), it.get('sp'), it.get('am'),
            it.get('ho'), it.get('hi'), it.get('st'), it.get('ds'), it.get('mc'),
            it.get('sb'), tuple(sorted((it.get('sch') or {}).items())))


def drop_phantom_bases(items):
    by = {it['n']: it for it in items}
    drop = set()
    for it in items:
        if re.search(r'\(Level \d+\+?\)$', it['n']):
            continue
        sib = by.get(f"{it['n']} (Level {int(it['l'])}+)")
        if not sib:
            continue
        if (sib['t'] == it['t'] and sib['s'] == it['s'] and sib['l'] == it['l']
                and stat_sig(sib) == stat_sig(it)):
            drop.add(it['n'])
    return [it for it in items if it['n'] not in drop], len(drop)


def main():
    ap = argparse.ArgumentParser(description='Build the standalone v2 planner.')
    ap.add_argument('--db', default=str(DATA_DIR / 'items'),
                    help='SQLite DB or directory of split .db.gz parts')
    ap.add_argument('--gems', default=str(PROCESSED_DIR / 'gems.json'))
    ap.add_argument('--pins', default=str(PROCESSED_DIR / 'pins.json'))
    ap.add_argument('--base', default=str(PROCESSED_DIR / 'base_stats.json'))
    ap.add_argument('--template', default=str(Path(__file__).with_name('app_template.html')))
    ap.add_argument('--out', default=str(Path(__file__).with_name('dist') / 'wizard101_build_v2.html'))
    args = ap.parse_args()
    if not Path(args.db).exists():
        ap.error(f'data not found: {args.db} (pass --db /path/to/wizard101_items.db or data/items)')

    t0 = time.time()
    global RAID_NAMES
    RAID_NAMES = load_raid_names()
    print(f'raid names: {len(RAID_NAMES)}')
    items = []
    skipped = 0
    for name, itype, school, level, blob in iter_item_rows(args.db):
        if itype not in TYPES:
            skipped += 1
            continue
        items.append(payload(name, itype, school, level, json.loads(blob)))
    items, phantoms = drop_phantom_bases(items)
    print(f'phantoms: {phantoms} base-name duplicates removed')

    data = {
        'generated': time.strftime('%Y-%m-%d %H:%M'),
        'schools': list(GAME_SCHOOLS),
        'types': list(TYPES),
        'weights': config.DEFAULT_WEIGHTS,
        'sources': SOURCES,
        'worlds': sorted({w for it in items for w in it['w']}),
        'base': {},
        'gems': (json.load(open(args.gems, encoding='utf-8'))
                 if os.path.exists(args.gems) else []),
        'pins': (json.load(open(args.pins, encoding='utf-8'))
                 if os.path.exists(args.pins) else []),
        'items': items,
    }
    if os.path.exists(args.base):
        with open(args.base, encoding='utf-8') as f:
            data['base'] = json.load(f)
    blob = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    blob = blob.replace('</', '<\\/')          # safe inside <script>

    with open(args.template, encoding='utf-8') as f:
        html = f.read()
    html = html.replace('/*__DATA__*/', blob)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'items   : {len(items)} ({skipped} non-gear skipped)')
    print(f'payload : {len(blob)/1024/1024:.1f} MB')
    print(f'wrote   : {args.out}  ({len(html)/1024/1024:.1f} MB) in {time.time()-t0:.1f}s')


if __name__ == '__main__':
    main()
