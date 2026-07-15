"""Package the clean recalls + events tables into a single Tableau Hyper extract.

Produces data/clean/fda_recalls.hyper containing two tables ("recalls", "events").
Open it directly in Tableau Desktop/Public and relate the two tables on event_id.
"""

from pathlib import Path

import pandas as pd
import pantab

CLEAN_DIR = Path("data/clean")

RECALL_DATE_COLS = [
    "recall_initiation_date", "center_classification_date", "report_date", "termination_date",
]
EVENT_DATE_COLS = [
    "first_recall_initiation_date", "last_recall_initiation_date",
    "earliest_report_date", "event_termination_date",
]


def build() -> None:
    recalls = pd.read_csv(CLEAN_DIR / "recalls.csv", parse_dates=RECALL_DATE_COLS)
    events = pd.read_csv(CLEAN_DIR / "events.csv", parse_dates=EVENT_DATE_COLS)

    out_path = CLEAN_DIR / "fda_recalls.hyper"
    pantab.frames_to_hyper(
        {"recalls": recalls, "events": events},
        out_path,
    )
    print(f"Wrote {out_path} ({out_path.stat().st_size / 1e6:.1f} MB): "
          f"recalls={len(recalls)} rows, events={len(events)} rows")


if __name__ == "__main__":
    build()
