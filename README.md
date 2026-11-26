# Wizard101 Build Planner

A standalone, single-file build planner for Wizard101 gear. Version 2 supersedes
v1 and incorporates its functionality.

Everything runs locally in the browser from one HTML file. No server, no network
requests.

## Quick start

Open:

`versions/v2/dist/wizard101_build_v2.html`

The GitHub Pages entry point is `index.html`, which redirects there.

## Repository layout

```
versions/
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
  merge_database.py  rebuilds a full SQLite DB from the parts
```

## Rebuild v2

```powershell
cd versions/v2
python build_app.py
```

The builder defaults to `data/items` and the processed gem/pin/base files. It
accepts `--db`, `--gems`, `--pins`, `--base`, `--template` and `--out`.

## Data

The full database is split into **eight compressed per-type parts** under
`data/items/`. They total **49.3 MB** and the largest is **9.2 MB**, so every file
can be uploaded through GitHub's web UI.

The builders read the parts directly. To reconstruct a single SQLite file:

```powershell
python tools/merge_database.py
```

The original 376 MB database is not needed. See [data/README.md](data/README.md).

## GitHub Pages

`index.html` redirects to the v2 build:

`https://auggy-bear.github.io/W101-Planner/`

Pages should serve from `main` / `/ (root)`.

## History

v1 has been retired. [versions/v2/V2_NON_GEM_FIXES.md](versions/v2/V2_NON_GEM_FIXES.md)
documents what changed from v1 to v2.
