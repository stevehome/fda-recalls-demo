# Onboarding

*Last Updated: 2026-07-15*

## Current state

The full data pipeline is done: extraction, cleaning, the events dimension table, and a
packaged Tableau Hyper extract. `data/clean/fda_recalls.hyper` (two tables: `recalls`
29,223 rows, `events` 7,790 rows) is ready to open directly in Tableau Desktop/Public.
No Tableau workbook exists yet — this environment can't drive Tableau's GUI, so the
dashboard build itself is a manual next step for the user.

## Quick start

```bash
uv sync                          # install deps
uv run src/extract_recalls.py    # pull raw data from openFDA (idempotent, ~2 min)
uv run src/clean_recalls.py      # produce data/clean/recalls.csv
uv run src/build_events.py       # produce data/clean/events.csv (run after cleaning)
uv run src/build_hyper.py        # produce data/clean/fda_recalls.hyper (run after both)
```

`data/` is gitignored — all four commands regenerate it from scratch.

## Next steps (per the plan)

1. Resolve the open questions in [architecture.md](architecture.md): Tableau Public vs.
   Desktop.
2. Open `data/clean/fda_recalls.hyper` in Tableau, relate `recalls` and `events` on
   `event_id`, and build the workbook: map + trend-over-time + categorical breakdown +
   a cross-filtering action, per the plan.
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
