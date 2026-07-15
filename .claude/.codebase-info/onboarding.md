# Onboarding

*Last Updated: 2026-07-15*

## Current state

Extraction and cleaning are done. The dataset is openFDA Food Enforcement (recalls);
`data/clean/recalls.csv` (29,223 rows) is ready to point Tableau at. No Tableau work has
started yet.

## Quick start

```bash
uv sync                          # install deps
uv run src/extract_recalls.py    # pull raw data from openFDA (idempotent, ~2 min)
uv run src/clean_recalls.py      # produce data/clean/recalls.csv
```

`data/` is gitignored — both commands regenerate it from scratch.

## Next steps (per the plan)

1. Decide whether a dimension table (e.g. an `events` rollup on `event_id`) adds enough
   value to be worth building, or whether the single fact table is sufficient for the
   Tableau build.
2. Resolve the open questions in [architecture.md](architecture.md): Tableau Public vs.
   Desktop.
3. Build the Tableau workbook: map + trend-over-time + categorical breakdown + a
   cross-filtering action, per the plan.
4. Write up the cleaning decisions for the portfolio piece (data-pipeline.md already has
   the raw material).

## How to work in this repo

- `uv run` / `uv add`, never bare `python3`/`pip`.
- Work incrementally, validate each step (this pipeline was built that way — profile raw
  data before writing cleaning rules, verify record counts against the API's own totals,
  sample outputs before trusting them).

## Maintaining this map

Run `update-codebase-map` after the Tableau workbook exists, or if the data model grows
beyond a single fact table.
