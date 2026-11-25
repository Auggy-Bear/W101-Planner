# Manual sync — no browser automation

For when automation is off the table. You drive the browser; the scripts only
build the URLs, verify what came back, and merge it into the database.

Everything here is sequential and human-paced. Roughly **10 page loads** for a
full refresh if `limit=5000` works, ~91 if the wiki caps at 500.

---

## 1. Test whether the 500 cap is real

1. Open <https://wiki.wizard101central.com/wiki/Special:Ask>
2. **Query** box:
   ```
   [[ItemName::+]]|sort=ItemName|order=asc
   ```
3. **Additional data to display** — paste the whole of `printouts.txt`
   (148 lines, each starting with `?`).
4. Set **LIMIT** to `5000`.
5. Click **Find results**.

Read the line above the table:

- `Results 1 – 5000` → the cap is only the form default. You're done in ~10 pulls.
- `Results 1 – 500` (or similar) → the server caps it. Use `--limit 500` from
  here on; same workflow, ~91 pulls. Consider splitting by `?ItemType` to keep
  each series short.

Also check one row has the full property set, not just a name. If the table
shows only one column, the printout box didn't take — re-paste `printouts.txt`
and submit again before going further.

## 2. Capture the RDF link

Right-click the **RDF** link in `(JSON | CSV | RSS | RDF)` → **Copy link
address**. Paste it into `rdf_link.txt` (one line, nothing else).

That link encodes the query, the 148 printouts and the format. Everything else
is derived from it.

## 3. Generate the URL list

```powershell
.\.venv\Scripts\python.exe make_urls.py --limit 5000
```

Writes `urls.txt` and `capture_plan.csv`. Each line differs only in `offset`.

## 4. Pull each page

For every URL in `urls.txt`:

1. Paste it into the address bar.
2. The RDF renders in Chrome's XML viewer (or downloads — either is fine).
3. **Ctrl+S** and save into `test\` using the name from `capture_plan.csv`
   (`ask_000000.xml`, `ask_005000.xml`, …). If Chrome downloads it instead, move
   the file into `test\` and rename it.
4. **Stop when a page returns fewer rows than your limit** — that's the end.

Do not rename the files to anything that sorts oddly; the verifier doesn't care
about order, only content.

## 5. Verify before importing

```powershell
.\.venv\Scripts\python.exe ingest_pages.py test
```

Look for:

- `property counts: {148: N}` — every page should carry all 148 properties.
- `duplicates` — should be near zero. A big number means pagination drifted;
  see Troubleshooting.
- `page sizes` — only the last page should be short.

## 6. Import

```powershell
.\.venv\Scripts\python.exe ingest_pages.py test --db wizard101_items.db
```

Updates are merged, so a partial page can't erase a full record.

Then check nothing went missing against the snapshot taken before the pull:

```powershell
.\.venv\Scripts\python.exe compare_names.py names_before.txt
```

`missing` should be 0 (or a handful of genuinely deleted items). A large
`missing` count means a chunk was skipped — re-pull that offset range.

## 7. Rebuild the workbook

```powershell
.\.venv\Scripts\python.exe export_excel.py --db wizard101_items.db --out wizard101_priority.xlsx
```

---

## Deltas from now on

Change the query to add a modification filter:

```
[[ItemName::+]][[Modification date::>2026-11-01]]|sort=ItemName|order=asc
```

Run it once, copy the new RDF link, `make_urls.py --limit 5000 --pages 1`, and
pull that single page. Items already known that didn't change are reported as
`unchanged` and cost nothing.

---

## Troubleshooting

**Table shows only one column.** The printout box didn't submit. Paste
`printouts.txt` last, then click *Find results* again.

**RDF renders as a huge tree and Ctrl+S saves `.html`.** Use *Save page as* and
pick "XML" / "Webpage, XML only", or check the Downloads folder. You can also
append `&sep=,` and use the CSV export instead, but RDF keeps datatypes and
multi-value fields intact.

**`limit=5000` silently becomes 500.** The cap is real. Re-run
`make_urls.py --limit 500`; the offsets regenerate accordingly.

**Duplicate items across pages.** Pagination drifted. Add `|sort=ItemName|order=asc`
to the query (it makes ordering deterministic) and re-pull from the first
affected offset.

**`ingest_pages.py` says 0 new.** Those items already exist and are unchanged —
that's the incremental merge working.
