"""Build an events dimension table by rolling up data/clean/recalls.csv on event_id.

A single real-world recall event (event_id) can spawn many recall_number rows - e.g.
one contamination incident recalled across multiple firms, lots, or product lines.
This produces one row per event for event-level Tableau views (e.g. "how many distinct
recall events per year" rather than "how many recall_number rows").
"""

import json
from pathlib import Path

import pandas as pd

CLEAN_DIR = Path("data/clean")

# Most severe first - used to pick a single representative classification per event.
CLASSIFICATION_SEVERITY = {"Class I": 0, "Class II": 1, "Class III": 2, "Not Yet Classified": 3}

# Least-resolved first - an event isn't fully closed until every recall under it is Terminated.
STATUS_PRIORITY = {"Ongoing": 0, "Completed": 1, "Terminated": 2}


def most_severe_classification(values: pd.Series) -> str:
    return min(values, key=lambda v: CLASSIFICATION_SEVERITY.get(v, 99))


def rollup_status(values: pd.Series) -> str:
    return min(values, key=lambda v: STATUS_PRIORITY.get(v, 99))


def build() -> None:
    df = pd.read_csv(CLEAN_DIR / "recalls.csv", parse_dates=[
        "recall_initiation_date", "center_classification_date", "report_date", "termination_date",
    ])

    grouped = df.groupby("event_id")

    events = grouped.agg(
        num_recalls=("recall_number", "count"),
        recalling_firm=("recalling_firm", "first"),  # always single-valued per event (verified)
        state=("state", "first"),
        country=("country", "first"),
        voluntary_mandated=("voluntary_mandated", "first"),
        distinct_classifications=("classification", "nunique"),
        distinct_reason_categories=("reason_category", "nunique"),
        first_recall_initiation_date=("recall_initiation_date", "min"),
        last_recall_initiation_date=("recall_initiation_date", "max"),
        earliest_report_date=("report_date", "min"),
    ).reset_index()

    events["classification_primary"] = grouped["classification"].apply(most_severe_classification).values
    events["reason_category_primary"] = grouped["reason_category"].agg(
        lambda s: s.mode().iloc[0]
    ).values
    events["status"] = grouped["status"].apply(rollup_status).values

    all_terminated = grouped["status"].apply(lambda s: (s == "Terminated").all())
    events["event_termination_date"] = grouped["termination_date"].max().where(all_terminated.values).values

    events = events[[
        "event_id",
        "num_recalls",
        "status",
        "classification_primary",
        "distinct_classifications",
        "reason_category_primary",
        "distinct_reason_categories",
        "voluntary_mandated",
        "recalling_firm",
        "state",
        "country",
        "first_recall_initiation_date",
        "last_recall_initiation_date",
        "earliest_report_date",
        "event_termination_date",
    ]]

    out_path = CLEAN_DIR / "events.csv"
    events.to_csv(out_path, index=False)

    terminated_but_no_date = events[(events["status"] == "Terminated") & events["event_termination_date"].isna()]

    report = {
        "input_recall_rows": len(df),
        "output_event_rows": len(events),
        "events_with_multiple_classifications": int((events["distinct_classifications"] > 1).sum()),
        "events_with_multiple_reason_categories": int((events["distinct_reason_categories"] > 1).sum()),
        "events_not_fully_terminated": int((events["status"] != "Terminated").sum()),
        "events_terminated_but_missing_termination_date": {
            "count": len(terminated_but_no_date),
            "event_ids": terminated_but_no_date["event_id"].tolist(),
            "note": "Source FDA data marks these Terminated but never populated termination_date. Left null, not fabricated.",
        },
        "max_recalls_in_a_single_event": int(events["num_recalls"].max()),
        "rollup_rules": {
            "classification_primary": "most severe classification among the event's recalls (Class I > II > III)",
            "reason_category_primary": "most common reason_category among the event's recalls",
            "status": "least-resolved status among the event's recalls (Ongoing > Completed > Terminated)",
            "event_termination_date": "max termination_date, but only if every recall in the event is Terminated; else null",
        },
    }
    (CLEAN_DIR / "events_report.json").write_text(json.dumps(report, indent=2, default=str))

    print(f"Wrote {len(events)} events to {out_path}")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    build()
