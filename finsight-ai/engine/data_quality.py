import pandas as pd
import numpy as np


# Core fields required for FinSight financial analysis.
REQUIRED_COLUMNS = [
    "year",
    "company",
    "revenue",
    "gross_profit",
    "net_income",
    "ebitda",
    "share_holder_equity",
    "cash_flow_from_operating",
    "current_ratio",
    "debt_equity_ratio"
]


# Additional fields required by the existing
# validation and analytics modules.
VALIDATION_COLUMNS = [
    "net_profit_margin",
    "roe"
]


def validate_uploaded_data(df):
    """
    Validate the structure and basic data quality of an
    uploaded financial dataset.

    Returns:
        dict containing validation status, errors,
        warnings and basic dataset information.
    """

    errors = []
    warnings = []

    # --------------------------------------------------------
    # Empty dataset
    # --------------------------------------------------------

    if df is None or df.empty:
        errors.append("The uploaded file contains no financial records.")

        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "row_count": 0,
            "column_count": 0,
            "missing_required_columns": REQUIRED_COLUMNS
        }

    df = df.copy()

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    missing_required = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_required:
        errors.append(
            "Missing required financial columns: "
            + ", ".join(missing_required)
        )

    # --------------------------------------------------------
    # Validation-specific columns
    # --------------------------------------------------------

    missing_validation = [
        column
        for column in VALIDATION_COLUMNS
        if column not in df.columns
    ]

    if missing_validation:
        warnings.append(
            "Some existing validation tests require additional "
            "columns: "
            + ", ".join(missing_validation)
        )

    # --------------------------------------------------------
    # Duplicate company-year records
    # --------------------------------------------------------

    if "company" in df.columns and "year" in df.columns:

        duplicates = df.duplicated(
            subset=["company", "year"],
            keep=False
        )

        duplicate_count = int(duplicates.sum())

        if duplicate_count > 0:
            errors.append(
                f"Duplicate company-year records detected: "
                f"{duplicate_count}"
            )

    # --------------------------------------------------------
    # Numeric financial fields
    # --------------------------------------------------------

    numeric_fields = [
        "year",
        "revenue",
        "gross_profit",
        "net_income",
        "ebitda",
        "share_holder_equity",
        "cash_flow_from_operating",
        "current_ratio",
        "debt_equity_ratio"
    ]

    for column in numeric_fields:

        if column not in df.columns:
            continue

        numeric_values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        invalid_values = numeric_values.isna()

        if invalid_values.any():

            errors.append(
                f"Column '{column}' contains "
                f"{int(invalid_values.sum())} "
                f"non-numeric or missing value(s)."
            )

    # --------------------------------------------------------
    # Infinite values
    # --------------------------------------------------------

    numeric_df = df.select_dtypes(include=np.number)

    if not numeric_df.empty:

        infinite_count = int(
            np.isinf(numeric_df.to_numpy()).sum()
        )

        if infinite_count > 0:
            errors.append(
                f"Dataset contains {infinite_count} "
                f"infinite numeric value(s)."
            )

    # --------------------------------------------------------
    # Revenue quality
    # --------------------------------------------------------

    if "revenue" in df.columns:

        revenue = pd.to_numeric(
            df["revenue"],
            errors="coerce"
        )

        if (revenue <= 0).any():

            warnings.append(
                f"{int((revenue <= 0).sum())} record(s) "
                "have zero or negative revenue."
            )

    # --------------------------------------------------------
    # Year quality
    # --------------------------------------------------------

    if "year" in df.columns:

        years = pd.to_numeric(
            df["year"],
            errors="coerce"
        )

        invalid_years = (
            years.isna()
            | (years < 1900)
            | (years > 2100)
        )

        if invalid_years.any():

            errors.append(
                f"{int(invalid_years.sum())} record(s) "
                "contain invalid financial year values."
            )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_required_columns": missing_required,
        "missing_validation_columns": missing_validation
    }
