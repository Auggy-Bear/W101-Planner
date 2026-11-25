"""Configurable priority scoring for Wizard101 items.

Items are ranked per *player school*: a universal ("Any") wand that gives Storm,
Ice and Death damage produces one ranking row for each of those schools, while a
Life-only robe is ranked only for Life.  Within a peer group (ItemType x 10-level
band x School) every stat becomes a percentile rank 0-100 and is averaged using
the weights in priority_weights.json.

Stat names mirror the in-game character panel: damage % and flat damage are kept
apart (the old model added "+35" to "117%"), and shadow pip rating, archmastery,
stun resistance, pip conversion and power pips are first-class components.
"""
from __future__ import annotations

import bisect
import json
import math
import os
from collections import defaultdict

SCHOOLS = ('Life', 'Death', 'Fire', 'Ice', 'Myth', 'Storm', 'Balance', 'Shadow')
UNIVERSAL = 'Universal'

DEFAULT_WEIGHTS = {
    'Damage': 0.25,
    'Resist': 0.17,
    'Critical': 0.14,
    'Block': 0.10,
    'Health': 0.08,
    'Pierce': 0.09,
    'Deck': 0.08,
    'Accuracy': 0.04,
    'FlatDamage': 0.02,
    'ShadowPip': 0.03,
    'StunResist': 0.00,
    'Heal': 0.00,
    'PowerPips': 0.00,
    'PipConversion': 0.00,
    'Value': 0.00,
}

DEFAULT_CONFIG = {
    'level_band': 10,
    'group_by': ['ItemType', 'LevelBand', 'School'],
    'weights': DEFAULT_WEIGHTS,
}

COMPONENT_PROPS = {
    'Damage': 'SchoolDamage + GlobalDamage',
    'FlatDamage': 'SchoolFlatDamage',
    'Resist': 'SchoolResist + GlobalResist',
    'Critical': 'SchoolCritical + GlobalCritical',
    'Block': 'SchoolCriticalBlock + GlobalCriticalBlock + AllCriticalBlock',
    'Pierce': 'ArmorPiercing + SchoolArmorPiercing + GlobalArmorPiercing',
    'Accuracy': 'SchoolAccuracy + GlobalAccuracy',
    'Health': 'Health',
    'Deck': 'DeckSize + 3 x MaxCopies + Sideboard',
    'ShadowPip': 'ShadowPipRating',
    'StunResist': 'StunResist',
    'Heal': 'OutgoingHealBoost + IncomingHealBoost',
    'PowerPips': 'PowerPipChance',
    'PipConversion': 'PipConversion + SchoolPipConversion + GlobalPipConversion',
    'Value': 'VendorSellPrice',
}

SCHOOL_STAT_SUFFIXES = ('Damage', 'FlatDamage', 'Resist', 'Critical',
                        'CriticalBlock', 'Accuracy', 'ArmorPiercing', 'PipConversion')
UNIVERSAL_KEYS = ('Health', 'Mana', 'Energy', 'GlobalDamage', 'GlobalResist',
                  'GlobalCritical', 'GlobalCriticalBlock', 'GlobalAccuracy',
                  'GlobalArmorPiercing', 'GlobalPipConversion', 'PowerPipChance',
                  'Archmastery', 'OutgoingHealBoost', 'IncomingHealBoost',
                  'StunResist', 'ShadowPipRating', 'ShadowPipChance',
                  'DeckSize')

# Short labels used in the workbook, in the same order as the game panel.
STAT_LABELS = [
    ('Health', 'Health'),
    ('Damage', 'Damage %'),
    ('FlatDamage', 'Flat Damage +'),
    ('Resist', 'Resist %'),
    ('Critical', 'Critical'),
    ('Block', 'Block'),
    ('Pierce', 'Pierce %'),
    ('Accuracy', 'Accuracy %'),
    ('StunResist', 'Stun Resist %'),
    ('HealOut', 'Healing Out %'),
    ('HealIn', 'Healing In %'),
    ('PowerPips', 'Power Pips %'),
    ('PipConversion', 'Pip Conversion'),
    ('ShadowPip', 'Shadow Pip Rating'),
    ('Archmastery', 'Archmastery'),
]


