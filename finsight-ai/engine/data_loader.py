
import pandas as pd


def load_application_data(data_path="data/clean_data.csv"):
    """
    Load and prepare the financial dataset
    for the FinSight AI application.
    """

    df = pd.read_csv(data_path)

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("/", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    # Standardize category values
    if "category" in df.columns:
        df["category"] = (
            df["category"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

    # Sort financial records
    df = df.sort_values(
        ["company", "year"]
    ).reset_index(drop=True)

    return df


def get_companies(df):
    """Return sorted company list."""

    return sorted(
        df["company"].dropna().unique().tolist()
    )


def get_years(df, company):
    """Return available years for a company."""

    return sorted(
        df.loc[
            df["company"] == company,
            "year"
        ].dropna().unique().tolist()
    )
