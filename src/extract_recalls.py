"""Pull raw FDA food enforcement (recall) records from the openFDA API.

Saves each page of the API response verbatim to data/raw/food_enforcement/,
untouched, so cleaning decisions later have an unmodified source to compare against.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

API_URL = "https://api.fda.gov/food/enforcement.json"
PAGE_SIZE = 1000
SKIP_CAP = 25000  # openFDA hard limit: "Skip value must 25000 or less."
RAW_DIR = Path("data/raw/food_enforcement")

# openFDA has no records before 2004; partitioning by year keeps each query's
# result count well under the 25000 skip cap (max observed ~3066 in one year).
FIRST_YEAR = 2004
LAST_YEAR = 2026


def fetch_page(client: httpx.Client, skip: int, search: str | None = None) -> dict:
    params = {"limit": PAGE_SIZE, "skip": skip}
    if search:
        params["search"] = search
    response = client.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()


def pull_year(client: httpx.Client, year: int) -> list[str]:
    search = f"recall_initiation_date:[{year}0101 TO {year}1231]"
    skip = 0
    pages_fetched = []

    while True:
        try:
            page = fetch_page(client, skip=skip, search=search)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                break  # no records for this year
            raise
        results = page["results"] if "results" in page else []
        if not results:
            break

        path = RAW_DIR / f"{year}_page_{skip:06d}.json"
        path.write_text(json.dumps(page, indent=2))
        pages_fetched.append(str(path))
        print(f"  {year} skip={skip}: {len(results)} records -> {path}")

        skip += PAGE_SIZE
        if len(results) < PAGE_SIZE or skip > SKIP_CAP:
            break
        time.sleep(0.3)

    return pages_fetched


def pull_all() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=30.0) as client:
        total = fetch_page(client, skip=0)["meta"]["results"]["total"]
        print(f"Total records reported by API: {total}")

        pages_fetched = []
        for year in range(FIRST_YEAR, LAST_YEAR + 1):
            pages_fetched += pull_year(client, year)
            time.sleep(0.3)

        manifest = {
            "source_url": API_URL,
            "pulled_at": datetime.now(timezone.utc).isoformat(),
            "total_reported_by_api": total,
            "years_covered": [FIRST_YEAR, LAST_YEAR],
            "pages": pages_fetched,
        }
        (RAW_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
        print(f"Done. {len(pages_fetched)} pages written to {RAW_DIR}/")


if __name__ == "__main__":
    pull_all()
