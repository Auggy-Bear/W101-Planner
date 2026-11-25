# v1 — original planner

Legacy gear-only planner, retained for comparison and history. Open
`dist/wizard101_build.html`.

It predates gems, pins, the 0–100 normalized score, raid filtering, anomaly
removal and duplicate badges. Use v2 for current work.

## Build

```powershell
python build_app.py
```

`priority.py` is the original Excel-oriented scoring/weight module used by this
builder. `base_stats.json` is version-local. `db_reader.py` reads the split
`data/items/` parts by default.

Output: `dist/wizard101_build.html`.
