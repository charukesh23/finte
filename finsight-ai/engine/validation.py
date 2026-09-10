
import pandas as pd
import numpy as np


def run_validation(df):
    """Run FinSight AI validation test cases."""

    results = []

    # -----------------------------------------
    # TC01 — Revenue Check
    # -----------------------------------------
    revenue_valid = (
        df["revenue"].notna()
        & np.isfinite(df["revenue"])
    )

    results.append({
        "test_id": "TC01",
        "test_name": "Revenue Check",
        "status": "PASS" if revenue_valid.all() else "REVIEW",
        "records_checked": len(df),
        "records_passed": int(revenue_valid.sum()),
        "records_failed": int((~revenue_valid).sum()),
        "description": "Verify revenue values are numeric and available"
    })

    # -----------------------------------------
    # TC02 — Net Income Check
    # -----------------------------------------
    income_valid = (
        df["net_income"].notna()
        & np.isfinite(df["net_income"])
    )

    results.append({
        "test_id": "TC02",
        "test_name": "Net Income Check",
        "status": "PASS" if income_valid.all() else "REVIEW",
        "records_checked": len(df),
        "records_passed": int(income_valid.sum()),
        "records_failed": int((~income_valid).sum()),
        "description": "Verify net income values are numeric and available"
    })

    # -----------------------------------------
    # TC03 — Profit Margin Check
    # -----------------------------------------
    calculated_margin = (
        df["net_income"] / df["revenue"] * 100
    )

    margin_difference = (
        calculated_margin - df["net_profit_margin"]
    ).abs()

    tolerance = 0.5

    margin_valid = margin_difference <= tolerance

    results.append({
        "test_id": "TC03",
        "test_name": "Profit Margin Check",
        "status": "PASS" if margin_valid.all() else "REVIEW",
        "records_checked": len(df),
        "records_passed": int(margin_valid.sum()),
        "records_failed": int((~margin_valid).sum()),
        "max_difference": round(float(margin_difference.max()), 4),
        "description": "Evaluate whether reported profit margin agrees with calculated margin"
    })

    # -----------------------------------------
    # TC04 — ROE Check
    # -----------------------------------------
    if "roe" in df.columns:

        roe_valid = (
            df["roe"].notna()
            & np.isfinite(df["roe"])
        )

        results.append({
            "test_id": "TC04",
            "test_name": "ROE Check",
            "status": "PASS" if roe_valid.all() else "REVIEW",
            "records_checked": len(df),
            "records_passed": int(roe_valid.sum()),
            "records_failed": int((~roe_valid).sum()),
            "description": "Evaluate return generated on shareholder equity"
        })

    else:

        results.append({
            "test_id": "TC04",
            "test_name": "ROE Check",
            "status": "UNAVAILABLE",
            "records_checked": 0,
            "records_passed": 0,
            "records_failed": 0,
            "description": "ROE was not provided in the uploaded financial data"
        })

    # -----------------------------------------
    # TC05 — Current Ratio Check
    # -----------------------------------------
    current_ratio_valid = (
        df["current_ratio"].notna()
        & np.isfinite(df["current_ratio"])
        & (df["current_ratio"] >= 0)
    )

    results.append({
        "test_id": "TC05",
        "test_name": "Current Ratio Check",
        "status": "PASS" if current_ratio_valid.all() else "REVIEW",
        "records_checked": len(df),
        "records_passed": int(current_ratio_valid.sum()),
        "records_failed": int((~current_ratio_valid).sum()),
        "description": "Evaluate short-term liquidity"
    })

    # -----------------------------------------
    # TC06 — Debt Equity Check
    # -----------------------------------------
    debt_equity_valid = (
        df["debt_equity_ratio"].notna()
        & np.isfinite(df["debt_equity_ratio"])
        & (df["debt_equity_ratio"] >= 0)
    )

    results.append({
        "test_id": "TC06",
        "test_name": "Debt Equity Check",
        "status": "PASS" if debt_equity_valid.all() else "REVIEW",
        "records_checked": len(df),
        "records_passed": int(debt_equity_valid.sum()),
        "records_failed": int((~debt_equity_valid).sum()),
        "description": "Evaluate financial leverage"
    })

    return pd.DataFrame(results)


def get_validation_summary(validation_results):
    """Create a simple validation summary."""

    total = len(validation_results)

    passed = (
        validation_results["status"] == "PASS"
    ).sum()

    review = (
        validation_results["status"] == "REVIEW"
    ).sum()

    return {
        "total_tests": int(total),
        "passed": int(passed),
        "review": int(review),
        "overall_status": "PASS" if review == 0 else "REVIEW"
    }
