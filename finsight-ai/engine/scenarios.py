
import pandas as pd
import numpy as np


def run_scenario(
    df,
    company,
    year=None,
    revenue_growth=0,
    target_margin=None
):
    """
    Run a what-if financial scenario.

    revenue_growth:
        Revenue change as a percentage.
        Example: 10 means +10%.

    target_margin:
        Optional target net profit margin.
        Example: 30 means 30%.
    """

    company_data = df[
        df["company"] == company
    ].copy()

    if company_data.empty:
        raise ValueError(
            f"Company {company} not found."
        )

    # Use latest year when year is not specified
    if year is None:
        year = int(company_data["year"].max())

    selected = company_data[
        company_data["year"] == year
    ]

    if selected.empty:
        raise ValueError(
            f"No data available for {company} in {year}."
        )

    row = selected.iloc[0]

    # -----------------------------------------
    # Current financial values
    # -----------------------------------------

    current_revenue = float(row["revenue"])
    current_net_income = float(row["net_income"])

    current_margin = (
        current_net_income
        / current_revenue
        * 100
    )

    # -----------------------------------------
    # Scenario revenue
    # -----------------------------------------

    projected_revenue = (
        current_revenue
        * (1 + revenue_growth / 100)
    )

    # -----------------------------------------
    # Scenario margin
    # -----------------------------------------

    if target_margin is None:
        scenario_margin = current_margin
    else:
        scenario_margin = target_margin

    # -----------------------------------------
    # Projected net income
    # -----------------------------------------

    projected_net_income = (
        projected_revenue
        * scenario_margin
        / 100
    )

    # -----------------------------------------
    # Impact
    # -----------------------------------------

    income_change = (
        projected_net_income
        - current_net_income
    )

    if current_net_income != 0:
        income_change_pct = (
            income_change
            / abs(current_net_income)
            * 100
        )
    else:
        income_change_pct = np.nan

    # -----------------------------------------
    # Scenario interpretation
    # -----------------------------------------

    if income_change > 0:
        impact = "Positive"
    elif income_change < 0:
        impact = "Negative"
    else:
        impact = "Neutral"

    return {
        "company": company,
        "year": year,

        "current_revenue": current_revenue,
        "projected_revenue": projected_revenue,

        "current_net_income": current_net_income,
        "projected_net_income": projected_net_income,

        "current_margin": current_margin,
        "scenario_margin": scenario_margin,

        "revenue_growth": revenue_growth,
        "income_change": income_change,
        "income_change_pct": income_change_pct,

        "impact": impact,

        "assumptions": {
            "revenue_growth_percent": revenue_growth,
            "target_net_margin_percent": target_margin,
            "scenario_type": "What-if scenario, not a forecast"
        }
    }


def compare_scenarios(
    df,
    company,
    year=None,
    scenarios=None
):
    """
    Run multiple what-if scenarios.
    """

    if scenarios is None:
        scenarios = [
            {
                "name": "Revenue +10%",
                "revenue_growth": 10,
                "target_margin": None
            },
            {
                "name": "Margin → 30%",
                "revenue_growth": 0,
                "target_margin": 30
            },
            {
                "name": "Revenue +10% + Margin 30%",
                "revenue_growth": 10,
                "target_margin": 30
            }
        ]

    results = []

    for scenario in scenarios:

        result = run_scenario(
            df=df,
            company=company,
            year=year,
            revenue_growth=scenario["revenue_growth"],
            target_margin=scenario["target_margin"]
        )

        result["scenario_name"] = scenario["name"]

        results.append(result)

    return pd.DataFrame(results)
