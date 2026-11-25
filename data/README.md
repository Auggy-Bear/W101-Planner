# Data

All captures, the uploadable item database and derived catalogues live here,
separate from the app versions.

## Layout

```
items/
  manifest.json               row counts, sizes and SHA-256 per part
  amulet.db.gz ... wand.db.gz eight per-type SQLite parts, 3-9 MB each
raw/
  Jewels/All/                 9 Ask pages, all jewels
  Jewels/Pins/                3 Ask pages, all pins
  Raid/                       2 Ask pages, Category:Raid Items
  New Since 2025-11-02/       22 item pages for the item DB refresh window
  Base Values/base_table.txt  base-stat source table
processed/
  gems.json                   2,127 gear gems
  pins.json                   1,218 pins
  base_stats.json             level 1-180 base stats
  gem_catalog.csv             flat gem export
  pins_catalog.csv            flat pin export
reports/
  gear_anomalies.xlsx         phantom bases, duplicate-stat groups, raid list
  wizard101_jewels_pins.xlsx  full jewel/pin validation workbook
reference/
  jewel/pin query definitions, property lists, sync notes
```

## Uploadable database

`items/` is the full item database split by `item_type` and gzip-compressed. The
largest part is 9.2 MB, so each file can be uploaded through GitHub's web UI.

The app builders read the directory directly:

```powershell
cd versions/v2
python build_app.py
```

The uncompressed `wizard101_items.db` (~376 MB) is **not needed** for a normal
build and is not committed. If you need a single SQLite file, concatenate the
parts or keep the original locally and pass `--db /path/to/wizard101_items.db`.
`versions/*/db_reader.py` accepts either a DB file or the split directory.

To regenerate the parts after a database update:

```powershell
python tools/split_database.py --db /path/to/wizard101_items.db
```

## Refreshing catalogues

1. Capture wiki pages manually (the wiki blocks automated requests).
2. Save them under `raw/` using the query definitions in `reference/`.
3. Run the v2 builders.

The gem/pin builders read `raw/Jewels/All` and `raw/Jewels/Pins`. The app builder
also reads `raw/Raid` for the 866 raid-tagged items.

## Reports

The workbooks document:

- 112 phantom level-170 base duplicates removed from the app payload;
- 6,087 identical-stat groups (20,778 items);
- 866 raid items, all matched to the database.
