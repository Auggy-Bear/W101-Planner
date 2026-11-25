"""Small shared configuration and parsing helpers for the v2 builder.

The interactive app owns its priority order. These weights are only the initial
payload defaults; the old Excel-oriented priority.py is not needed to build v2.
"""
from __future__ import annotations

import math

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


def num(value):
    """Coerce wiki values (numbers, numeric strings, booleans) to a finite float."""
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else 0.0
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def as_bool(value):
    """Interpret the wiki's boolean-ish strings."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ('true', 'yes', '1')
    return bool(value)
