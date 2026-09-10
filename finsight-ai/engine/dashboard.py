
import pandas as pd


def get_company_snapshot(financial_df, company, year):
    """
    Return the selected company's financial snapshot
    for the requested year.
    """

    company_df = financial_df[
        financial_df["company"] == company
    ].copy()

    current_rows = company_df[
        company_df["year"] == year
    ]

    if current_rows.empty:
        raise ValueError(
            f"No financial data found for {company} {year}"
        )

    current = current_rows.iloc[0]

    return {
        "company": company,
        "year": int(year),

        "revenue": float(current["revenue"]),
        "gross_profit": float(current["gross_profit"]),
        "net_income": float(current["net_income"]),
        "ebitda": float(current["ebitda"]),

        "net_profit_margin": float(
            current["net_profit_margin"]
        ),

        "current_ratio": float(
            current["current_ratio"]
        ),

        "debt_equity_ratio": float(
            current["debt_equity_ratio"]
        ),

        "roe": (
            float(current["roe"])
            if "roe" in current.index
            else None
        ),

        "roa": (
            float(current["roa"])
            if "roa" in current.index
            else None
        ),

        "roi": (
            float(current["roi"])
            if "roi" in current.index
            else None
        ),

        "operating_cash_flow": float(
            current["cash_flow_from_operating"]
        )
    }


def get_company_trend(financial_df, company):
    """
    Return historical financial trends
    for the selected company.
    """

    company_df = financial_df[
        financial_df["company"] == company
    ].copy()

    company_df = company_df.sort_values("year")

    company_df["gross_margin"] = (
        company_df["gross_profit"]
        / company_df["revenue"]
    ) * 100

    company_df["ebitda_margin"] = (
        company_df["ebitda"]
        / company_df["revenue"]
    ) * 100

    return company_df[
        [
            "year",
            "revenue",
            "net_income",
            "ebitda",
            "gross_margin",
            "ebitda_margin",
            "net_profit_margin"
        ]
    ].reset_index(drop=True)
