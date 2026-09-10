
from engine.root_cause import analyze_root_cause
from engine.evidence import build_evidence


def generate_investigation_report(
    financial_df,
    company,
    year
):
    """
    Combine root-cause analysis and supporting evidence
    into one investigation report.
    """

    root_cause_df = analyze_root_cause(financial_df)

    match = root_cause_df[
        (root_cause_df["company"] == company) &
        (root_cause_df["year"] == year)
    ]

    if match.empty:
        # A valid financial dataset may not contain enough
        # year-over-year movement to produce a root-cause finding.
        # This should not crash the application.

        try:
            evidence = build_evidence(
                financial_df,
                company,
                year
            )
        except Exception:
            evidence = {
                "company": company,
                "year": int(year),
                "current": {},
                "previous": {},
                "changes": [],
                "evidence_count": 0
            }

        return {
            "company": company,
            "year": int(year),
            "assessment": (
                "No major financial driver detected under "
                "the current analytical thresholds."
            ),
            "primary_driver": "No major driver detected",
            "drivers": [],
            "investigation_chain": [],
            "evidence": evidence,
            "recommendation": (
                "No major financial driver was automatically "
                "detected. Perform a broader review of the "
                "financial statements."
            )
        }

    root_cause = match.iloc[0]

    evidence = build_evidence(
        financial_df,
        company,
        year
    )

    drivers = root_cause["drivers"]

    if drivers:

        primary_driver = drivers[0]["driver"]

        recommendation = (
            f"Investigate {primary_driver.lower()} "
            f"and review the underlying financial components "
            f"driving the change."
        )

    else:

        primary_driver = "No major driver detected"

        recommendation = (
            "No major financial driver was automatically detected. "
            "Perform a broader review of the financial statements."
        )

    report = {
        "company": company,
        "year": int(year),

        "assessment": root_cause["assessment"],

        "primary_driver": primary_driver,

        "drivers": drivers,

        "investigation_chain": root_cause[
            "investigation_chain"
        ],

        "evidence": evidence,

        "recommendation": recommendation
    }

    return report