def num(v):
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    if isinstance(v, (int, float)):
        f = float(v)
        return f if math.isfinite(f) else 0.0
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return 0.0
    if isinstance(v, list):
        return sum(num(x) for x in v)
    return 0.0


def dsum(*vals):
    """Sum distinct non-zero values (the wiki repeats one stat in several properties)."""
    seen = set()
    total = 0.0
    for v in vals:
        if v and v not in seen:
            seen.add(v)
            total += v
    return total


def as_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in ('true', 'yes', '1')
    return bool(v)


def first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def level_band(level, width):
    if level is None:
        return 'Unknown'
    try:
        lv = int(float(level))
    except (TypeError, ValueError):
        return 'Unknown'
    lo = (lv // width) * width
    return f'{lo}-{lo + width - 1}'


def normalize_family(school_vals, generic, universal, own):
    universal_dup = bool(universal and generic and abs(universal - generic) < 1e-9)
    owners = [k for k, v in school_vals.items() if v and generic and abs(v - generic) < 1e-9]
    if universal_dup:
        owner = None
    elif not generic:
        owner = None
    elif owners:
        owner = own if own in owners else owners[0]
    elif own in SCHOOLS:
        owner = own
    else:
        owner = None

    univ = 0.0
    if universal and not universal_dup:
        matches = any(v and abs(v - universal) < 1e-9 for v in school_vals.values())
        if not matches:
            univ = universal

    out = {}
    for k in SCHOOLS:
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


def _family_value(props, school, suffix):
    vals = {k: num(props.get(f'{k}{suffix}')) for k in SCHOOLS}
    out = normalize_family(vals, num(props.get(suffix)),
                           num(props.get(f'Global{suffix}')),
                           school if school in SCHOOLS else None)
    return out.get(school, 0.0) if school in SCHOOLS else 0.0


def components(props, school):
    s = school if school in SCHOOLS else ''
    g = lambda k: num(props.get(k))
    return {
        'Damage': dsum(g(f'{s}Damage'), g('GlobalDamage')),
        'FlatDamage': g(f'{s}FlatDamage'),
        'Resist': dsum(g(f'{s}Resist'), g('GlobalResist')),
        'Critical': dsum(g(f'{s}Critical'), g('GlobalCritical')),
        'Block': dsum(g(f'{s}CriticalBlock'), g('GlobalCriticalBlock'),
                      g('AllCriticalBlock')),
        'Pierce': _family_value(props, school, 'ArmorPiercing'),
        'Accuracy': dsum(g(f'{s}Accuracy'), g('GlobalAccuracy')),
        'Health': g('Health'),
        'Deck': g('DeckSize') + 3 * g('MaxCopies') + g('Sideboard'),
        'ShadowPip': g('ShadowPipRating'),
        'StunResist': g('StunResist'),
        'Heal': g('OutgoingHealBoost') + g('IncomingHealBoost'),
        'PowerPips': g('PowerPipChance'),
        'PipConversion': _family_value(props, school, 'PipConversion'),
        'Value': g('VendorSellPrice'),
    }


def variant_schools(item):
    """Which player schools this item can meaningfully be ranked for."""
    school = first(item.get('school')) or 'None'
    if school in SCHOOLS:
        return [school]          # school-locked gear: only its own school can wear it
    props = item['props']
    served = [s for s in SCHOOLS
              if any(num(props.get(f'{s}{suffix}')) > 0 for suffix in SCHOOL_STAT_SUFFIXES)]
    if any(num(props.get(k)) > 0 for k in UNIVERSAL_KEYS) or not served:
        served.append(UNIVERSAL)
    return served


def _percentiles(values):
    order = sorted(values)
    n = len(order)
    if n <= 1:
        return [50.0] * n
    return [100.0 * bisect.bisect_right(order, v) / n for v in values]


def score_items(items, config=None):
    """Return a list of ranking *views*: one per (item, player school) pair."""
    cfg = dict(DEFAULT_CONFIG)
    if config:
        cfg.update(config)
    weights = cfg.get('weights') or DEFAULT_WEIGHTS
    width = int(cfg.get('level_band', 10))
    group_by = cfg.get('group_by') or DEFAULT_CONFIG['group_by']

    views = []
    for it in items:
        band = level_band(it.get('level'), width)
        for school in variant_schools(it):
            comps = components(it['props'], school)
            views.append({
                'item': it,
                'name': it.get('name'),
                'item_type': it.get('item_type') or 'Unknown',
                'school': school,
                'band': band,
                'level': it.get('level'),
                'uri': it.get('uri'),
                'comps': comps,
            })

    groups = defaultdict(list)
    for v in views:
        key = {'ItemType': v['item_type'], 'LevelBand': v['band'], 'School': v['school']}
        gk = tuple(key[k] for k in group_by)
        v['group_key'] = ' | '.join(str(x) for x in gk)
        groups[gk].append(v)

    for members in groups.values():
        active = []
        for comp in weights:
            vals = [m['comps'].get(comp, 0.0) for m in members]
            if len(members) < 3 or max(vals) - min(vals) <= 1e-12:
                continue
            for m, p in zip(members, _percentiles(vals)):
                m.setdefault('pct', {})[comp] = p
            active.append(comp)

        wsum = sum(weights.get(c, 0.0) for c in active)
        for m in members:
            for c in COMPONENT_PROPS:
                m[f'stat_{c}'] = round(m['comps'].get(c, 0.0), 2)
            m['scored'] = any(m['comps'].get(c, 0.0) > 0 for c in
                              ('Damage', 'FlatDamage', 'Critical', 'Pierce', 'Resist',
                               'Block', 'Health', 'Deck', 'ShadowPip', 'StunResist',
                               'Heal', 'PowerPips', 'PipConversion'))
            if not active or wsum <= 0:
                # Fewer than 3 peers, or every comparable stat is constant:
                # a percentile would be meaningless, so leave it unranked.
                m['score'] = None
                m['active'] = []
                for c in weights:
                    m[f'pct_{c}'] = None
                continue
            pct = m.get('pct', {})
            m['score'] = round(sum(weights.get(c, 0.0) * pct.get(c, 0.0)
                                   for c in active) / wsum, 2)
            m['active'] = active
            for c in weights:
                m[f'pct_{c}'] = round(pct.get(c, 0.0), 1) if c in active else None

    for members in groups.values():
        ranked = [m for m in members if m['score'] is not None]
        ranked.sort(key=lambda x: (-x['score'], -(x['comps'].get('Damage', 0)),
                                   x['name'] or ''))
        n = len(ranked)
        for i, m in enumerate(ranked, 1):
            m['rank'] = i
            m['group_size'] = n
            frac = 1.0 - (i - 1) / max(n, 1)
            m['tier'] = ('S' if frac >= 0.90 else 'A' if frac >= 0.70 else
                         'B' if frac >= 0.40 else 'C' if frac >= 0.15 else 'D')
        for m in members:
            if m['score'] is None:
                m['rank'] = None
                m['tier'] = '-'
                m['group_size'] = n

    return views


def load_config(path='priority_weights.json'):
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            user = json.load(f)
        cfg['level_band'] = user.get('level_band', cfg['level_band'])
        cfg['group_by'] = user.get('group_by', cfg['group_by'])
        w = dict(DEFAULT_WEIGHTS)
        w.update(user.get('weights', {}))
        cfg['weights'] = w
    return cfg
