# Onboarding

*Last Updated: 2026-07-20*

## Current state

The project is done end to end: extraction, cleaning, the events dimension table, and a
finished interactive dashboard. Open [`dashboard/index.html`](../../dashboard/index.html)
directly in a browser — no server, no build step. See [README.md](../../README.md) for
the portfolio write-up (the cleaning decisions and the dashboard build, told as a
narrative) and [data-pipeline.md](data-pipeline.md) for the full technical detail.

The project started as a Tableau demo and pivoted to a code-driven dashboard on
2026-07-20 (Tableau Public can't open `.hyper` files; Tableau's story feature was
mid-rewrite). The Tableau path still exists and still works
([tableau/BUILD_SPEC.md](../../tableau/BUILD_SPEC.md)), just isn't the active one — see
[architecture.md](architecture.md).

## Quick start

```bash
uv sync                          # install deps
uv run src/extract_recalls.py    # pull raw data from openFDA (idempotent, ~2 min)
uv run src/clean_recalls.py      # produce data/clean/recalls.csv
uv run src/build_events.py       # produce data/clean/events.csv (run after cleaning)
uv run src/build_dashboard.py    # produce dashboard/index.html (run after both)
```

`data/` is gitignored — all commands regenerate it from scratch. `dashboard/index.html`
**is** committed (small, and it's the shipped deliverable).

## Possible next steps

Nothing required — the project is complete as a portfolio piece. If picked back up:

1. A filter/date-range control on the dashboard (deliberately cut from v1 — see
   architecture.md's open questions).
2. Actually building the Tableau workbook from `tableau/BUILD_SPEC.md`, if the Tableau
   angle is wanted after all.

## How to work in this repo

- `uv run` / `uv add`, never bare `python3`/`pip`.
- Work incrementally, validate each step. This pipeline was built that way throughout —
  profile raw data before writing cleaning rules, verify record counts against known
  totals, sample outputs before trusting them, and (for the dashboard) actually render
  the page in a headless browser in both light and dark mode rather than trusting that a
  passing color-validator check means the page renders correctly.

## Maintaining this map

Run `update-codebase-map` if the dashboard's chart set changes, a filter control is
added, or the Tableau path is revived.
