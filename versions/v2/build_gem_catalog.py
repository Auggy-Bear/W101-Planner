"""Compile gear jewels from the single All table, using categories for
shape/source/effect and names for the numeric value."""
import csv
import glob
import html
import json
import os
import re
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
ROOT = BASE / 'data' / 'raw' / 'Jewels' / 'All'
OUT = BASE / 'data' / 'processed'
OUT.mkdir(parents=True, exist_ok=True)
SHAPE_CAT = {'Circle-Shaped Jewels': 'Circle', 'Square-Shaped Jewels': 'Square',
             'Triangle-Shaped Jewels': 'Triangle', 'Tear-Shaped Jewels': 'Tear'}
EFFECT_MAP = {
    'Accuracy-Boosting Jewels': ('a', 'Accuracy'),
    'Archmastery-Boosting Jewels': ('am', 'Archmastery'),
    'Armor Piercing-Boosting Jewels': ('p', 'Armor Piercing'),
    'Critical Block-Boosting Jewels': ('b', 'Critical Block'),
    'Critical-Boosting Jewels': ('c', 'Critical'),
    'Damage-Boosting Jewels': ('d', 'Damage'),
    'Energy-Boosting Jewels': ('en', 'Energy'),
    'Flat Damage-Boosting Jewels': ('f', 'Flat Damage'),
    'Flat Resistance-Boosting Jewels': ('fr', 'Flat Resistance'),
    'Health-Boosting Jewels': ('hp', 'Health'),
    'Incoming Heal-Boosting Jewels': ('hi', 'Incoming Heal'),
    'Mana-Boosting Jewels': ('mn', 'Mana'),
    'Outgoing Heal-Boosting Jewels': ('ho', 'Outgoing Heal'),
    'Pip Conversion-Boosting Jewels': ('pc', 'Pip Conversion'),
    'Power Pip-Boosting Jewels': ('pp', 'Power Pip'),
    'Shadow Pip-Boosting Jewels': ('sp', 'Shadow Pip'),
    'Stun Resistance-Boosting Jewels': ('st', 'Stun Resistance'),
}
SOURCE_BITS = {
    'Bought Jewels': (1 << 3, 'Bought'),
    'Crafted Jewels': (1 << 2, 'Crafted'),
    'Dropped Jewels': (1 << 1, 'Dropped'),
    'Fished Jewels': (1 << 5, 'Fished'),
    'Gardened Jewels': (1 << 10, 'Gardened'),
    'Gift Card Jewels': (1 << 6, 'Gift Card'),
    'Item Granted Jewels': (1 << 0, 'Item Granted'),
    'Quest Reward Jewels': (1 << 4, 'Quest Reward'),
    'Special Events Jewels': (1 << 8, 'Special Events'),
}
UNKNOWN = 1 << 9


def rows():
    out = []
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
    return out


gems = []
skipped = []
for r in rows():
    cats = r.get('Category', [])
    shape = next((v for k, v in SHAPE_CAT.items() if k in cats), None)
    if not shape:
        continue
    name = r.get('')
    eff = None
    for cat, (stat, label) in EFFECT_MAP.items():
        if cat in cats:
            eff, stat = label, stat
            break
    if eff is None:
        if re.search(r'\bPiercing\b', name, re.I):
            eff, stat = 'Armor Piercing', 'p'
        elif re.search(r'\bConversion\b', name, re.I):
            eff, stat = 'Pip Conversion', 'pc'
    mval = re.search(r'\+(\d+(?:\.\d+)?)\s*(%)?', name)
    if eff is None or mval is None:
        skipped.append(name)
        continue
    pct = bool(mval.group(2))
    src = 0
    labels = []
    for cat, (bit, label) in SOURCE_BITS.items():
        if cat in cats:
            src |= bit
            labels.append(label)
    if not src:
        src = UNKNOWN
        labels = ['Unknown']
    gems.append({
        'name': name,
        'shape': shape,
        'school': r.get('School') or 'Any',
        'level': int(float(r['Level'])) if str(r.get('Level', '')).strip().isdigit() else None,
        'effect': eff,
        'stat': stat,
        'value': float(mval.group(1)),
        'pct': pct,
        'src': src,
        'sources': labels,
        'na': 'No Auction Jewels' in cats,
    })

gems.sort(key=lambda g: (g['shape'], g['school'], g['name']))
json.dump(gems, open(OUT / 'gems.json', 'w', encoding='utf-8'), indent=1)
with open(OUT / 'gem_catalog.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['Name', 'Shape', 'School', 'Level', 'Effect', 'Stat', 'Value', 'Percent', 'No Auction', 'Sources'])
    for g in gems:
        w.writerow([g['name'], g['shape'], g['school'], g['level'], g['effect'], g['stat'],
                    g['value'], 'yes' if g['pct'] else '', 'yes' if g['na'] else '',
                    '; '.join(g['sources'])])
print('gems:', len(gems), 'skipped:', len(skipped))
print('by stat:', dict(Counter(g['stat'] for g in gems)))
print('by shape:', dict(Counter(g['shape'] for g in gems)))
