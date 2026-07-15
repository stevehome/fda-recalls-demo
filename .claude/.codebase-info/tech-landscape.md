# Tech Landscape

*Last Updated: 2026-07-15*

## Stack

- **Language**: Python 3.12, managed with `uv` (`pyproject.toml` + `uv.lock`) — per this
  user's convention, always `uv run`/`uv add`, never bare `python3`/`pip`
- **Data extraction/cleaning deps**: `httpx` (HTTP client), `pandas` (data wrangling;
  pulls in `numpy`, `python-dateutil` transitively)
- **Tableau extract deps**: `pantab` (wraps Tableau's official Hyper API), `pyarrow`
- **Visualization**: Tableau — Public vs. Desktop still undecided (see
  [architecture.md](architecture.md)). No GUI automation available in this environment,
  so the workbook itself must be built by hand in Tableau Desktop/Public
- **Source data**: openFDA Food Enforcement API (`https://api.fda.gov/food/enforcement.json`),
  no API key required

## Source-of-truth files

- `pyproject.toml` / `uv.lock` — dependencies
- `src/extract_recalls.py`, `src/clean_recalls.py`, `src/build_events.py`,
  `src/build_hyper.py` — the pipeline itself; see [data-pipeline.md](data-pipeline.md)

## Not yet present

- No Tableau workbook (`.twb`/`.twbx`) yet — `data/clean/fda_recalls.hyper` is ready to
  open in Tableau Desktop/Public
- No test suite (small enough pipeline that manual validation + the generated
  `*_report.json` files has sufficed so far)
