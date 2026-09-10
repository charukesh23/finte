
import pandas as pd
import numpy as np


def analyze_root_cause(df):
    """Analyze year-over-year financial movements and identify potential drivers."""

    results = []

    df = df.sort_values(
        ["company", "year"]
    ).reset_index(drop=True)

    for company, group in df.groupby("company"):

        group = group.sort_values("year").reset_index(drop=True)

        for i in range(1, len(group)):

            current = group.iloc[i]
            previous = group.iloc[i - 1]

            # -----------------------------
            # Growth calculations
            # -----------------------------

            revenue_growth = current.get(
                "revenue_yoy",
                np.nan
            )

            net_income_growth = current.get(
                "net_income_yoy",
                np.nan
            )

            # -----------------------------
            # Margin changes
            # -----------------------------

            gross_margin_change = (
                current["gross_margin_calculated"]
                - previous["gross_margin_calculated"]
            )

            ebitda_margin_change = (
                current["ebitda_margin_calculated"]
                - previous["ebitda_margin_calculated"]
            )

            net_margin_change = (
                current["net_margin_calculated"]
                - previous["net_margin_calculated"]
            )

            drivers = []

            # -----------------------------
            # Driver 1 — Gross Margin
            # -----------------------------

            if gross_margin_change <= -2:

                drivers.append({
                    "driver": "Gross Margin Pressure",
                    "change": round(
                        float(gross_margin_change), 2
                    ),
                    "unit": "percentage points"
                })

            # -----------------------------
            # Driver 2 — EBITDA Margin
            # -----------------------------

            if ebitda_margin_change <= -2:

                drivers.append({
                    "driver": "EBITDA Margin Pressure",
                    "change": round(
                        float(ebitda_margin_change), 2
                    ),
                    "unit": "percentage points"
                })

            # -----------------------------
            # Driver 3 — Liquidity
            # -----------------------------

            current_ratio_change = (
                current["current_ratio"]
                - previous["current_ratio"]
            )

            if current_ratio_change <= -0.2:

                drivers.append({
                    "driver": "Liquidity Deterioration",
                    "change": round(
                        float(current_ratio_change), 2
                    ),
                    "unit": "ratio points"
                })

            # -----------------------------
            # Driver 4 — Leverage
            # -----------------------------

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

                    drivers.append({
                        "driver": "Leverage Increase",
                        "change": round(
                            float(de_change), 2
                        ),
                        "unit": "percent"
                    })

            # -----------------------------
            # Overall assessment
            # -----------------------------

            if not drivers:
                assessment = (
                    "No major financial driver detected "
                    "under the current analytical thresholds."
                )

            else:

                driver_names = ", ".join(
                    d["driver"]
                    for d in drivers
                )

                assessment = (
                    "Primary areas requiring investigation: "
                    + driver_names
                    + "."
                )

            # -----------------------------
            # Investigation chain
            # -----------------------------

            chain = []

            if pd.notna(revenue_growth):
                chain.append(
                    f"Revenue changed {revenue_growth:.1f}% YoY."
                )

            if gross_margin_change <= -2:
                chain.append(
                    f"Gross Margin declined "
                    f"{abs(gross_margin_change):.2f} "
                    f"percentage points."
                )

            if ebitda_margin_change <= -2:
                chain.append(
                    f"EBITDA Margin declined "
                    f"{abs(ebitda_margin_change):.2f} "
                    f"percentage points."
                )

            if pd.notna(net_income_growth):
                chain.append(
                    f"Net Income changed "
                    f"{net_income_growth:.1f}% YoY."
                )

            results.append({
                "company": company,
                "year": int(current["year"]),
                "category": (
                    current["category"]
                    if "category" in current.index
                    else "Not provided"
                ),
                "revenue_growth": revenue_growth,
                "net_income_growth": net_income_growth,
                "gross_margin_change_pp": gross_margin_change,
                "ebitda_margin_change_pp": ebitda_margin_change,
                "net_margin_change_pp": net_margin_change,
                "driver_count": len(drivers),
                "drivers": drivers,
                "assessment": assessment,
                "investigation_chain": chain
            })

    return pd.DataFrame(results)


def get_root_cause_summary(root_cause_df):
    """Return summary of root-cause analysis."""

    if root_cause_df.empty:
        return {
            "periods_analyzed": 0,
            "periods_with_drivers": 0,
            "total_drivers": 0
        }

    return {
        "periods_analyzed": len(root_cause_df),
        "periods_with_drivers": int(
            (root_cause_df["driver_count"] > 0).sum()
        ),
        "total_drivers": int(
            root_cause_df["driver_count"].sum()
        )
    }
