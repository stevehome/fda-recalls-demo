# Architecture

*Last Updated: 2026-07-20*

## Goal

A portfolio project demonstrating data-cleaning judgment end-to-end, using a public
dataset messy enough to require genuine cleaning/preparation work — the cleaning
pipeline itself is meant to be part of the demo, not just the finished dashboard.

**Visualization tool pivoted mid-project**: started as a Tableau demo (see
`planning/PLAN.md`), moved off Tableau entirely on 2026-07-20 — Tableau Public can't
open a `.hyper` file directly, and Tableau's story-writing feature was mid-rewrite and
unreliable to build against. The dashboard step is now a self-contained, code-driven
HTML page instead, with no GUI dependency. The Tableau path (`tableau/BUILD_SPEC.md`,
`src/build_hyper.py`) is left in place as a still-valid alternate, just not the active one.

## Dataset

**Chosen**: openFDA Food Enforcement (recalls), `https://api.fda.gov/food/enforcement.json`.
CFPB complaints and the other candidates in `planning/PLAN.md` were not pursued.

## Pipeline status

```
Extract (Python via uv)              ✅ done — src/extract_recalls.py
   → raw snapshot saved before modification
Clean/prep (scripted, reproducible)  ✅ done — src/clean_recalls.py
   → dedupe, standardize categories, normalize dates, explicit null handling
Model                                ✅ fact table (recalls.csv) + events dimension
                                         (events.csv) — src/build_events.py
Dashboard (code-driven)              ✅ done — src/build_dashboard.py →
                                         dashboard/index.html. Self-contained HTML/
                                         CSS/SVG/vanilla JS, no external dependencies,
                                         no server needed. Verified in a headless
                                         browser (light + dark mode, no console errors).
Document                             🚧 ongoing — see data-pipeline.md

--- alternate path, not active ---
Hyper extract                        ✅ done — src/build_hyper.py → fda_recalls.hyper
Tableau build spec                   ✅ written — tableau/BUILD_SPEC.md
Build in Tableau                     ⬜ not started — abandoned in favor of the
                                         code-driven dashboard above
```

See [data-pipeline.md](data-pipeline.md) for the full extraction/cleaning/dashboard
detail, schema, and every decision made. See
[tableau/BUILD_SPEC.md](../../tableau/BUILD_SPEC.md) for the sheet-by-sheet Tableau
build plan, if that path is picked back up.

## Open questions

- Whether to add a filter row (date range / dimension) to the dashboard — v1 shipped
  without one; it's a static analytical view, not a live monitoring dashboard, so this
  was a deliberate scope cut rather than an oversight.
- Whether the cleaning pipeline lives in this repo (leaning yes, since the pipeline is
  part of the portfolio value) vs. a throwaway script elsewhere.

See [planning/PLAN.md](../../planning/PLAN.md) for full reasoning and all candidate
datasets considered.
