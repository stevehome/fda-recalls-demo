# Data Pipeline

*Last Updated: 2026-07-20*

## Overview

```
src/extract_recalls.py     → data/raw/food_enforcement/*.json  (untouched API snapshots)
src/clean_recalls.py       → data/clean/recalls.csv            (tidy fact table)
src/build_events.py        → data/clean/events.csv             (event-level dimension table)
src/build_dashboard.py     → dashboard/index.html               (active: code-driven dashboard)
src/dashboard_template.html → static template build_dashboard.py fills in
src/profile_raw.py         → ad-hoc exploration/profiling (not part of the pipeline proper)

--- alternate path, not active (see architecture.md) ---
src/build_hyper.py         → data/clean/fda_recalls.hyper       (Tableau Hyper extract)
```

`data/` is gitignored — raw and clean outputs are fully reproducible by re-running the
scripts against the public openFDA API. `dashboard/index.html` **is** committed — small
(~26 KB) and it's the actual shippable deliverable, not an intermediate artifact.

## Extraction — `src/extract_recalls.py`

Run: `uv run src/extract_recalls.py`

Source: openFDA Food Enforcement (recalls) API — `https://api.fda.gov/food/enforcement.json`,
no API key required.

**Key constraint:** openFDA caps the `skip` pagination parameter at 25000 per query
("Skip value must 25000 or less"). With ~29,200 total records, straight offset
pagination can't reach the whole dataset. The script partitions requests by
`recall_initiation_date` year (2004–2026) so each partition's result count stays well
under the cap (largest single year: ~3,066 records in 2016), then paginates normally
within each year.

Output: one JSON file per page at `data/raw/food_enforcement/{year}_page_{skip}.json`
(verbatim API responses, unmodified), plus `manifest.json` recording the source URL,
pull timestamp, and API-reported total.

Last full pull: 29,223 of 29,224 records reported by the API. The one gap is a record
with a corrupted `recall_initiation_date` (see Known Fixes below) that doesn't fall into
any valid year partition — it's recovered during cleaning, not extraction.

## Cleaning — `src/clean_recalls.py`

Run: `uv run src/clean_recalls.py`

Reads every page under `data/raw/food_enforcement/`, applies the transformations below,
and writes `data/clean/recalls.csv` (one row per `recall_number`) plus
`data/clean/cleaning_report.json` (row counts, category distribution, and every decision
made, generated fresh on each run).

| Transformation | Decision | Why |
|---|---|---|
| Known date typo | `F-0880-2013`'s `recall_initiation_date` `'02121207'` → `'20121207'` | Digit transposition; corroborated by that record's `report_date` (2013-01-23) and `center_classification_date` (2013-01-14) |
| Date parsing | `recall_initiation_date`, `center_classification_date`, `report_date`, `termination_date` parsed from `YYYYMMDD` strings to real dates | `termination_date` is null for 1,500 rows — legitimate (recall still `Ongoing`/`Completed`, not `Terminated`) |
| State cleanup | New `state` column: valid 2-letter US code or null; original preserved in `state_raw` | Source `state` mixes blank, `"N/A"`, and spelled-out Canadian provinces (British Columbia, Ontario, etc.) with US postal codes — unsafe to use directly for any state-level breakdown |
| `voluntary_mandated` | Blank/`"N/A"` → `"Unknown"` | Consistent categorical values |
| `reason_category` (new column) | Derived from free-text `reason_for_recall` via ordered regex rules (see `REASON_CATEGORY_RULES` in the script) | Source has no structured recall-cause field; this is what enables a "recalls by cause" chart. Heuristic, not exact — ~17% of rows fall into `"Other"` |
| Dropped columns | `product_type` (constant `"Food"` across this endpoint), `openfda` (always empty) | No information value |

`reason_category` buckets (largest first, as of last run): Undeclared Allergen,
Listeria, Other, Salmonella, Foreign Material, Other Pathogen/Contamination,
Insanitary/Processing, Temperature Abuse/Spoilage, E. coli, Labeling/Misbranding, Heavy
Metal Contamination, Pesticide/Chemical.

## Clean schema — `data/clean/recalls.csv`

One row per `recall_number` (29,223 rows). Columns: `recall_number`, `event_id`
(multiple recalls can share one `event_id` — same real-world recall event, e.g. multiple
firms/lots), `status`, `classification` (Class I/II/III), `voluntary_mandated`,
`initial_firm_notification`, `reason_category`, `reason_for_recall` (raw text),
`recalling_firm`, `city`, `state`, `state_raw`, `country`, `product_description`,
`product_quantity`, `distribution_pattern`, `recall_initiation_date`,
`center_classification_date`, `report_date`, `termination_date`.

## Events dimension — `src/build_events.py`

Run: `uv run src/build_events.py` (reads `data/clean/recalls.csv`, must run after cleaning)

Rolls `recalls.csv` up from one row per `recall_number` (29,223) to one row per
`event_id` (7,790) — a real-world recall event can spawn many `recall_number` rows
(max observed: 409, for a single large contamination incident). Verified before
building: `recalling_firm`, `state`, `country`, and `voluntary_mandated` are always
single-valued within an event (0% of events have more than one distinct value), so
those roll up with `first`. `classification` and `reason_category` do vary within some
events (2.2% and 0.7% respectively), so those use explicit rollup rules:

| Column | Rollup rule | Why |
|---|---|---|
| `classification_primary` | Most severe classification among the event's recalls (Class I > II > III) | An event should surface its worst-case severity, not an arbitrary one |
| `reason_category_primary` | Most common `reason_category` among the event's recalls | Representative cause for the event as a whole |
| `status` | Least-resolved status among the event's recalls (Ongoing > Completed > Terminated) | An event isn't fully closed until every recall under it is Terminated — confirmed on a 409-recall event that was 404 Terminated + 5 still Completed |
| `event_termination_date` | Max `termination_date`, but only if every recall in the event is `Terminated`; else null | Don't report a close date for an event that isn't fully closed |

