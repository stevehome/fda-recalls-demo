# Directory Structure

*Last Updated: 2026-07-15*

```
codebase-mapper/
├── .claude/
│   ├── settings.json
│   └── .codebase-info/        # this map
├── planning/
│   └── PLAN.md                # original Tableau demo project brainstorm
├── src/
│   ├── extract_recalls.py     # pulls raw recall data from openFDA
│   ├── clean_recalls.py       # produces data/clean/recalls.csv
│   ├── build_events.py        # produces data/clean/events.csv
│   ├── build_hyper.py         # produces data/clean/fda_recalls.hyper
│   └── profile_raw.py         # ad-hoc exploration script (not part of the pipeline)
├── data/                      # gitignored — reproducible from src/*.py
│   ├── raw/food_enforcement/  # untouched API response pages + manifest.json
│   └── clean/                 # recalls.csv, events.csv, fda_recalls.hyper, *_report.json
├── tableau/
│   └── BUILD_SPEC.md          # executable spec for the Tableau workbook build
├── pyproject.toml
├── uv.lock
└── .python-version
```

## Planned next

The actual Tableau workbook (`.twb`/`.twbx`) — building it requires Tableau's GUI, so
it's a manual step for the user following `tableau/BUILD_SPEC.md`. Once built, save it
into `tableau/` alongside the spec.
