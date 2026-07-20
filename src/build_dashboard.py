"""Build a self-contained, code-driven dashboard (no Tableau) from the clean data.

Reads data/clean/recalls.csv + events.csv, pre-aggregates into small JSON payloads
(never ships the raw 29k-row table to the browser), and injects that JSON into
src/dashboard_template.html to produce dashboard/index.html - a single static file
with no external dependencies (no CDN, no build step to view it).
"""

import json
from pathlib import Path

import pandas as pd

CLEAN_DIR = Path("data/clean")
RAW_DIR = Path("data/raw/food_enforcement")
TEMPLATE_PATH = Path("src/dashboard_template.html")
OUT_PATH = Path("dashboard/index.html")

BUCKET_ORDER = ["1 (single recall)", "2–5", "6–20", "21–100", "100+"]


def bucket_for(num_recalls: int) -> str:
    if num_recalls == 1:
        return BUCKET_ORDER[0]
    if num_recalls <= 5:
        return BUCKET_ORDER[1]
    if num_recalls <= 20:
        return BUCKET_ORDER[2]
    if num_recalls <= 100:
        return BUCKET_ORDER[3]
    return BUCKET_ORDER[4]


def aggregate() -> dict:
    recalls = pd.read_csv(CLEAN_DIR / "recalls.csv", parse_dates=["recall_initiation_date"])
    events = pd.read_csv(CLEAN_DIR / "events.csv")

    total_recalls = len(recalls)
    total_events = len(events)
    pct_class_i = round((recalls["classification"] == "Class I").mean() * 100, 1)
    date_min = recalls["recall_initiation_date"].min().strftime("%Y-%m-%d")
    date_max = recalls["recall_initiation_date"].max().strftime("%Y-%m-%d")
    not_yet_classified_count = int((recalls["classification"] == "Not Yet Classified").sum())

    states_top15 = (
        recalls[recalls["state"].notna()]
        .groupby("state").size().sort_values(ascending=False).head(15)
    )

    recalls["year"] = recalls["recall_initiation_date"].dt.year
    severity_only = recalls[recalls["classification"].isin(["Class I", "Class II", "Class III"])]
    yearly = (
        severity_only.groupby(["year", "classification"]).size()
        .unstack(fill_value=0)
        .reindex(columns=["Class I", "Class II", "Class III"], fill_value=0)
        .sort_index()
    )

    reason_counts = recalls.groupby("reason_category").size().sort_values(ascending=False)

    events = events.copy()
    events["bucket"] = events["num_recalls"].apply(bucket_for)
    bucket_counts = events.groupby("bucket").size().reindex(BUCKET_ORDER, fill_value=0)
    max_event_size = int(events["num_recalls"].max())

    return {
        "kpis": {
            "total_recalls": total_recalls,
            "total_events": total_events,
            "pct_class_i": pct_class_i,
            "date_min": date_min,
            "date_max": date_max,
        },
        "states_top15": [{"state": s, "count": int(c)} for s, c in states_top15.items()],
        "yearly_trend": [
            {"year": int(year), "class_i": int(row["Class I"]), "class_ii": int(row["Class II"]), "class_iii": int(row["Class III"])}
            for year, row in yearly.iterrows()
        ],
        "reason_counts": [{"category": cat, "count": int(c)} for cat, c in reason_counts.items()],
        "event_buckets": [{"bucket": b, "count": int(c)} for b, c in bucket_counts.items()],
        "not_yet_classified_count": not_yet_classified_count,
        "max_event_size": max_event_size,
    }


def build() -> None:
    data = aggregate()
    pull_date = json.loads((RAW_DIR / "manifest.json").read_text())["pulled_at"][:10]

    template = TEMPLATE_PATH.read_text()
    html = (
        template
        .replace("__DASHBOARD_DATA__", json.dumps(data, separators=(",", ":")))
        .replace("__TOTAL_RECALLS__", f"{data['kpis']['total_recalls']:,}")
        .replace("__TOTAL_EVENTS__", f"{data['kpis']['total_events']:,}")
        .replace("__DATE_MIN__", data["kpis"]["date_min"])
        .replace("__DATE_MAX__", data["kpis"]["date_max"])
        .replace("__PULL_DATE__", pull_date)
        .replace("__NOT_YET_CLASSIFIED_COUNT__", str(data["not_yet_classified_count"]))
        .replace("__MAX_EVENT_SIZE__", str(data["max_event_size"]))
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html)
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build()
