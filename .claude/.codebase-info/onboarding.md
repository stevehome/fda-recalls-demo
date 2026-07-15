# Onboarding

*Last Updated: 2026-07-15*

## Current state

Extraction, cleaning, and the events dimension table are all done. The dataset is
openFDA Food Enforcement (recalls); `data/clean/recalls.csv` (29,223 rows, one per
recall) and `data/clean/events.csv` (7,790 rows, one per real-world recall event) are
ready to point Tableau at. No Tableau work has started yet.

## Quick start

```bash
uv sync                          # install deps
uv run src/extract_recalls.py    # pull raw data from openFDA (idempotent, ~2 min)
uv run src/clean_recalls.py      # produce data/clean/recalls.csv
uv run src/build_events.py       # produce data/clean/events.csv (run after cleaning)
```

`data/` is gitignored — all three commands regenerate it from scratch.

## Next steps (per the plan)

1. Resolve the open questions in [architecture.md](architecture.md): Tableau Public vs.
   Desktop.
2. Build the Tableau workbook: map + trend-over-time + categorical breakdown + a
   cross-filtering action, per the plan. `recalls.csv` and `events.csv` can be related
   in Tableau on `event_id`.
3. Write up the cleaning decisions for the portfolio piece (data-pipeline.md already has
   the raw material).

## How to work in this repo

- `uv run` / `uv add`, never bare `python3`/`pip`.
- Work incrementally, validate each step (this pipeline was built that way — profile raw
  data before writing cleaning rules, verify record counts against the API's own totals,
  sample outputs before trusting them).

## Maintaining this map

Run `update-codebase-map` after the Tableau workbook exists, or if the data model grows
beyond a single fact table.
