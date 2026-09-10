
import pandas as pd
import numpy as np


def build_peer_benchmark(df, selected_year=None):
    """Compare companies against peers in the same category."""

    # Category is required to identify comparable companies.
    # Do not infer or invent peer categories for uploaded data.
    if "category" not in df.columns:
        return pd.DataFrame([{
            "company": (
                df["company"].iloc[0]
                if "company" in df.columns and not df.empty
                else None
            ),
            "category": None,
            "year": selected_year,
            "peer_count": 0,
            "peer_status": "UNAVAILABLE",
            "unavailable_reason": (
                "Category/sector information was not provided "
                "in the uploaded financial data."
            )
        }])

    records = []

    # Use the selected financial year when provided.
    # Otherwise, fall back to each company's latest available year.
    if selected_year is not None:

        latest_df = df[
            df["year"] == selected_year
        ].copy()

    else:

        latest_years = (
            df.groupby("company")["year"]
            .max()
            .reset_index()
            .rename(columns={"year": "latest_year"})
        )

        latest_df = df.merge(
            latest_years,
            on="company",
            how="inner"
        )

        latest_df = latest_df[
            latest_df["year"] == latest_df["latest_year"]
        ].copy()

    metrics = [
        "revenue",
        "net_income",
        "net_profit_margin",
        "current_ratio",
        "debt_equity_ratio"
    ]

    # Optional metrics are included only when provided.
    # Never invent unavailable financial metrics.
    optional_metrics = ["roe", "roa", "roi"]

    for metric in optional_metrics:
        if metric in latest_df.columns:
            metrics.append(metric)

    for _, company_row in latest_df.iterrows():

        company = company_row["company"]
        category = company_row["category"]
        year = company_row["year"]

        # Same-category companies
        peers = latest_df[
            (latest_df["category"] == category)
            & (latest_df["company"] != company)
        ]

        record = {
            "company": company,
            "category": category,
            "year": year,
            "peer_count": len(peers)
        }

        if len(peers) == 0:
            record["peer_status"] = "No true peer available"

            for metric in metrics:
                record[f"{metric}_company"] = company_row[metric]
                record[f"{metric}_peer_avg"] = np.nan
                record[f"{metric}_vs_peer_pct"] = np.nan

        else:
            record["peer_status"] = "Peer benchmark available"

            for metric in metrics:

                company_value = company_row[metric]
                peer_average = peers[metric].mean()

                if (
                    pd.notna(peer_average)
                    and peer_average != 0
                ):
                    difference_pct = (
                        (company_value - peer_average)
                        / abs(peer_average)
                    ) * 100
                else:
                    difference_pct = np.nan

                record[f"{metric}_company"] = company_value
                record[f"{metric}_peer_avg"] = peer_average
                record[f"{metric}_vs_peer_pct"] = difference_pct

        records.append(record)

    return pd.DataFrame(records)


def get_benchmark_summary(benchmark_df):
    """Return peer benchmarking summary."""

    if benchmark_df.empty:
        return {
            "companies_benchmarked": 0,
            "peer_available": 0,
            "no_peer_available": 0
        }

    return {
        "companies_benchmarked": len(benchmark_df),
        "peer_available": int(
            (benchmark_df["peer_status"] == "Peer benchmark available").sum()
        ),
        "no_peer_available": int(
            (benchmark_df["peer_status"] == "No true peer available").sum()
        )
    }
