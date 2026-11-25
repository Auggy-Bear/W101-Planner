# Version 2 — non-gem/non-pin changes vs version 1

## Scoring

- Set score is normalized **0–100**. The reference includes base stats, every
  legal item and its best socket potential, then applies the soft caps.
- The displayed score is recomputed **after** the final build is materialised,
  so it always matches the shown gear.
- Balanced (weights), damage, resist, accuracy and the other goal modes all use
  the same normalized reference.

## Search / Best in Slot

- Exclusion now removes a piece from the equipped build, clears its lock and
  socket assignments, and reruns Best in Slot when a result exists.
- The current build is used as a starting point, reducing local-optimum
  regressions when constraints change.
- Excluded items cannot be kept by lock/keep-picks.
- Minimum item level filter for forcing level-appropriate gear.

## Data integrity

- 112 phantom level-170 base-name duplicates removed (the `HasQuery` pages such
  as `Dynamic Crimefighter's Coat` that duplicated their `(Level 170+)` page).
- Duplicate-stat ⚠ badge in the list, with the matching names in the tooltip.
- `gear_anomalies.xlsx`: phantom pairs, 6,087 identical-stat groups, raid list.

## Raid

- Raid source added from `Category:Raid Items`: **866** items, all matched and
  tagged; the old world-field method only caught 30.
- Raid is an **exclusive** filter: unchecked Raid removes raid-tagged gear even
  when Crafted/Dropped also match.

## Sources / filters

- Source abbreviations now have full-name tooltips.
- Sources are documented as OR, with Raid as the exception.
- Source tags and the Raid filter apply consistently to list, above-level rows,
  Best in Slot and deep-dive replacements.

## Setup sharing

- Copy setup / Paste setup with school, level, goal, optimizer, order, all 16
  enabled flags, weights, caps, minimums, filters, source mask/names and
  gem/pin toggles.
- `copiedAt` and `buildStamp` detect stale copies.
- Goal select is synced before Best in Slot and Copy setup, fixing the
  Balanced-vs-Max-damage divergence.

## UI

- Stacked Damage/Resistance rows with percent signs and flat rows.
- Collapsible gem/pin socket rows (details omitted here because gem/pin-related).
- Per-slot copy/paste setup buttons.

## Badge requirements — not implemented

Badge requirements are **not present in the extracted data**:

- no `Badge`, `RequiresBadge`, `BadgeRequired` or equivalent item property
- no badge column in `wizard101_priority.xlsx`
- no "Badge Required" text in the raw Data Dump captures
- only `RequiresPvPRank` exists, on 37 items

A toggle would have no data to act on. To add it, capture recipe pages with a
badge field (or a `Category:Recipes` query with a badge printout) and the filter
can be wired the same way as the Raid source.
