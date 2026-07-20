# Directory Structure

*Last Updated: 2026-07-20*

```
codebase-mapper/
├── .claude/
│   ├── settings.json
│   └── .codebase-info/         # this map
├── planning/
│   └── PLAN.md                 # original Tableau brainstorm + pivot note at the top
├── README.md                   # portfolio write-up: cleaning decisions + dashboard build
├── index.html                  # GitHub Pages root redirect -> dashboard/index.html;
│                                #   carries the Open Graph/Twitter Card preview tags
├── social-preview.png          # 1200x630 OG/Twitter image; committed (see data-pipeline.md)
├── .nojekyll                   # disables Jekyll processing on GitHub Pages
├── scripts/
│   └── generate_social_preview.js  # Node/Playwright, not part of the uv pipeline
├── src/
│   ├── extract_recalls.py      # pulls raw recall data from openFDA
│   ├── clean_recalls.py        # produces data/clean/recalls.csv
│   ├── build_events.py         # produces data/clean/events.csv
│   ├── build_dashboard.py      # produces dashboard/index.html (active viz path)
│   ├── dashboard_template.html # static template build_dashboard.py fills in
│   ├── build_hyper.py          # produces data/clean/fda_recalls.hyper (alternate, inactive)
│   └── profile_raw.py          # ad-hoc exploration script (not part of the pipeline)
├── dashboard/
│   └── index.html              # the shipped deliverable — committed (not gitignored),
│                                #   self-contained, no server needed
├── data/                       # gitignored — reproducible from src/*.py
│   ├── raw/food_enforcement/   # untouched API response pages + manifest.json
│   └── clean/                  # recalls.csv, events.csv, fda_recalls.hyper, *_report.json
├── tableau/                    # alternate/inactive Tableau path
│   ├── BUILD_SPEC.md           # executable spec for the Tableau workbook build
│   └── codebase-mapper.code-workspace
├── pyproject.toml
├── uv.lock
└── .python-version
```

## Planned next

Optionally: a filter/date-range control on the dashboard (see architecture.md's open
questions) — not currently planned as a firm next step, just a noted possibility. The
Tableau workbook under `tableau/` remains a valid but inactive path if picked back up.
