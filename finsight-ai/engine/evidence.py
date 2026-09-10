
import pandas as pd
import numpy as np


def build_evidence(
    financial_df: pd.DataFrame,
    company: str,
    year: int
) -> dict:

    df = financial_df.copy()
    df = df.sort_values(["company", "year"])

    company_df = df[df["company"] == company].copy()

    current_rows = company_df[company_df["year"] == year]

    if current_rows.empty:
        raise ValueError(
            f"No financial data found for {company} in {year}"
        )

    current = current_rows.iloc[0]

    previous_rows = company_df[
        company_df["year"] < year
    ].sort_values("year")

    previous = (
        previous_rows.iloc[-1]
        if not previous_rows.empty
        else None
    )

    evidence = {
        "company": company,
        "year": int(year),
        "current": {},
        "previous": {},
        "changes": [],
        "evidence_count": 0
    }

    metrics = [
        "revenue",
        "net_income",
        "gross_profit",
        "ebitda",
        "current_ratio",
        "debt_equity_ratio",
        "net_profit_margin"
    ]

    for metric in metrics:

        current_value = current.get(metric, np.nan)

        if pd.notna(current_value):
            evidence["current"][metric] = float(current_value)

        if previous is not None:
            previous_value = previous.get(metric, np.nan)

            if pd.notna(previous_value):
                evidence["previous"][metric] = float(previous_value)

    if previous is not None:

        # Revenue
        prev_revenue = previous["revenue"]
        curr_revenue = current["revenue"]

        if pd.notna(prev_revenue) and prev_revenue != 0:

            revenue_growth = (
                (curr_revenue - prev_revenue)
                / abs(prev_revenue)
            ) * 100

            evidence["changes"].append({
                "metric": "Revenue",
                "current": round(float(curr_revenue), 2),
                "previous": round(float(prev_revenue), 2),
                "change": round(float(revenue_growth), 2),
                "unit": "%",
                "evidence_type": "YoY Growth"
            })

        # Net Income
        prev_income = previous["net_income"]
        curr_income = current["net_income"]

        if pd.notna(prev_income) and prev_income != 0:

            income_growth = (
                (curr_income - prev_income)
                / abs(prev_income)
            ) * 100

            evidence["changes"].append({
                "metric": "Net Income",
                "current": round(float(curr_income), 2),
                "previous": round(float(prev_income), 2),
                "change": round(float(income_growth), 2),
                "unit": "%",
                "evidence_type": "YoY Growth"
            })

        # Gross Margin
        prev_gm = (
            previous["gross_profit"]
            / previous["revenue"]
        ) * 100

        curr_gm = (
            current["gross_profit"]
            / current["revenue"]
        ) * 100

        evidence["changes"].append({
            "metric": "Gross Margin",
            "current": round(float(curr_gm), 2),
            "previous": round(float(prev_gm), 2),
            "change": round(float(curr_gm - prev_gm), 2),
            "unit": "percentage points",
            "evidence_type": "Margin Change"
        })

        # EBITDA Margin
        prev_ebitda_margin = (
            previous["ebitda"]
            / previous["revenue"]
        ) * 100

        curr_ebitda_margin = (
            current["ebitda"]
            / current["revenue"]
        ) * 100

        evidence["changes"].append({
            "metric": "EBITDA Margin",
            "current": round(float(curr_ebitda_margin), 2),
            "previous": round(float(prev_ebitda_margin), 2),
            "change": round(
                float(curr_ebitda_margin - prev_ebitda_margin),
                2
            ),
            "unit": "percentage points",
            "evidence_type": "Margin Change"
        })

        # Current Ratio
        prev_ratio = previous["current_ratio"]
        curr_ratio = current["current_ratio"]

        if pd.notna(prev_ratio) and pd.notna(curr_ratio):

            evidence["changes"].append({
                "metric": "Current Ratio",
                "current": round(float(curr_ratio), 2),
                "previous": round(float(prev_ratio), 2),
                "change": round(float(curr_ratio - prev_ratio), 2),
                "unit": "x",
                "evidence_type": "Liquidity Change"
            })

        # Debt / Equity
        prev_de = previous["debt_equity_ratio"]
        curr_de = current["debt_equity_ratio"]

        if (
            pd.notna(prev_de)
            and pd.notna(curr_de)
            and prev_de != 0
        ):

            de_change = (
                (curr_de - prev_de)
                / abs(prev_de)
            ) * 100

            evidence["changes"].append({
                "metric": "Debt/Equity",
                "current": round(float(curr_de), 2),
                "previous": round(float(prev_de), 2),
                "change": round(float(de_change), 2),
                "unit": "%",
                "evidence_type": "Leverage Change"
            })

    evidence["evidence_count"] = len(evidence["changes"])

    return evidence
