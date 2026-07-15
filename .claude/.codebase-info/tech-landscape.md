# Tech Landscape

*Last Updated: 2026-07-15*

## Stack

- **Language**: Python 3.12, managed with `uv` (`pyproject.toml` + `uv.lock`) — per this
  user's convention, always `uv run`/`uv add`, never bare `python3`/`pip`
- **Data extraction/cleaning deps**: `httpx` (HTTP client), `pandas` (data wrangling;
  pulls in `numpy`, `python-dateutil` transitively)
- **Visualization**: Tableau — not yet started, Public vs. Desktop still undecided (see
  [architecture.md](architecture.md))
- **Source data**: openFDA Food Enforcement API (`https://api.fda.gov/food/enforcement.json`),
  no API key required

## Source-of-truth files

- `pyproject.toml` / `uv.lock` — dependencies
- `src/extract_recalls.py`, `src/clean_recalls.py` — the pipeline itself; see
  [data-pipeline.md](data-pipeline.md)

## Not yet present

- No Tableau workbook (`.twb`/`.twbx`) yet
- No dimension/lookup tables beyond the single `recalls.csv` fact table
- No test suite (small enough pipeline that manual validation + the generated
  `cleaning_report.json` has sufficed so far)
