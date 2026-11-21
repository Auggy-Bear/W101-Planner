# Wizard101 Gear Planner

A single-file, offline build planner for Wizard101 gear. Pick your school and
level, set a priority order, and it ranks every item and searches whole builds.

**Live:** https://Auggy-Bear.github.io/W101-Planner/

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

## First build in 30 seconds

1. Pick your **School** and **Level** in the header.
2. Leave **Goal** on *Balanced* (or choose the stat you care about).
3. Press **Best in slot**.
4. Read the totals, hover any number for its breakdown, then copy or tweak.

That is enough to get a usable build. Everything else is optional tuning.

## Header

| Control | What it does |
|---|---|
| **School** | Which wizard you are building for. |
| **Level** | Maximum item level. Items above it are shown greyed at the bottom of the list. |
| **Goal** | *Balanced* uses the weighted score. The other options maximise one stat first. |
| **Optimiser** | *Set search* tries whole builds (slower, better). *Greedy* fills slots one at a time (fast). |
| **Picks** | *Replace all* searches every slot. *Keep my picks* leaves your equipped items alone and only fills empty slots. |
| **Sources** | Tick where gear can come from (packs, drops, crafting, vendors...). An item is kept if **any** of its sources is ticked. |
| **Setup** | Opens the tuning panel: priority order, caps, minimums, filters, saved settings. |
| **Best in slot** | Runs the search and fills the build. |
| **Clear build** | Empties every slot. |

## Setup panel

**Priority order** - the stats the score cares about, top = most important. Drag
rows or use the arrows. Untick a stat to ignore it completely. Order matters more
than the numbers: the top stat outweighs everything below it.

**Caps** - stop valuing a stat past a threshold. Power pip is the usual one: above
100% it does nothing, so the optimiser stops chasing it. Blank means no cap.

**Minimums** - hard requirements. The search gives up score to hit these first,
then optimises normally. Leave at 0 to ignore.

**Filters** - hide retired gear, restrict to tradeable/auctionable, exclude
seasonal/event pieces, or limit to one world. These apply to the list, the slots
and the search.

**Saved settings** - school, level, priority, caps, minimums, filters, locks and
the equipped build are kept in this browser. *Clear saved settings* resets them.

## Item list

Tabs switch slot type: Hat, Robe, Boots, Wand, Athame, Amulet, Ring, Deck.

- **Search** filters the current tab by name.
- Columns show tier, score, damage, resist, crit, block, pierce, accuracy, health
  and shadow pip rating.
- **equip** puts the item straight into its slot.
- **x** excludes that item from all future searches.
- Items **above your level** appear greyed at the bottom; they cannot be equipped
  yet but you can still see what is coming.
- The list renders 250 rows at a time and loads more as you scroll (or with the
  **Show more** button). Counts at the bottom always reflect the full pool.

## Totals

The top card is the build's real totals: Health, Mana, Power pips, Energy, Shadow
pip rating, Archmastery, healing, stun resist and deck size, followed by a block
per stat with one chip per school.

- **Hover any chip or hero card** for the base value plus every item feeding it.
- A capped stat that goes over shows red with the excess.
- Damage, resist, crit, block, pierce and accuracy show all eight positions so you
  can see how the build behaves on another wizard. Pip Conversion shows the seven
  playable schools, since Shadow has no conversion stat.

## Equipped

Each slot shows the item, a **lock** checkbox and a clear **x**. Item names link
to their wiki page.

- **Lock** a slot to keep it fixed while Best in slot fills the rest.
- **Copy build** puts a plain-text summary on the clipboard for Discord or a forum.
- **Replacement levels (deep dive)** expands to show, per slot, the level at which
  a better single piece becomes available.

## Good to know

- The score is percentile-based within the current tab, so "90" means "top of the
  items available to you", not a universal rating.
- With a goal selected, the list sorts by that goal first, then by weighted score.
- Sockets/gems, set bonuses and pets are not modelled, so in-game totals can be
  higher than the planner's.
- Best viewed on desktop; the item table needs horizontal scrolling on phones.
- This only covers to Level 180. Level 190 will be updated hopefully by year end.

## Data credits

Item data was compiled from the Wizard101 Central wiki on 2026-11-17. Wizard101
and its item data belong to KingsIsle Entertainment. This is an unofficial fan
tool and is not affiliated with or endorsed by KingsIsle or Wizard101 Central.