**Known source data gap**: 2 events (`event_id` 83562, 84056 — 4 recall rows total) are
marked `Terminated` by the FDA but never got a `termination_date` populated in the
source. Left null rather than fabricated; recorded explicitly in
`data/clean/events_report.json` under `events_terminated_but_missing_termination_date`
so it doesn't silently blend into the "not fully terminated" count.

**Bug caught during development**: an early version assigned
`grouped["termination_date"].max().where(...)` directly onto the output frame without
`.values`. The output frame has a default `0..N` index while that Series is indexed by
`event_id`, so pandas aligned by label instead of position and silently produced
all-null output. Fixed by appending `.values` to force positional assignment, matching
the pattern already used for the other rollup columns.

## Clean schema — `data/clean/events.csv`

One row per `event_id` (7,790 rows): `event_id`, `num_recalls`, `status`,
`classification_primary`, `distinct_classifications`, `reason_category_primary`,
`distinct_reason_categories`, `voluntary_mandated`, `recalling_firm`, `state`,
`country`, `first_recall_initiation_date`, `last_recall_initiation_date`,
`earliest_report_date`, `event_termination_date`.

## Dashboard — `src/build_dashboard.py` + `src/dashboard_template.html`

Run: `uv run src/build_dashboard.py` (reads `recalls.csv` and `events.csv`, must run
after both)

The active visualization path (see [architecture.md](architecture.md) for why Tableau
was dropped). Two-file design:

- `src/dashboard_template.html` — a static HTML/CSS/JS file with placeholder tokens
  (`__DASHBOARD_DATA__`, `__TOTAL_RECALLS__`, etc.). All charting is hand-written
  vanilla JS/SVG — no charting library, no CDN, nothing that needs a build step.
- `src/build_dashboard.py` — pre-aggregates `recalls.csv`/`events.csv` into small JSON
  payloads (state top-15, yearly trend by classification, reason category counts, event
  size buckets, KPIs) and string-replaces them into the template, writing
  `dashboard/index.html`. The raw 29k-row table is never shipped to the browser — only
  these aggregates are.

Charts: state ranking (top 15), a severity trend over time, a cause breakdown, and an
event-size distribution, plus a KPI row. Colors follow the `dataviz` skill's method: the
severity trend uses an **ordinal** one-hue ramp (Class I darkest → Class III lightest,
since severity is an ordered scale, not arbitrary categories) validated with
`validate_palette.js --ordinal`; the single-series ranking bars use one flat validated
hue. Every chart has hover tooltips, a keyboard-focus equivalent, and a "View as table"
toggle (the accessibility twin required by the skill).

**Bug caught during development**: the CSS defined light-mode variable defaults on both
`:root` and a `.viz-root` wrapper class (`:root, .viz-root { --surface-1: ...; }`), but
the dark-mode media-query override only targeted `:root`. Since `.viz-root` re-declared
the same custom properties, its descendants inherited the hardcoded light value instead
of cascading through `:root`'s dark override — cards stayed light-themed inside a
dark page, and white KPI text became invisible on a white card. Caught by actually
rendering the page in a headless browser (Playwright) in both color schemes and
screenshotting it, not by reasoning about the CSS. Fixed by declaring the variables on
`:root` only.

Also fixed before shipping: vertical bars exceeded the skill's ≤24px thickness cap (were
up to 48px), bar corners were rounded on all four sides instead of just the tip (square
at the baseline is the spec), axis ticks used raw fractional values instead of
human-friendly rounded numbers, and the severity trend's three direct end-labels
collided at the right edge where the lines converge — dropped in favor of the legend +
tooltip, per the skill's guidance on converging series.

Verified: headless-browser run in light and dark mode with zero console/page errors,
table-view toggle interaction tested, and all embedded aggregate numbers cross-checked
against `cleaning_report.json`/`events_report.json` (29,223 recalls, 7,790 events, event
buckets summing to 7,790, etc.).

## Alternate path (not active): Hyper extract — `src/build_hyper.py`

Run: `uv run src/build_hyper.py` (reads `recalls.csv` and `events.csv`, must run after
both)

Uses `pantab` (wraps Tableau's official Hyper API) to package both tables into a single
`data/clean/fda_recalls.hyper` (9.2 MB, smaller than the 17 MB `recalls.csv` alone) —
the native, optimized data source format for Tableau. Contains two tables, `recalls` and
`events`; open the file directly in Tableau Desktop and create a relationship on
`event_id` (not baked into the extract itself). Verified by reading the extract back
with `pantab` and confirming row counts, column set, and date typing all match the
source CSVs. Tableau Public can't open this file directly (see
[tableau/BUILD_SPEC.md](../../tableau/BUILD_SPEC.md) for the CSV-based workaround it
documents) — this, plus Tableau's story feature being mid-rewrite, is why the project
moved to the code-driven dashboard above instead.

See [architecture.md](architecture.md) for the overall pipeline stages and
[planning/PLAN.md](../../planning/PLAN.md) for the original brainstorm.

## Re-running

All scripts are idempotent — safe to re-run. Extraction overwrites raw pages in place;
cleaning regenerates `recalls.csv`/`cleaning_report.json` from whatever is currently in
`data/raw/`; `build_events.py` regenerates `events.csv`/`events_report.json` from
whatever is currently in `data/clean/recalls.csv`; `build_dashboard.py` regenerates
`dashboard/index.html` from whatever is currently in both clean CSVs; `build_hyper.py`
(alternate path) regenerates `fda_recalls.hyper` the same way.
