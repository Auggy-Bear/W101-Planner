# v2 — current planner

Single-file HTML build planner. Open `dist/wizard101_build_v2.html`.

## Features

- Eight gear slots with live item rankings and set totals.
- Gems and pins: auto-pick, manual assignment, visibility toggles and source
  filtering. Both default to the state that makes the displayed totals match the
  visible build.
- Normalized **0–100** set score, recomputed after the final build.
- Best in Slot with hard minimums, caps, priority weights and exact global
  verification for the gear-only/pins-only cases.
- Excluding a list item removes it from the equipped build and reruns Best in
  Slot if a result exists.
- Raid source (866 items), exclusive: unchecked Raid hides raid gear even when
  Crafted/Dropped also match.
- Duplicate-stat ⚠ badge, 112 phantom base items removed.
- Copy/Paste setup JSON for sharing priorities and constraints.

See [V2_NON_GEM_FIXES.md](V2_NON_GEM_FIXES.md) for the change list.

## Build

Requirements: Python 3.10+ (standard library only) and the item database.

```powershell
python build_gem_catalog.py
python build_pin_catalog.py
python build_app.py
```

Outputs:

- `dist/wizard101_build_v2.html`
- `../../data/processed/gems.json`
- `../../data/processed/pins.json`

Use `--db`, `--gems`, `--pins`, `--base`, `--template`, `--out` to override paths.

## Code map

| File | Purpose |
|---|---|
| `app_template.html` | UI and all client-side planner logic (inline CSS/JS) |
| `build_app.py` | Reads the SQLite items, builds the payload, injects it into the template |
| `build_gem_catalog.py` | Rebuilds `gems.json` from `data/raw/Jewels/All` |
| `build_pin_catalog.py` | Rebuilds `pins.json` from `data/raw/Jewels/Pins` |
| `config.py` | Initial priority weights and wiki-value coercion helpers |
| `db_reader.py` | Reads a single SQLite DB or the split `.db.gz` parts |
| `dist/` | Built standalone HTML |

`build_app.py` does not depend on the old Excel scorer. The interactive app owns
its priorities; `config.DEFAULT_WEIGHTS` is only the payload default. It reads
`data/items/` by default, so no 376 MB database is required.

## Data

Processed inputs live in `../../data/processed/`; raw captures in
`../../data/raw/`. The database is not committed; see
[../../data/README.md](../../data/README.md).

## Notes

- No automated wiki access. Captures are manual browser saves.
- All computation is local; the HTML makes no network requests.
