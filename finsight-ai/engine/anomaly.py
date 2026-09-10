
import pandas as pd
import numpy as np


def detect_anomalies(df):
    """Detect unusual financial movements and generate review findings."""

    findings = []

    # Ensure chronological order
    df = df.sort_values(["company", "year"]).reset_index(drop=True)

    for company, group in df.groupby("company"):

        group = group.sort_values("year").reset_index(drop=True)

        for i in range(1, len(group)):

            current = group.iloc[i]
            previous = group.iloc[i - 1]

            year = int(current["year"])

            # -----------------------------------------
            # 1. Margin Compression
            # -----------------------------------------

            margin_change = (
                current["net_margin_calculated"]
                - previous["net_margin_calculated"]
            )

            if margin_change <= -3:

                severity = (
                    "HIGH" if margin_change <= -7
                    else "MEDIUM"
                )

                findings.append({
                    "company": company,
                    "year": year,
                    "category": current["category"],
                    "finding_type": "Margin Compression",
                    "severity": severity,
                    "title": "Net profit margin declined materially",
                    "metric": "Net Profit Margin",
                    "current_value": current["net_margin_calculated"],
                    "previous_value": previous["net_margin_calculated"],
                    "change": margin_change
                })

            # -----------------------------------------
            # 2. Leverage Increase
            # -----------------------------------------

            previous_de = previous["debt_equity_ratio"]

            if (
                pd.notna(previous_de)
                and previous_de > 0
            ):

                de_change = (
                    (current["debt_equity_ratio"] - previous_de)
                    / previous_de
                ) * 100

                if de_change >= 20:

                    severity = (
                        "HIGH" if de_change >= 50
                        else "MEDIUM"
                    )

                    findings.append({
                        "company": company,
                        "year": year,
                        "category": current["category"],
                        "finding_type": "Leverage Increase",
                        "severity": severity,
                        "title": "Debt-to-equity ratio increased materially",
                        "metric": "Debt/Equity Ratio",
                        "current_value": current["debt_equity_ratio"],
                        "previous_value": previous_de,
                        "change": de_change
                    })

            # -----------------------------------------
            # 3. Liquidity Deterioration
            # -----------------------------------------

            previous_current_ratio = previous["current_ratio"]

            if (
                pd.notna(previous_current_ratio)
                and previous_current_ratio > 0
            ):

                liquidity_change = (
                    (current["current_ratio"] - previous_current_ratio)
                    / previous_current_ratio
                ) * 100

                if liquidity_change <= -20:

                    severity = (
                        "HIGH" if liquidity_change <= -40
                        else "MEDIUM"
                    )

                    findings.append({
                        "company": company,
                        "year": year,
                        "category": current["category"],
                        "finding_type": "Liquidity Deterioration",
                        "severity": severity,
                        "title": "Current ratio declined materially",
                        "metric": "Current Ratio",
                        "current_value": current["current_ratio"],
                        "previous_value": previous_current_ratio,
                        "change": liquidity_change
                    })

            # -----------------------------------------
            # 4. Revenue-Profit Divergence
            # -----------------------------------------

            revenue_previous = previous["revenue"]
            income_previous = previous["net_income"]

            if (
                revenue_previous != 0
                and income_previous != 0
            ):

                revenue_growth = (
                    (current["revenue"] - revenue_previous)
                    / abs(revenue_previous)
                ) * 100

                income_growth = (
                    (current["net_income"] - income_previous)
                    / abs(income_previous)
                ) * 100

                # Revenue grows while profit declines
                if (
                    revenue_growth >= 10
                    and income_growth <= -5
                ):

                    findings.append({
                        "company": company,
                        "year": year,
                        "category": current["category"],
                        "finding_type": "Revenue-Profit Divergence",
                        "severity": "HIGH",
                        "title": "Revenue increased while net income declined",
                        "metric": "Revenue vs Net Income",
                        "current_value": current["net_income"],
                        "previous_value": income_previous,
                        "change": income_growth
                    })

            # -----------------------------------------
            # 5. Earnings-Cash Flow Divergence
            # -----------------------------------------

            net_income = current["net_income"]
            operating_cash = current["cash_flow_from_operating"]

            if (
                net_income > 0
                and operating_cash < 0
            ):

                findings.append({
                    "company": company,
                    "year": year,
                    "category": current["category"],
                    "finding_type": "Earnings-Cash Flow Divergence",
                    "severity": "HIGH",
                    "title": "Positive earnings with negative operating cash flow",
                    "metric": "Net Income vs Operating Cash Flow",
                    "current_value": operating_cash,
                    "previous_value": net_income,
                    "change": np.nan
                })

            # -----------------------------------------
            # 6. Profitability Lag
            # -----------------------------------------

            revenue_growth = current.get("revenue_yoy", np.nan)
            net_income_growth = current.get("net_income_yoy", np.nan)

            if (
                pd.notna(revenue_growth)
                and pd.notna(net_income_growth)
                and revenue_growth >= 10
                and net_income_growth < revenue_growth - 20
            ):

                findings.append({
                    "company": company,
                    "year": year,
                    "category": current["category"],
                    "finding_type": "Profitability Lag",
                    "severity": "MEDIUM",
                    "title": "Profit growth is lagging revenue growth",
                    "metric": "Revenue Growth vs Net Income Growth",
                    "current_value": net_income_growth,
                    "previous_value": revenue_growth,
                    "change": net_income_growth - revenue_growth
                })

    anomaly_columns = [
        "company",
        "year",
        "category",
        "finding_type",
        "severity",
        "title",
        "metric",
        "current_value",
        "previous_value",
        "change"
    ]

    return pd.DataFrame(
        findings,
        columns=anomaly_columns
    )


def get_anomaly_summary(findings):
    """Return summary statistics for detected anomalies."""

    if findings.empty:
        return {
            "total_findings": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

    return {
        "total_findings": len(findings),
        "high": int((findings["severity"] == "HIGH").sum()),
        "medium": int((findings["severity"] == "MEDIUM").sum()),
        "low": int((findings["severity"] == "LOW").sum())
    }
