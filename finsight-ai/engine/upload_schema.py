# ============================================================
# FINSIGHT AI — UPLOAD SCHEMA
# ============================================================

# Required for the core financial calculation engine.
CORE_REQUIRED_COLUMNS = [
    "year",
    "company",
    "revenue",
    "gross_profit",
    "net_income",
    "ebitda",
    "share_holder_equity",
    "cash_flow_from_operating",
    "cash_flow_from_investing",
    "cash_flow_from_financial_activities",
    "current_ratio",
    "debt_equity_ratio"
]


# Required by validation and several downstream
# financial intelligence modules.
ANALYTICS_COLUMNS = [
    "net_profit_margin",
    "roe",
    "roa",
    "roi"
]


# Useful financial statement / contextual fields.
OPTIONAL_COLUMNS = [
    "category",
    "market_capin_b_usd",
    "earning_per_share",
    "free_cash_flow_per_share",
    "return_on_tangible_equity",
    "number_of_employees",
    "inflation_ratein_us"
]


# Fields that can be calculated by FinSight when
# the underlying values are available.
DERIVABLE_COLUMNS = [
    "net_profit_margin",
    "gross_margin_calculated",
    "ebitda_margin_calculated",
    "net_margin_calculated",
    "net_cash_flow"
]


# Complete set of fields expected by the current
# FinSight intelligence pipeline.
ALL_KNOWN_COLUMNS = (
    CORE_REQUIRED_COLUMNS
    + ANALYTICS_COLUMNS
    + OPTIONAL_COLUMNS
)


def get_schema():
    """Return the FinSight upload schema."""

    return {
        "core_required": CORE_REQUIRED_COLUMNS.copy(),
        "analytics": ANALYTICS_COLUMNS.copy(),
        "optional": OPTIONAL_COLUMNS.copy(),
        "derivable": DERIVABLE_COLUMNS.copy(),
        "all_known": ALL_KNOWN_COLUMNS.copy()
    }
