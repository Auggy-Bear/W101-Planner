# Finding items you have not captured yet

The 2026-11-17 pull brought the database's newest captured edit to
**2026-11-15**. Anything created or edited after that date is missing. Refresh
the number any time with:

```powershell
.\.venv\Scripts\python.exe new_items.py --cutoff
```

## 1. Run this in the wiki page

Open <https://wiki.wizard101central.com/wiki/Special:Ask> and use:

**Query** — all on one line, including the `|sort` and `|order`:

```
[[ItemName::+]][[Modification date::>2026-11-15]]|sort=Modification date|order=desc
```

**Additional data to display** — paste the whole of `printouts.txt`
(149 lines, every one starting with `?`). That is every property the app knows
about, plus `Modification date`.

> **Common mistake:** `|sort=` and `|order=` belong in the **Query** box, not in
> *Additional data to display*. That box only accepts `?PropertyName` lines. If
> you put sort directives there, the query still runs but returns names only and
> the RDF/CSV/JSON export contains nothing but the item name.

**LIMIT** — `5000`. If the wiki caps it at 500, page through with `offset`.

**Format as** — RDF export (the `RDF` link in the results header).

Save each page into `Data Dump\new\` with any name ending `.rdf` or `.xml`.
`make_urls.py` can generate the paginated URLs from the RDF link.

> The modification date filter catches **edited** items as well as new ones. That
> is intentional: the local step below separates genuinely new items from changed
> ones.

## 2. See only what is new

```powershell
.\.venv\Scripts\python.exe new_items.py "Data Dump\new" --out new_items.csv
```

It prints the count and names, then writes `new_items.csv` and `new_items.xlsx`
with **every property** for each item not already in `wizard101_items.db`.

Useful flags:

| Flag | Effect |
|---|---|
| `--changed` | also list existing items whose properties changed |
| `--ingest` | merge the export into the database after reporting |
| `--cutoff` | print the current modification-date cutoff |

After ingesting, run `--cutoff` again and use the new date for next time.

## Why you must list the properties

`Special:Ask`'s RDF export only contains the **printouts you ask for** — it does
not dump every property the way the old `Special:ExportRDF` did. `printouts.txt`
holds all 148 known properties, so new items arrive fully populated. If the wiki
introduces a brand-new property later, it will not appear until you add it to
`printouts.txt`.

## If the result is enormous

A long gap can be tens of thousands of items. The 2026-11-17 pull used 8 pages (4,000 rows) and found 3,198 new items; if more were changed, keep paging past offset 4000. Options:

- Narrow the date, e.g. `[[Modification date::>2026-06-01]]`.
- Pull with `LIMIT 5000` and page through offsets; `new_items.py` accepts a whole
  folder and de-duplicates by item URI.
- Sort by `Modification date` descending so the newest pages are the ones you
  pull first.

## Troubleshooting the RDF/JSON link

If clicking `RDF` or `JSON` does nothing or is blocked:

1. **Right-click the link -> Save link as...** instead of left-clicking. Chrome
   sometimes blocks a download that opens in a new tab.
2. Check the address bar for a **blocked-download icon** and choose "Allow".
3. Try the **CSV** link instead of RDF; it is the same data as a flat table.
4. If an ad/tracker blocker is running, disable it for this site - some block
   URLs containing `format=rdf`.
5. Test with **LIMIT 20** first. A 5,000-row RDF with 149 printouts is a large
   response and can time out; once a small export works, raise the limit.

Tell me the exact message you get if none of those work - "blocked" can mean a
popup block, a Cloudflare challenge, or a server timeout, and each has a
different fix.


## If RDF/JSON downloads are blocked

Save each results page instead: **Ctrl+S -> "Webpage, HTML Only"** into
`Data Dump\New Since 2025-11-02\` (any name). Then:

```powershell
.\.venv\Scripts\python.exe ingest_ask_html.py "Data Dump\New Since 2025-11-02"
```

It reads the `smwtable` from each saved page, maps the 150 columns by their
property class, handles `<br>`-separated multi-values, and merges results into
`wizard101_items.db` (new items inserted, existing ones merged by name).

Add `--dry-run` first to see the counts without writing. The 2026-11-17 pull of
8 pages (4,000 rows) added 3,198 new items and updated 802 existing ones.


## Coverage check - 2026-11-17 pull

20 result pages were saved (10,000 rows, **7,503 unique items**):

- descending: pages 1-5500, covering **2026-04-09 .. 2026-11-15**
- ascending: pages 498-5500, covering **2025-11-25 .. 2026-05-30**
- the two directions overlap (2026-04-09 .. 2026-05-30), so they join cleanly

Both gaps are now closed with `1-497 asc` and `2501-3000 asc`. Coverage runs
continuously from **2025-11-02 00:25** to **2026-11-15 20:40** with zero gaps.

The final ingest added **701 new items** (22 pages, 8,233 unique), bringing the
database to **51,697**. `ingest_ask_html.py` is idempotent, so re-running over the
whole folder is safe.
