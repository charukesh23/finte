
import pandas as pd
import numpy as np


def build_financial_map(df, company=None, year=None):
    """Build financial intelligence map data for a company/year."""

    if company is None:
        company = df["company"].iloc[0]

    company_data = df[
        df["company"] == company
    ].copy()

    if company_data.empty:
        raise ValueError(f"Company {company} not found.")

    # Use latest year if year is not provided
    if year is None:
        year = int(company_data["year"].max())

    row_data = company_data[
        company_data["year"] == year
    ]

    if row_data.empty:
        raise ValueError(
            f"No financial data available for {company} in {year}."
        )

    row = row_data.iloc[0]

    # -----------------------------------------
    # Financial metric nodes
    # -----------------------------------------

    nodes = [
        {
            "id": "revenue",
            "label": "Revenue",
            "value": float(row["revenue"]),
            "unit": "USD M"
        },
        {
            "id": "gross_profit",
            "label": "Gross Profit",
            "value": float(row["gross_profit"]),
            "unit": "USD M"
        },
        {
            "id": "ebitda",
            "label": "EBITDA",
            "value": float(row["ebitda"]),
            "unit": "USD M"
        },
        {
            "id": "net_income",
            "label": "Net Income",
            "value": float(row["net_income"]),
            "unit": "USD M"
        },
        {
            "id": "operating_cash",
            "label": "Operating Cash Flow",
            "value": float(row["cash_flow_from_operating"]),
            "unit": "USD M"
        },
        {
            "id": "current_ratio",
            "label": "Current Ratio",
            "value": float(row["current_ratio"]),
            "unit": "x"
        },
        {
            "id": "debt_equity",
            "label": "Debt / Equity",
            "value": float(row["debt_equity_ratio"]),
            "unit": "x"
        },
        {
            "id": "net_margin",
            "label": "Net Profit Margin",
            "value": float(row["net_profit_margin"]),
            "unit": "%"
        }
    ]

    # -----------------------------------------
    # Optional return metrics
    # -----------------------------------------

    optional_return_metrics = [
        ("roe", "ROE"),
        ("roa", "ROA"),
        ("roi", "ROI")
    ]

    for metric_id, metric_label in optional_return_metrics:

        if metric_id in row.index:
            nodes.append({
                "id": metric_id,
                "label": metric_label,
                "value": float(row[metric_id]),
                "unit": "%"
            })

    # -----------------------------------------
    # Analytical relationships
    # -----------------------------------------

    edges = [
        {
            "source": "revenue",
            "target": "gross_profit",
            "relationship": "Revenue contributes to Gross Profit"
        },
        {
            "source": "gross_profit",
            "target": "ebitda",
            "relationship": "Gross Profit contributes to EBITDA"
        },
        {
            "source": "ebitda",
            "target": "net_income",
            "relationship": "EBITDA contributes to Net Income"
        },
        {
            "source": "net_income",
            "target": "operating_cash",
            "relationship": "Compare earnings with operating cash generation"
        },
        {
            "source": "current_ratio",
            "target": "net_income",
            "relationship": "Liquidity context"
        },
        {
            "source": "debt_equity",
            "target": "net_income",
            "relationship": "Leverage context"
        }
    ]

    # Add relationships only when the corresponding
    # optional return metric is actually available.
    for metric_id, _ in optional_return_metrics:

        if metric_id in row.index:
            edges.append({
                "source": "net_income",
                "target": metric_id,
                "relationship": f"Net Income influences {metric_id.upper()}"
            })

    return {
        "company": company,
        "year": year,
        "nodes": nodes,
        "edges": edges
    }


def get_map_summary(financial_map):
    """Return summary information for the financial map."""

    return {
        "company": financial_map["company"],
        "year": financial_map["year"],
        "node_count": len(financial_map["nodes"]),
        "edge_count": len(financial_map["edges"])
    }
