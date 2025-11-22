"""
Assignment 4 - ECON7890

This script loads the Kowloon property transaction data (`hw.csv`), cleans the
fields, enriches it with macro indicators, runs exploratory data analysis (EDA),
and trains a couple of learning models to understand price drivers.

Artifacts (cleaned data, charts, model metrics) are written to
`Excercises/assignment4_outputs`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


DATA_PATH = Path(__file__).resolve().parent / "hw.csv"
OUTPUT_DIR = Path(__file__).resolve().parent / "assignment4_outputs"


# ---------- Cleaning helpers ----------

def _parse_number(text: Any) -> float:
    """
    Extract the first numeric value found in a text field.

    Examples of valid inputs: "657ft<sup>2</sup>", "5 years 12 days", "2#".
    Returns NaN when parsing fails.
    """
    if pd.isna(text):
        return np.nan
    match = re.search(r"([0-9]*\.?[0-9]+)", str(text))
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return np.nan
    return np.nan


def _parse_percent(text: Any) -> float:
    """Convert percentage strings like '413%' to decimal (4.13)."""
    if pd.isna(text):
        return np.nan
    text = str(text).replace("%", "").strip()
    if not text or text == "--":
        return np.nan
    try:
        return float(text) / 100.0
    except ValueError:
        return np.nan


def _parse_holding_years(text: Any) -> float:
    """Convert holding period text such as '16 years 251 days' into years."""
    if pd.isna(text):
        return np.nan
    if text in ("--", "-1"):
        return np.nan
    text = str(text)
    years = _parse_number(text)
    days_match = re.search(r"([0-9]+)\\s*day", text)
    days = float(days_match.group(1)) if days_match else 0.0
    if np.isnan(years):
        # Sometimes only days are present
        return days / 365.0 if days else np.nan
    return years + days / 365.0


def load_raw_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Read the CSV file into a dataframe."""
    df = pd.read_csv(path)
    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and engineer features from the raw transaction data."""
    df = df.copy()

    # Drop unnamed artifacts and standardize column names.
    df = df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")], errors="ignore")
    rename_map: Dict[str, str] = {
        "withpre": "pre_sale_flag",
        "catname": "estate",
        "catfathername": "district",
        "price": "price_label",
        "price_value": "price_hkd",
        "holddate": "holding_period_text",
        "winloss": "winloss_pct",
        "act_area": "saleable_area",
        "area": "gross_area",
        "arearaw": "gross_area_raw",
        "sq_price": "sq_price_label",
        "sq_price_value": "price_per_gross_sf",
        "sq_actprice": "sq_actprice_label",
        "sq_actprice_value": "price_per_saleable_sf",
        "date_y": "year_text",
        "state": "building",
        "addr": "address",
    }
    df = df.rename(columns=rename_map)

    # Parse dates and basic numeric fields.
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["pre_sale_flag"] = df["pre_sale_flag"].fillna(0).astype(int)
    df["price_hkd"] = pd.to_numeric(df["price_hkd"], errors="coerce")
    df["price_per_gross_sf"] = pd.to_numeric(df["price_per_gross_sf"], errors="coerce")
    df["price_per_saleable_sf"] = pd.to_numeric(df["price_per_saleable_sf"], errors="coerce")

    # Area fields come with HTML remnants like "657ft<sup>2</sup>".
    df["saleable_area"] = df["saleable_area"].apply(_parse_number)
    df["gross_area"] = df["gross_area"].apply(_parse_number)
    gross_series = df["gross_area_raw"] if "gross_area_raw" in df.columns else pd.Series(np.nan, index=df.index)
    df["gross_area_raw"] = pd.to_numeric(gross_series, errors="coerce")

    # Floor parsing: keep the numeric component only.
    df["floor_num"] = df["floor"].apply(_parse_number)

    # Holding period and profit/loss information.
    df["holding_period_years"] = df["holding_period_text"].apply(_parse_holding_years)
    df["winloss_pct"] = df["winloss_pct"].apply(_parse_percent)

    # Use calculated price per saleable sqft when missing from the source.
    df["price_per_saleable_sf"] = df["price_per_saleable_sf"].fillna(
        df["price_hkd"] / df["saleable_area"]
    )

    # Remove obviously bad rows.
    df = df.dropna(subset=["date", "price_hkd", "saleable_area", "price_per_saleable_sf", "district", "estate"])
    df = df[(df["saleable_area"] > 0) & (df["price_hkd"] > 0) & (df["price_per_saleable_sf"] > 0)]

    # Keep trimmed text for categorical columns.
    df["estate"] = df["estate"].astype(str).str.strip()
    df["district"] = df["district"].astype(str).str.strip()
    df["building"] = df["building"].astype(str).str.strip()

    # Deduplicate by transaction id if present.
    if "id" in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=["id"])
        after = len(df)
        print(f"Removed {before - after} duplicate transaction rows based on id.")

    return df


# ---------- External data ----------

def fetch_world_bank_indicator(indicator_id: str, value_name: str, start_year: int = 2010, end_year: int = 2025) -> pd.DataFrame:
    """
    Pull a World Bank indicator (annual frequency) for Hong Kong.

    Returns columns: year, <value_name>.
    """
    url = f"https://api.worldbank.org/v2/country/HKG/indicator/{indicator_id}?per_page=500&format=json"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    if len(data) < 2 or not isinstance(data[1], list):
        raise ValueError(f"Unexpected World Bank response for indicator {indicator_id}")

    records: List[Dict[str, float]] = []
    for entry in data[1]:
        year_text = entry.get("date")
        value = entry.get("value")
        if value is None or year_text is None:
            continue
        try:
            year = int(year_text)
        except ValueError:
            continue
        if start_year <= year <= end_year:
            records.append({"year": year, value_name: float(value)})

    out_df = pd.DataFrame(records)
    return out_df.sort_values("year").reset_index(drop=True)


def build_macro_dataset(start_year: int = 2014, end_year: int = 2020) -> pd.DataFrame:
    """
    Collect unemployment rate and CPI index from the World Bank for Hong Kong.
    Unemployment: SL.UEM.TOTL.ZS (total unemployment, %)
    CPI: FP.CPI.TOTL (2010 = 100)
    """
    unemployment = fetch_world_bank_indicator(
        indicator_id="SL.UEM.TOTL.ZS",
        value_name="unemployment_rate",
        start_year=start_year,
        end_year=end_year,
    )
    cpi = fetch_world_bank_indicator(
        indicator_id="FP.CPI.TOTL",
        value_name="cpi_index",
        start_year=start_year,
        end_year=end_year,
    )
    macro = pd.merge(unemployment, cpi, on="year", how="outer")
    return macro


def merge_macro(transactions: pd.DataFrame, macro: pd.DataFrame) -> pd.DataFrame:
    """Merge yearly macro data into the transaction dataframe."""
    merged = pd.merge(transactions, macro, on="year", how="left")
    return merged


# ---------- EDA ----------

def run_eda(df: pd.DataFrame, output_dir: Path = OUTPUT_DIR) -> None:
    """Perform quick EDA and export visualizations/statistics."""
    output_dir.mkdir(exist_ok=True)
    numeric_cols = ["price_hkd", "saleable_area", "gross_area", "price_per_saleable_sf", "price_per_gross_sf"]
    summary_stats = df[numeric_cols].describe()
    summary_stats.to_csv(output_dir / "summary_stats.csv")

    missing = df[numeric_cols].isna().sum().sort_values(ascending=False)
    missing.to_csv(output_dir / "missing_numeric_counts.csv")

    top_districts = df["district"].value_counts().head(10)
    top_districts.to_csv(output_dir / "top_districts.csv")

    # Distribution of price per saleable sqft.
    plt.figure(figsize=(8, 5))
    sns.histplot(x=df["price_per_saleable_sf"], bins=50, kde=True, color="steelblue")
    plt.xlabel("Price per saleable sqft (HKD)")
    plt.ylabel("Count")
    plt.title("Distribution of price per saleable sqft")
    plt.tight_layout()
    plt.savefig(output_dir / "price_per_saleable_distribution.png", dpi=150)
    plt.close()

    # Scatter: saleable area vs price per sqft.
    plt.figure(figsize=(8, 5))
    sns.scatterplot(
        data=df.sample(min(len(df), 5000), random_state=42),
        x="saleable_area",
        y="price_per_saleable_sf",
        hue="district",
        alpha=0.6,
        legend=False,
    )
    plt.xlabel("Saleable area (sqft)")
    plt.ylabel("Price per saleable sqft (HKD)")
    plt.title("Saleable area vs price per sqft")
    plt.tight_layout()
    plt.savefig(output_dir / "area_vs_price_scatter.png", dpi=150)
    plt.close()

    # Monthly median price trend.
    monthly = df.set_index("date")["price_per_saleable_sf"].resample("ME").median().dropna()
    monthly.to_csv(output_dir / "monthly_median_price.csv")
    plt.figure(figsize=(9, 5))
    monthly.plot()
    plt.ylabel("Median price per saleable sqft (HKD)")
    plt.title("Monthly median price per saleable sqft")
    plt.tight_layout()
    plt.savefig(output_dir / "monthly_median_price.png", dpi=150)
    plt.close()

    # Yearly view with macro overlay (unemployment).
    yearly = (
        df.groupby("year")
        .agg(
            median_price_per_saleable_sf=("price_per_saleable_sf", "median"),
            unemployment_rate=("unemployment_rate", "median"),
        )
        .dropna()
    )
    yearly.to_csv(output_dir / "yearly_price_macro_summary.csv")
    if not yearly.empty:
        fig, ax1 = plt.subplots(figsize=(9, 5))
        ax1.plot(yearly.index, yearly["median_price_per_saleable_sf"], marker="o", color="tab:blue", label="Median price/sf")
        ax1.set_ylabel("Median price per saleable sqft (HKD)", color="tab:blue")
        ax1.tick_params(axis="y", labelcolor="tab:blue")

        ax2 = ax1.twinx()
        ax2.plot(yearly.index, yearly["unemployment_rate"], marker="s", color="tab:red", label="Unemployment rate")
        ax2.set_ylabel("Unemployment rate (%)", color="tab:red")
        ax2.tick_params(axis="y", labelcolor="tab:red")

        plt.title("Yearly price per sqft vs unemployment")
        fig.tight_layout()
        plt.savefig(output_dir / "yearly_price_vs_unemployment.png", dpi=150)
        plt.close()


# ---------- Modeling ----------

def train_models(df: pd.DataFrame, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    """
    Train and evaluate two models to explain price per saleable square foot.
    Returns a dataframe with evaluation metrics saved to disk.
    """
    output_dir.mkdir(exist_ok=True)
    target = "price_per_saleable_sf"

    feature_columns = [
        "saleable_area",
        "gross_area",
        "floor_num",
        "holding_period_years",
        "winloss_pct",
        "pre_sale_flag",
        "unemployment_rate",
        "cpi_index",
        "year",
        "district",
    ]

    model_df = df.dropna(subset=feature_columns + [target]).copy()

    X = model_df[feature_columns]
    y = model_df[target]

    categorical_cols = ["district"]
    numeric_cols = [col for col in feature_columns if col not in categorical_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("numeric", "passthrough", numeric_cols),
        ]
    )

    models = {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(
            n_estimators=120, random_state=42, n_jobs=-1, min_samples_leaf=2
        ),
    }

    results = []
    feature_importances = None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    for name, model in models.items():
        clf = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)

        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        results.append({"model": name, "mae": mae, "r2": r2})

        if name == "RandomForest":
            # Extract feature importances for interpretation.
            model_step = clf.named_steps["model"]
            feature_names = clf.named_steps["preprocess"].get_feature_names_out()
            importances = pd.Series(model_step.feature_importances_, index=feature_names)
            feature_importances = (
                importances.sort_values(ascending=False)
                .head(15)
                .reset_index()
                .rename(columns={"index": "feature", 0: "importance"})
            )
            feature_importances.to_csv(output_dir / "feature_importances.csv", index=False)

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_dir / "model_performance.csv", index=False)

    print("Model evaluation results:")
    print(results_df)
    if feature_importances is not None:
        print("\nTop 15 random forest feature importances:")
        print(feature_importances)

    return results_df


# ---------- Main orchestration ----------

def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("Loading raw data from", DATA_PATH)
    raw_df = load_raw_data(DATA_PATH)
    print(f"Raw dataset shape: {raw_df.shape}")

    print("Cleaning transactions...")
    cleaned = clean_transactions(raw_df)
    print(f"Cleaned dataset shape: {cleaned.shape}")
    cleaned.to_csv(OUTPUT_DIR / "cleaned_transactions.csv", index=False)

    print("Fetching macro data...")
    macro = build_macro_dataset(start_year=2014, end_year=2020)
    macro.to_csv(OUTPUT_DIR / "macro_data.csv", index=False)

    print("Merging macro data...")
    merged = merge_macro(cleaned, macro)
    merged.to_csv(OUTPUT_DIR / "transactions_with_macro.csv", index=False)

    print("Running exploratory data analysis...")
    run_eda(merged, OUTPUT_DIR)

    print("Training models...")
    train_models(merged, OUTPUT_DIR)

    print(f"All artifacts saved to {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
