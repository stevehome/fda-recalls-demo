# Architecture

*Last Updated: 2026-07-15*

## Goal

A portfolio project demonstrating Tableau skills end-to-end, using a public dataset
messy enough to require genuine cleaning/preparation work — the cleaning pipeline itself
is meant to be part of the demo, not just the finished dashboard.

## Dataset

**Chosen**: openFDA Food Enforcement (recalls), `https://api.fda.gov/food/enforcement.json`.
CFPB complaints and the other candidates in `planning/PLAN.md` were not pursued.

## Pipeline status

```
Extract (Python via uv)              ✅ done — src/extract_recalls.py
   → raw snapshot saved before modification
Clean/prep (scripted, reproducible)  ✅ done — src/clean_recalls.py
   → dedupe, standardize categories, normalize dates, explicit null handling
Model                                🚧 single denormalized fact table so far;
                                         no separate dimension tables yet
Build in Tableau                     ⬜ not started
Document                             🚧 ongoing — see data-pipeline.md
```

See [data-pipeline.md](data-pipeline.md) for the full extraction/cleaning detail,
schema, and every cleaning decision made.

## Open questions

- Tableau Public (free, must be public) vs. Desktop/private — affects publishing
  decisions for data naming real companies/entities.
- Whether the cleaning pipeline lives in this repo (leaning yes, since the pipeline is
  part of the portfolio value) vs. a throwaway script elsewhere.

See [planning/PLAN.md](../../planning/PLAN.md) for full reasoning and all candidate
datasets considered.
