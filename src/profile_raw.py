"""One-off exploration of the raw FDA recall pages to inform cleaning decisions."""

import json
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw/food_enforcement")


def load_raw() -> pd.DataFrame:
    records = []
    for f in sorted(RAW_DIR.glob("*_page_*.json")):
        records.extend(json.loads(f.read_text())["results"])
    return pd.DataFrame(records)


if __name__ == "__main__":
    df = load_raw()
    print("shape:", df.shape)
    print("\ncolumns:\n", df.columns.tolist())
    print("\nnull counts:\n", df.isna().sum().sort_values(ascending=False))
    print("\nduplicate recall_number count:", df["recall_number"].duplicated().sum())
    print("\nduplicate event_id count:", df["event_id"].duplicated().sum())
    print("\nclassification values:\n", df["classification"].value_counts(dropna=False))
    print("\nstatus values:\n", df["status"].value_counts(dropna=False))
    print("\nproduct_type values:\n", df["product_type"].value_counts(dropna=False))
    print("\nvoluntary_mandated values:\n", df["voluntary_mandated"].value_counts(dropna=False))
    print("\ncountry values:\n", df["country"].value_counts(dropna=False))
    print("\nstate values (top 20):\n", df["state"].value_counts(dropna=False).head(20))
    print("\nstate values (odd/short):\n", df[df["state"].str.len() != 2]["state"].value_counts(dropna=False))

    bad_date = df[df["recall_initiation_date"].str.len() != 8]
    print("\nrows with malformed recall_initiation_date:", len(bad_date))
    if len(bad_date):
        print(bad_date[["recall_number", "recall_initiation_date", "recalling_firm", "product_description"]])

    print("\nempty string counts per date field:")
    for col in ["recall_initiation_date", "center_classification_date", "termination_date", "report_date"]:
        print(f"  {col}: empty={sum(df[col] == '')}, null={df[col].isna().sum()}")
