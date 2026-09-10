
import pandas as pd
import numpy as np


def calculate_health_score(row):
    """Calculate a 0-100 financial health score."""

    # -----------------------------
    # Profitability Score (25%)
    # -----------------------------

    npm = row.get("net_profit_margin", np.nan)
    roe = row.get("roe", np.nan)

    profitability_score = 50

    if pd.notna(npm):
        if npm >= 20:
            profitability_score += 25
        elif npm >= 10:
            profitability_score += 15
        elif npm >= 0:
            profitability_score += 5
        else:
            profitability_score -= 20

    if pd.notna(roe):
        if roe >= 20:
            profitability_score += 25
        elif roe >= 10:
            profitability_score += 15
        elif roe >= 0:
            profitability_score += 5
        else:
            profitability_score -= 15

    profitability_score = np.clip(profitability_score, 0, 100)


    # -----------------------------
    # Growth Score (25%)
    # -----------------------------

    revenue_growth = row.get("revenue_yoy", np.nan)
    income_growth = row.get("net_income_yoy", np.nan)

    growth_score = 50

    if pd.notna(revenue_growth):
        if revenue_growth >= 15:
            growth_score += 25
        elif revenue_growth >= 5:
            growth_score += 15
        elif revenue_growth >= 0:
            growth_score += 5
        else:
            growth_score -= 15

    if pd.notna(income_growth):
        if income_growth >= 15:
            growth_score += 25
        elif income_growth >= 5:
            growth_score += 15
        elif income_growth >= 0:
            growth_score += 5
        else:
            growth_score -= 15

    growth_score = np.clip(growth_score, 0, 100)


    # -----------------------------
    # Liquidity Score (20%)
    # -----------------------------

    current_ratio = row.get("current_ratio", np.nan)

    if pd.isna(current_ratio):
        liquidity_score = 50
    elif current_ratio >= 2:
        liquidity_score = 100
    elif current_ratio >= 1.5:
        liquidity_score = 85
    elif current_ratio >= 1:
        liquidity_score = 70
    elif current_ratio >= 0.75:
        liquidity_score = 45
    else:
        liquidity_score = 20


    # -----------------------------
    # Leverage Score (20%)
    # -----------------------------

    debt_equity = row.get("debt_equity_ratio", np.nan)

    if pd.isna(debt_equity):
        leverage_score = 50
    elif debt_equity <= 0.5:
        leverage_score = 100
    elif debt_equity <= 1:
        leverage_score = 85
    elif debt_equity <= 2:
        leverage_score = 65
    elif debt_equity <= 3:
        leverage_score = 45
    else:
        leverage_score = 20


    # -----------------------------
    # Cash Flow Score (10%)
    # -----------------------------

    operating_cash = row.get(
        "cash_flow_from_operating",
        np.nan
    )

    net_income = row.get(
        "net_income",
        np.nan
    )

    if pd.isna(operating_cash):
        cash_flow_score = 50
    elif operating_cash > 0 and net_income > 0:
        cash_flow_score = 100
    elif operating_cash > 0:
        cash_flow_score = 70
    else:
        cash_flow_score = 20


    # -----------------------------
    # Weighted Health Score
    # -----------------------------

    health_score = (
        profitability_score * 0.25
        + growth_score * 0.25
        + liquidity_score * 0.20
        + leverage_score * 0.20
        + cash_flow_score * 0.10
    )

    return round(float(np.clip(health_score, 0, 100)), 1)


def classify_health(score):
    """Classify financial health."""

    if score >= 80:
        return "Excellent"
    elif score >= 65:
        return "Healthy"
    elif score >= 50:
        return "Moderate"
    elif score >= 35:
        return "Watch"
    else:
        return "High Risk"


def build_health_risk_scores(df, selected_year=None):
    """Build health and risk scores for latest company data."""

    if selected_year is not None:
        latest = df[df["year"] == selected_year].copy()
    else:
        latest = (
            df.sort_values("year")
            .groupby("company")
            .tail(1)
            .copy()
        )

    latest["health_score"] = latest.apply(
        calculate_health_score,
        axis=1
    )

    latest["risk_score"] = (
        100 - latest["health_score"]
    ).round(1)

    latest["health_classification"] = (
        latest["health_score"]
        .apply(classify_health)
    )

    # Category is optional for health scoring.
    # Do not infer or invent a category when it was not uploaded.
    if "category" not in latest.columns:
        latest["category"] = "Not provided"

    return latest[
        [
            "company",
            "category",
            "year",
            "health_score",
            "risk_score",
            "health_classification"
        ]
    ].sort_values(
        "health_score",
        ascending=False
    ).reset_index(drop=True)
