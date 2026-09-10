
import pandas as pd
import numpy as np


def load_financial_data(path="data/clean_data.csv"):
    """Load and prepare the financial dataset."""
    df = pd.read_csv(path)

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("(", "")
        .str.replace(")", "")
    )

    return df


def calculate_financial_metrics(df):
    """Calculate core financial metrics and YoY changes."""

    df = df.copy()

    # Sort for year-over-year calculations
    df = df.sort_values(["company", "year"]).reset_index(drop=True)

    # -----------------------------
    # Core calculated metrics
    # -----------------------------

    df["gross_margin_calculated"] = (
        df["gross_profit"] / df["revenue"] * 100
    )

    df["ebitda_margin_calculated"] = (
        df["ebitda"] / df["revenue"] * 100
    )

    df["net_margin_calculated"] = (
        df["net_income"] / df["revenue"] * 100
    )

    df["net_cash_flow"] = (
        df["cash_flow_from_operating"]
        + df["cash_flow_from_investing"]
        + df["cash_flow_from_financial_activities"]
    )

    # -----------------------------
    # Previous-year values
    # -----------------------------

    yoy_columns = [
        "revenue",
        "gross_profit",
        "net_income",
        "ebitda",
        "share_holder_equity",
        "cash_flow_from_operating",
        "current_ratio",
        "debt_equity_ratio",
        "net_profit_margin"
    ]

    for col in yoy_columns:
        df[f"{col}_previous"] = df.groupby("company")[col].shift(1)

        previous = df[f"{col}_previous"]

        # Safe YoY calculation
        df[f"{col}_yoy"] = np.where(
            previous != 0,
            ((df[col] - previous) / previous) * 100,
            np.nan
        )

    # -----------------------------
    # Margin changes
    # Use percentage-point change
    # -----------------------------

    for margin in [
        "gross_margin_calculated",
        "ebitda_margin_calculated",
        "net_margin_calculated"
    ]:
        previous_margin = df.groupby("company")[margin].shift(1)

        df[f"{margin}_previous"] = previous_margin

        df[f"{margin}_change_pp"] = (
            df[margin] - previous_margin
        )

    # Replace infinite values
    numeric_columns = df.select_dtypes(include=np.number).columns

    df[numeric_columns] = df[numeric_columns].replace(
        [np.inf, -np.inf],
        np.nan
    )

    return df


def build_financial_dataset(path="data/clean_data.csv"):
    """Load the dataset and calculate all financial metrics."""

    df = load_financial_data(path)

    df = calculate_financial_metrics(df)

    return df
