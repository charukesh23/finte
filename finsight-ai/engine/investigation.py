
import pandas as pd
import numpy as np


def generate_investigation(row):
    """Generate an evidence-based investigation for one anomaly."""

    finding_type = row["finding_type"]
    company = row["company"]
    year = row["year"]

    current = row["current_value"]
    previous = row["previous_value"]
    change = row["change"]

    # -----------------------------------------
    # Margin Compression
    # -----------------------------------------

    if finding_type == "Margin Compression":

        explanation = (
            f"{company}'s calculated net profit margin declined "
            f"from {previous:.2f}% to {current:.2f}% in {year}, "
            f"a change of {change:.2f} percentage points."
        )

        drivers = [
            "Review changes in gross margin",
            "Review operating cost movements",
            "Review interest and other expenses"
        ]

        recommendation = (
            "Investigate the main cost and margin drivers "
            "behind the decline in profitability."
        )

    # -----------------------------------------
    # Leverage Increase
    # -----------------------------------------

    elif finding_type == "Leverage Increase":

        explanation = (
            f"{company}'s debt-to-equity ratio increased "
            f"from {previous:.2f} to {current:.2f} in {year}, "
            f"representing a {change:.1f}% increase."
        )

        drivers = [
            "Review changes in debt levels",
            "Review changes in shareholder equity",
            "Assess financing requirements"
        ]

        recommendation = (
            "Review the company's financing structure and "
            "determine whether increased leverage requires attention."
        )

    # -----------------------------------------
    # Liquidity Deterioration
    # -----------------------------------------

    elif finding_type == "Liquidity Deterioration":

        explanation = (
            f"{company}'s current ratio declined "
            f"from {previous:.2f} to {current:.2f} in {year}, "
            f"a {change:.1f}% decline."
        )

        drivers = [
            "Review current asset movements",
            "Review current liability movements",
            "Investigate working-capital changes"
        ]

        recommendation = (
            "Review short-term assets and liabilities to "
            "understand the deterioration in liquidity."
        )

    # -----------------------------------------
    # Revenue-Profit Divergence
    # -----------------------------------------

    elif finding_type == "Revenue-Profit Divergence":

        explanation = (
            f"{company}'s revenue increased while net income "
            f"declined by {abs(change):.1f}% in {year}. "
            "This indicates a potential profitability divergence."
        )

        drivers = [
            "Review gross margin pressure",
            "Review operating expenses",
            "Review financing and other expenses"
        ]

        recommendation = (
            "Investigate why revenue growth did not translate "
            "into higher profitability."
        )

    # -----------------------------------------
    # Earnings-Cash Flow Divergence
    # -----------------------------------------

    elif finding_type == "Earnings-Cash Flow Divergence":

        explanation = (
            f"{company} reported positive net income of "
            f"{previous:.2f} while operating cash flow was "
            f"{current:.2f} in {year}."
        )

        drivers = [
            "Review working-capital movements",
            "Review receivables and inventory",
            "Review non-cash earnings adjustments"
        ]

        recommendation = (
            "Investigate the difference between reported earnings "
            "and operating cash generation."
        )

    # -----------------------------------------
    # Profitability Lag
    # -----------------------------------------

    elif finding_type == "Profitability Lag":

        explanation = (
            f"{company}'s revenue growth exceeded net income growth "
            f"by {abs(change):.1f} percentage points in {year}."
        )

        drivers = [
            "Review margin movements",
            "Review operating cost growth",
            "Review changes in financing costs"
        ]

        recommendation = (
            "Investigate the factors causing profitability "
            "to lag behind revenue growth."
        )

    else:

        explanation = (
            f"A financial anomaly was detected for {company} "
            f"in {year}."
        )

        drivers = [
            "Review underlying financial metrics"
        ]

        recommendation = (
            "Perform additional financial review."
        )

    return {
        "investigation_id": f"{company}_{year}",
        "company": company,
        "year": year,
        "category": row["category"],
        "finding_type": finding_type,
        "severity": row["severity"],
        "title": row["title"],
        "explanation": explanation,
        "possible_drivers": drivers,
        "recommendation": recommendation,
        "evidence_current": current,
        "evidence_previous": previous,
        "evidence_change": change
    }


def build_investigations(anomaly_df):
    """Generate investigations for all anomaly findings."""

    if anomaly_df.empty:
        return pd.DataFrame()

    investigations = []

    for _, row in anomaly_df.iterrows():
        investigations.append(
            generate_investigation(row)
        )

    return pd.DataFrame(investigations)


def get_investigation_summary(investigation_df):
    """Return investigation summary."""

    if investigation_df.empty:
        return {
            "total_investigations": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

    return {
        "total_investigations": len(investigation_df),
        "high": int(
            (investigation_df["severity"] == "HIGH").sum()
        ),
        "medium": int(
            (investigation_df["severity"] == "MEDIUM").sum()
        ),
        "low": int(
            (investigation_df["severity"] == "LOW").sum()
        )
    }
