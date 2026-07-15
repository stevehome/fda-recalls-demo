# Data Pipeline

*Last Updated: 2026-07-15*

## Overview

```
src/extract_recalls.py  → data/raw/food_enforcement/*.json  (untouched API snapshots)
src/clean_recalls.py    → data/clean/recalls.csv             (tidy fact table for Tableau)
src/build_events.py     → data/clean/events.csv              (event-level dimension table)
src/profile_raw.py      → ad-hoc exploration/profiling (not part of the pipeline proper)
```

`data/` is gitignored — both raw and clean outputs are fully reproducible by re-running
the scripts against the public openFDA API.

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
| State cleanup | New `state` column: valid 2-letter US code or null; original preserved in `state_raw` | Source `state` mixes blank, `"N/A"`, and spelled-out Canadian provinces (British Columbia, Ontario, etc.) with US postal codes — unsafe to feed directly into Tableau's US state geo role |
| `voluntary_mandated` | Blank/`"N/A"` → `"Unknown"` | Consistent categorical values |
| `reason_category` (new column) | Derived from free-text `reason_for_recall` via ordered regex rules (see `REASON_CATEGORY_RULES` in the script) | Source has no structured recall-cause field; this is what enables a "recalls by cause" view in Tableau. Heuristic, not exact — ~17% of rows fall into `"Other"` |
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

See [architecture.md](architecture.md) for the overall pipeline stages and
[planning/PLAN.md](../../planning/PLAN.md) for the original brainstorm.

## Re-running

All three scripts are idempotent — safe to re-run. Extraction overwrites raw pages in
place; cleaning regenerates `recalls.csv`/`cleaning_report.json` from whatever is
currently in `data/raw/`; `build_events.py` regenerates `events.csv`/`events_report.json`
from whatever is currently in `data/clean/recalls.csv`.
