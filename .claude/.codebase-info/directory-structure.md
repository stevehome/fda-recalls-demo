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
│   └── profile_raw.py         # ad-hoc exploration script (not part of the pipeline)
├── data/                      # gitignored — reproducible from src/*.py
│   ├── raw/food_enforcement/  # untouched API response pages + manifest.json
│   └── clean/                 # recalls.csv + cleaning_report.json
├── pyproject.toml
├── uv.lock
└── .python-version
```

Git repo initialized (via `uv init`) but no commits made yet as of last mapping.

## Planned next

A `tableau/` directory for the workbook once the Tableau build starts. No dimension
tables planned yet — see [data-pipeline.md](data-pipeline.md).
