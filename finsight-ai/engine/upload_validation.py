
import pandas as pd

from engine.upload_schema import (
    CORE_REQUIRED_COLUMNS,
    ANALYTICS_COLUMNS
)


def validate_uploaded_data(df):
    """
    Validate a normalized financial dataset before analysis.

    Returns:
        {
            "valid": bool,
            "errors": list[str],
            "warnings": list[str],
            "stats": dict
        }
    """

    errors = []
    warnings = []

    # ---------------------------------------------------------
    # 1. Empty dataset
    # ---------------------------------------------------------
    if df is None or df.empty:
        return {
            "valid": False,
            "errors": ["Uploaded dataset is empty."],
            "warnings": [],
            "stats": {
                "rows": 0,
                "columns": 0
            }
        }

    # ---------------------------------------------------------
    # 2. Missing core fields
    # ---------------------------------------------------------
    missing_core = [
        col for col in CORE_REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_core:
        errors.append(
            "Missing required financial fields: "
            + ", ".join(missing_core)
        )

    # ---------------------------------------------------------
    # 3. Missing analytics fields
    # ---------------------------------------------------------
    missing_analytics = [
        col for col in ANALYTICS_COLUMNS
        if col not in df.columns
    ]

    if missing_analytics:
        warnings.append(
            "Optional analytics fields not provided: "
            + ", ".join(missing_analytics)
        )

    # ---------------------------------------------------------
    # 4. Duplicate company/year combinations
    # ---------------------------------------------------------
    if "company" in df.columns and "year" in df.columns:

        duplicate_count = df.duplicated(
            subset=["company", "year"]
        ).sum()

        if duplicate_count > 0:
            errors.append(
                f"Found {duplicate_count} duplicate "
                "company/year record(s)."
            )

    # ---------------------------------------------------------
    # 5. Numeric validation
    # ---------------------------------------------------------
    numeric_columns = [
        col for col in CORE_REQUIRED_COLUMNS
        if col not in ["company", "year"]
        and col in df.columns
    ]

    non_numeric = []

    for col in numeric_columns:
        converted = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        invalid_count = (
            df[col].notna() &
            converted.isna()
        ).sum()

        if invalid_count > 0:
            non_numeric.append(
                f"{col} ({invalid_count})"
            )

    if non_numeric:
        errors.append(
            "Non-numeric financial values found: "
            + ", ".join(non_numeric)
        )

    # ---------------------------------------------------------
    # 6. Infinite values
    # ---------------------------------------------------------
    numeric_df = df.select_dtypes(include="number")

    if not numeric_df.empty:
        infinite_count = (
            numeric_df.isin([float("inf"), float("-inf")])
            .sum()
            .sum()
        )

        if infinite_count > 0:
            errors.append(
                f"Found {infinite_count} infinite numeric value(s)."
            )

    # ---------------------------------------------------------
    # 7. Invalid year
    # ---------------------------------------------------------
    if "year" in df.columns:

        years = pd.to_numeric(
            df["year"],
            errors="coerce"
        )

        invalid_years = years.isna().sum()

        if invalid_years > 0:
            errors.append(
                f"Found {invalid_years} invalid year value(s)."
            )

    # ---------------------------------------------------------
    # 8. Revenue sanity check
    # ---------------------------------------------------------
    if "revenue" in df.columns:

        revenue = pd.to_numeric(
            df["revenue"],
            errors="coerce"
        )

        non_positive = (revenue <= 0).sum()

        if non_positive > 0:
            warnings.append(
                f"Found {non_positive} record(s) "
                "with non-positive revenue."
            )

    # ---------------------------------------------------------
    # 9. Statistics
    # ---------------------------------------------------------
    stats = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_core_fields": missing_core,
        "missing_analytics_fields": missing_analytics
    }

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": stats
    }


def get_upload_quality_summary(validation_result):
    """
    Create a compact human-readable summary.
    """

    if validation_result["valid"]:
        status = "VALID"
    else:
        status = "INVALID"

    return {
        "status": status,
        "errors": len(validation_result["errors"]),
        "warnings": len(validation_result["warnings"]),
        "rows": validation_result["stats"]["rows"],
        "columns": validation_result["stats"]["columns"]
    }
