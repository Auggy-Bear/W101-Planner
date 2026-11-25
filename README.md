# Wizard101 Build Planner

Two standalone, single-file build planners for Wizard101 gear:

- **v2** — current planner with gems, pins, normalized 0–100 scoring, duplicate
  detection, raid filtering and setup sharing.
- **v1** — the original gear-only planner, kept for comparison and history.

Everything runs locally in the browser from one HTML file. No server, no build
step for the user, no network calls.

## Quick start

Open:

- `versions/v2/dist/wizard101_build_v2.html` — current
- `versions/v1/dist/wizard101_build.html` — legacy

## Repository layout

```
versions/
  v1/
    app_template.html
    build_app.py
    db_reader.py
    priority.py
    base_stats.json
    dist/wizard101_build.html
  v2/
    app_template.html
    build_app.py
    build_gem_catalog.py
    build_pin_catalog.py
    config.py
    db_reader.py
    dist/wizard101_build_v2.html
    V2_NON_GEM_FIXES.md
data/
  items/             8 gzipped per-item-type database parts + manifest
  raw/               saved wiki captures
  processed/         gems.json, pins.json, base_stats.json, CSVs
  reports/           anomaly and jewel/pin workbooks
  reference/         query definitions and capture notes
tools/
  split_database.py  splits a full SQLite DB into the per-type parts
```

## Rebuild v2

```powershell
cd versions/v2
python build_app.py
```

The builder defaults to `data/items` and the processed gem/pin/base files. It
accepts `--db`, `--gems`, `--pins`, `--base`, `--template` and `--out`.

For v1:

```powershell
cd versions/v1
python build_app.py
```

## Data upload

The full database is split into **eight compressed per-type parts** under
`data/items/`:

| Part | Size |
|---|---:|
| hat.db.gz | 9.2 MB |
| robe.db.gz | 9.1 MB |
| boots.db.gz | 9.0 MB |
| wand.db.gz | 8.2 MB |
| athame.db.gz | 3.7 MB |
| ring.db.gz | 3.6 MB |
| amulet.db.gz | 3.3 MB |
| deck.db.gz | 3.2 MB |

All are under 10 MB, so every file can be uploaded through GitHub's web UI. The
builders read them directly; the original 376 MB SQLite file is optional.

See [data/README.md](data/README.md).

## GitHub Pages

`index.html` redirects to the v2 build, so the Pages URL stays stable:

`https://auggy-bear.github.io/W101-Planner/`

Pages should serve from `main` / `/ (root)`.

## Version differences

See [versions/v2/V2_NON_GEM_FIXES.md](versions/v2/V2_NON_GEM_FIXES.md) for the
non-gem/non-pin changes in v2.
