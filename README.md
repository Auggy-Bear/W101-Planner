# Wizard101 Gear Planner

A single-file, offline build planner for Wizard101 gear. Pick your school and
level, set a priority order, and it ranks every item and searches whole builds.

**Live:** https://YOUR-USERNAME.github.io/YOUR-REPO/

## What it does

- 51,697 items, all eight gear slots, levels 1-180
- Per-school percentile ranking and a set optimiser (Best in slot)
- Goals: balanced score, max damage, resist, health, healing, power/shadow pips
- Caps, minimums, per-slot locks, source filters, seasonal exclusion
- Base stats and class-only base pip conversion from the level table
- Hover any stat chip for a base + per-item breakdown
- Copy build as plain text; runs entirely in your browser, no account, no tracking

## Running locally

Download `index.html` and open it. Everything is embedded - no server, no build
step, no network calls.

## Data credits

Item data was compiled from the Wizard101 Central wiki on 2026-11-17. Wizard101
and its item data belong to KingsIsle Entertainment. This is an unofficial fan
tool and is not affiliated with or endorsed by KingsIsle or Wizard101 Central.

## Known gaps

- Sockets/gems and set bonuses are not modelled (no source data yet)
- Pets are not modelled, so in-game totals can be higher than the planner's
- Best viewed on desktop; the item table needs horizontal scrolling on phones

## Deploying

GitHub Pages: Settings -> Pages -> Deploy from a branch -> `main` / `(root)`.
The site is served from `index.html` at the repository root.
