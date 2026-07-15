"""Clean raw FDA food enforcement (recall) records into a tidy fact table for Tableau.

Reads data/raw/food_enforcement/*.json (untouched API responses) and writes
data/clean/recalls.csv. Every transformation here is a documented decision, not a
silent default — see the comments and cleaning_report.json output.
"""

import json
import re
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw/food_enforcement")
CLEAN_DIR = Path("data/clean")

DATE_COLS = [
    "recall_initiation_date",
    "center_classification_date",
    "termination_date",
    "report_date",
]

US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN",
    "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV",
    "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN",
    "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC", "PR", "GU", "VI",
}

# Ordered (specific -> general) keyword rules for reason_for_recall. First match wins.
# Heuristic, not a perfect classification - e.g. "does not declare X" is folded into
# Undeclared Allergen even though X is occasionally a non-allergen (species substitution).
REASON_CATEGORY_RULES = [
    ("Undeclared Allergen", r"undeclared|allerg|does not declare|fail(s)?\s+to\s+declare"),
    ("Listeria", r"listeria"),
    ("Salmonella", r"salmonella"),
    ("E. coli", r"e\.?\s?coli"),
    ("Foreign Material", r"foreign material|foreign object|metal|plastic|glass fragment"),
    ("Heavy Metal Contamination", r"\blead\b|arsenic|mercury|cadmium"),
    ("Pesticide/Chemical", r"pesticide|chemical residue|contamina.*chemical"),
    ("Temperature Abuse/Spoilage", r"temperature abus|not stored refrigerat|spoilage|swollen|\bbloat|leak"),
    ("Labeling/Misbranding", r"mislabel|label(l)?ing|misbranded|incorrect label"),
    ("Insanitary/Processing", r"insanitary|underprocess|unapproved process|under-process|\bgmp\b|good manufacturing practice"),
    ("Other Pathogen/Contamination", r"contamina|bacteria|pathogen|norovirus|mold"),
]


def load_raw() -> pd.DataFrame:
    records = []
    for f in sorted(RAW_DIR.glob("*_page_*.json")):
        records.extend(json.loads(f.read_text())["results"])
    return pd.DataFrame(records)


def fix_known_date_typo(df: pd.DataFrame) -> pd.DataFrame:
    # F-0880-2013: recall_initiation_date is '02121207'. Its other dates
    # (report_date 2013-01-23, center_classification_date 2013-01-14) confirm this
    # is a digit transposition of '20121207' (2012-12-07), not a genuine 1912 date.
    mask = df["recall_number"] == "F-0880-2013"
    df.loc[mask, "recall_initiation_date"] = "20121207"
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in DATE_COLS:
        df[col] = pd.to_datetime(df[col], format="%Y%m%d", errors="coerce")
    return df


def clean_state(df: pd.DataFrame) -> pd.DataFrame:
    df["state_raw"] = df["state"]
    is_us = df["country"] == "United States"
    is_valid_code = df["state"].isin(US_STATE_CODES)
    df["state"] = df["state"].where(is_us & is_valid_code, other=pd.NA)
    return df


def clean_voluntary_mandated(df: pd.DataFrame) -> pd.DataFrame:
    df["voluntary_mandated"] = df["voluntary_mandated"].replace({"N/A": "Unknown", "": "Unknown"})
    return df


def categorize_reason(reason: str) -> str:
    text = reason.lower()
    for category, pattern in REASON_CATEGORY_RULES:
        if re.search(pattern, text):
            return category
    return "Other"


def clean() -> None:
    df = load_raw()
    start_count = len(df)

    df = fix_known_date_typo(df)
    df = parse_dates(df)
    df = clean_state(df)
    df = clean_voluntary_mandated(df)
    df["reason_category"] = df["reason_for_recall"].apply(categorize_reason)

    # product_type is constant ("Food") across this endpoint - carries no information.
    df = df.drop(columns=["product_type", "openfda"])

    keep_cols = [
        "recall_number",
        "event_id",
        "status",
        "classification",
        "voluntary_mandated",
        "initial_firm_notification",
        "reason_category",
        "reason_for_recall",
        "recalling_firm",
        "city",
        "state",
        "state_raw",
        "country",
        "product_description",
        "product_quantity",
        "distribution_pattern",
        "recall_initiation_date",
        "center_classification_date",
        "report_date",
        "termination_date",
    ]
    df = df[keep_cols]

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CLEAN_DIR / "recalls.csv"
    df.to_csv(out_path, index=False)

    report = {
        "input_rows": start_count,
        "output_rows": len(df),
        "reason_category_counts": df["reason_category"].value_counts().to_dict(),
        "state_nulled_count": int(df["state"].isna().sum()),
        "state_nulled_reason": "blank/N/A/non-US or non-standard code in source state field",
        "null_date_counts_after_parse": {col: int(df[col].isna().sum()) for col in DATE_COLS},
        "known_fixes_applied": ["F-0880-2013 recall_initiation_date '02121207' -> '20121207'"],
        "dropped_columns": ["product_type (constant value 'Food')", "openfda (empty across this endpoint)"],
    }
    (CLEAN_DIR / "cleaning_report.json").write_text(json.dumps(report, indent=2, default=str))

    print(f"Wrote {len(df)} rows to {out_path}")
    print(json.dumps(report["reason_category_counts"], indent=2))


if __name__ == "__main__":
    clean()
