"""Compile the Pins capture into pins.json / pins_catalog.csv."""
import csv
import glob
import html
import json
import os
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
ROOT = BASE / 'data' / 'raw' / 'Jewels' / 'Pins'
OUT = BASE / 'data' / 'processed'
OUT.mkdir(parents=True, exist_ok=True)
EFFECT_MAP = {
    'Accuracy-Boosting Pins': 'Accuracy',
    'Armor Piercing-Boosting Pins': 'Armor Piercing',
    'Critical Block-Boosting Pins': 'Critical Block',
    'Critical-Boosting Pins': 'Critical',
    'Damage-Boosting Pins': 'Damage',
    'Outgoing Healing-Boosting Pins': 'Outgoing Healing',
    'Pip Conversion-Boosting Pins': 'Pip Conversion',
    'Resistance-Boosting Pins': 'Resistance',
}
SOURCE_BITS = {'Bought': (1 << 3, 'Bought'), 'Crafted': (1 << 2, 'Crafted'),
               'Dropped': (1 << 1, 'Dropped'), 'Fished': (1 << 5, 'Fished'),
               'Gardened': (1 << 10, 'Gardened'), 'Gift Card': (1 << 6, 'Gift Card'),
               'Item Granted': (1 << 0, 'Item Granted'), 'Quest Reward': (1 << 4, 'Quest Reward'),
               'Special Events': (1 << 8, 'Special Events')}
SCHOOLS = ['Balance', 'Death', 'Fire', 'Ice', 'Life', 'Myth', 'Storm', 'Shadow']
SUFFIX = {'Accuracy': 'a', 'ArmorPiercing': 'p', 'CriticalBlock': 'b', 'Critical': 'c',
          'FlatDamage': 'f', 'Damage': 'd', 'FlatResist': 'fr', 'Resist': 'r',
          'PipConversion': 'pc', 'OutgoingHealing': 'ho'}
META = {'', 'Category', 'Level', 'School', 'PowerPins', 'SwordPins', 'ShieldPins'}


def parse():
    out = []
    heads = None
    for path in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        text = open(path, encoding='utf-8', errors='replace').read()
        m = re.search(r'<table\b[^>]*class="[^"]*smwtable[^"]*"[^>]*>', text)
        if not m:
            continue
        chunk = text[m.start():text.find('</table>', m.start())]
        heads = [html.unescape(re.sub(r'<[^>]+>', '', h)).strip()
                 for h in re.findall(r'<th\b[^>]*>(.*?)</th>', chunk, re.S)]
        for row in re.findall(r'<tr\b.*?</tr>', chunk, re.S):
            cells = re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.S)
            if not cells:
                continue
            vals = []
            for c in cells:
                if 'Category:' in c:
                    anchors = re.findall(r'<a\b[^>]*>(.*?)</a>', c, re.S)
                    vals.append([html.unescape(re.sub(r'<[^>]+>', '', a)).strip() for a in anchors])
                else:
                    vals.append(html.unescape(re.sub(r'<[^>]+>', '', c)).strip())
            out.append(dict(zip(heads, vals)))
    return heads or [], out


def effect_of_prop(prop, raw):
    school = 'Any'
    name = prop
    if prop.startswith('Global'):
        name = prop[6:]
    else:
        for s in SCHOOLS:
            if prop.startswith(s):
                school = s
                name = prop[len(s):]
                break
    stat = SUFFIX.get(name)
    m = re.search(r'([+-]?\d+(?:\.\d+)?)', str(raw).replace('\xa0', ' '))
    if stat is None or m is None:
        return None
    return {'stat': stat, 'school': school, 'value': float(m.group(1)),
            'pct': '%' in str(raw)}


heads, rows = parse()
stat_cols = [h for h in heads if h not in META]
pins = []
for r in rows:
    cats = r.get('Category', [])
    pshape = next((s.replace(' Pins', '') for s in ['Power Pins', 'Sword Pins', 'Shield Pins'] if s in cats), '')
    eff = next((v for k, v in EFFECT_MAP.items() if k in cats), '')
    effects = []
    for h in stat_cols:
        if r.get(h):
            e = effect_of_prop(h, r[h])
            if e:
                effects.append(e)
    src = 0
    labels = []
    for label, (bit, name) in SOURCE_BITS.items():
        if label in cats:
            src |= bit
            labels.append(name)
    if not src:
        src |= 1 << 9
        labels = ['Unknown']
    pins.append({
        'name': r.get('', ''),
        'level': int(float(r['Level'])) if str(r.get('Level', '')).strip().isdigit() else None,
        'school': r.get('School') or 'Any',
        'shape': pshape,
        'effect': eff,
        'effects': effects,
        'src': src,
        'sources': labels,
        'no_auction': 'No Auction Jewels' in cats,
        'categories': cats,
        'stats': {h: re.sub(r'\s+', '', r[h].replace('\xa0', ' ')) for h in stat_cols if r.get(h)},
    })

pins.sort(key=lambda p: (p['shape'], p['school'], p['name']))
json.dump(pins, open(OUT / 'pins.json', 'w', encoding='utf-8'), indent=1)

with open(OUT / 'pins_catalog.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Name', 'Shape', 'Effect', 'School', 'Level', 'No Auction', 'Sources', 'Effects', 'Stats', 'Categories'])
    for p in pins:
        w.writerow([p['name'], p['shape'], p['effect'], p['school'], p['level'],
                    'yes' if p['no_auction'] else '', '; '.join(p['sources']),
                    '; '.join(f"{e['stat']}:{e['school']}={e['value']}{'%' if e['pct'] else ''}" for e in p['effects']),
                    '; '.join(f'{k}={v}' for k, v in p['stats'].items()), '; '.join(p['categories'])])

print('pins:', len(pins))
print('by shape:', dict(Counter(p['shape'] for p in pins)))
print('by effect:', dict(Counter(p['effect'] for p in pins)))
print('with effects:', sum(1 for p in pins if p['effects']))
print('effect rows:', dict(Counter(e['stat'] for p in pins for e in p['effects'])))
