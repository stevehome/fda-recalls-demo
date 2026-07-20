# Tech Landscape

*Last Updated: 2026-07-20*

## Stack

- **Language**: Python 3.12, managed with `uv` (`pyproject.toml` + `uv.lock`) — per this
  user's convention, always `uv run`/`uv add`, never bare `python3`/`pip`
- **Data extraction/cleaning deps**: `httpx` (HTTP client), `pandas` (data wrangling;
  pulls in `numpy`, `python-dateutil` transitively)
- **Visualization (active)**: hand-written HTML/CSS/SVG/vanilla JS, no charting
  library, no CDN, no build step — `dashboard/index.html` is a single self-contained
  file. Built following the `dataviz` skill's color-and-marks method (colorblind-safety
  and contrast are validated with a script, not eyeballed).
- **Visualization (alternate, not active)**: Tableau — `pantab` (wraps Tableau's
  official Hyper API) + `pyarrow` for the extract. See
  [architecture.md](architecture.md) for why this path was dropped.
- **Dev-time only, not a runtime dependency**: Playwright + a scratch Node project (not
  checked into this repo) were used to headless-browser-test `dashboard/index.html` in
  light/dark mode before shipping, and to generate `social-preview.png` (via the
  committed `scripts/generate_social_preview.js`) — the dashboard itself has zero JS
  dependencies to view it.
- **Source data**: openFDA Food Enforcement API (`https://api.fda.gov/food/enforcement.json`),
  no API key required

## Source-of-truth files

- `pyproject.toml` / `uv.lock` — dependencies
- `src/extract_recalls.py`, `src/clean_recalls.py`, `src/build_events.py`,
  `src/build_dashboard.py`, `src/dashboard_template.html` — the active pipeline; see
  [data-pipeline.md](data-pipeline.md)
- `src/build_hyper.py` — alternate/inactive Tableau path
- `scripts/generate_social_preview.js` — Node, not part of the `uv` pipeline; requires
  `npm install playwright` in a scratch directory to run

## Not yet present

- No test suite (small enough pipeline that manual validation + the generated
  `*_report.json` files, plus a one-off headless-browser check for the dashboard, has
  sufficed so far)
- No filter/date-range control on the dashboard (deliberate v1 scope cut — see
  architecture.md's open questions)
