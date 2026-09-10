import re
import pandas as pd


# ============================================================
# FINANCIAL COLUMN ALIASES
# ============================================================

COLUMN_ALIASES = {
    "year": [
        "year",
        "financial_year",
        "fiscal_year",
        "fy",
        "period"
    ],

    "company": [
        "company",
        "company_name",
        "organization",
        "organisation",
        "entity"
    ],

    "category": [
        "category",
        "sector",
        "industry",
        "company_category"
    ],

    "revenue": [
        "revenue",
        "sales",
        "total_sales",
        "net_sales",
        "turnover",
        "total_revenue"
    ],

    "gross_profit": [
        "gross_profit",
        "gross_profit_amount"
    ],

    "net_income": [
        "net_income",
        "net_profit",
        "profit_after_tax",
        "pat",
        "net_earnings",
        "earnings"
    ],

    "ebitda": [
        "ebitda"
    ],

    "share_holder_equity": [
        "share_holder_equity",
        "shareholders_equity",
        "shareholder_equity",
        "stockholders_equity",
        "equity",
        "total_equity"
    ],

    "cash_flow_from_operating": [
        "cash_flow_from_operating",
        "operating_cash_flow",
        "cash_from_operations",
        "cash_flow_operating",
        "ocf"
    ],

    "cash_flow_from_investing": [
        "cash_flow_from_investing",
        "investing_cash_flow",
        "cash_from_investing"
    ],

    "cash_flow_from_financial_activities": [
        "cash_flow_from_financial_activities",
        "financing_cash_flow",
        "cash_flow_from_financing",
        "cash_from_financing"
    ],

    "current_ratio": [
        "current_ratio"
    ],

    "debt_equity_ratio": [
        "debt_equity_ratio",
        "debt_to_equity",
        "debt_to_equity_ratio",
        "d_e_ratio"
    ],

    "roe": [
        "roe",
        "return_on_equity",
        "return_on_shareholders_equity"
    ],

    "roa": [
        "roa",
        "return_on_assets"
    ],

    "roi": [
        "roi",
        "return_on_investment"
    ],

    "net_profit_margin": [
        "net_profit_margin",
        "net_margin",
        "profit_margin",
        "net_margin_percent"
    ],

    "free_cash_flow_per_share": [
        "free_cash_flow_per_share",
        "fcf_per_share"
    ],

    "return_on_tangible_equity": [
        "return_on_tangible_equity",
        "rote"
    ],

    "number_of_employees": [
        "number_of_employees",
        "employees",
        "employee_count",
        "total_employees"
    ],

    "market_capin_b_usd": [
        "market_capin_b_usd",
        "market_cap",
        "market_cap_b_usd",
        "market_capitalization"
    ],

    "inflation_ratein_us": [
        "inflation_ratein_us",
        "inflation_rate",
        "us_inflation",
        "inflation"
    ]
}


def normalize_column_name(column):
    """Convert a column name into a consistent comparison format."""

    column = str(column).strip().lower()

    column = re.sub(r"[^a-z0-9]+", "_", column)

    column = re.sub(r"_+", "_", column)

    return column.strip("_")


def build_alias_lookup():
    """Build reverse lookup from aliases to standard FinSight names."""

    lookup = {}

    for standard_name, aliases in COLUMN_ALIASES.items():

        for alias in aliases:
            lookup[normalize_column_name(alias)] = standard_name

    return lookup


def map_financial_columns(df):
    """
    Map uploaded financial column names to FinSight standard names.

    Returns:
        mapped_df
        mapping
        unmapped_columns
    """

    df = df.copy()

    alias_lookup = build_alias_lookup()

    mapping = {}
    unmapped_columns = []

    for column in df.columns:

        normalized = normalize_column_name(column)

        if normalized in alias_lookup:

            standard_name = alias_lookup[normalized]

            if standard_name not in mapping.values():
                mapping[column] = standard_name

            else:
                unmapped_columns.append(column)

        else:
            unmapped_columns.append(column)

    mapped_df = df.rename(columns=mapping)

    return mapped_df, mapping, unmapped_columns


def derive_financial_columns(df):
    """
    Derive safe financial metrics that can be calculated
    directly from uploaded core financial fields.

    Does not invent unavailable metrics such as ROE, ROA, or ROI.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # Net Profit Margin
    # ---------------------------------------------------------
    if "net_profit_margin" not in df.columns:
        if (
            "net_income" in df.columns
            and "revenue" in df.columns
        ):
            revenue = pd.to_numeric(
                df["revenue"],
                errors="coerce"
            )

            net_income = pd.to_numeric(
                df["net_income"],
                errors="coerce"
            )

            df["net_profit_margin"] = (
                net_income / revenue
            ) * 100

    return df
