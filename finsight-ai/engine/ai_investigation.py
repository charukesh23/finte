
import json


def build_ai_investigation_context(intelligence_result):
    """
    Convert FinSight financial intelligence output
    into structured context for AI investigation.
    """

    return {
        "company": intelligence_result.get("company"),
        "year": intelligence_result.get("year"),
        "financial_data": intelligence_result.get("financial_data"),
        "validation": intelligence_result.get("validation"),
        "anomalies": intelligence_result.get("anomalies"),
        "benchmark": intelligence_result.get("benchmark"),
        "risk": intelligence_result.get("risk"),
        "investigation": intelligence_result.get("investigation"),
        "scenarios": intelligence_result.get("scenarios"),
        "financial_map": intelligence_result.get("financial_map"),
    }


def extract_ai_signals(context):
    """
    Extract decision-relevant signals from FinSight analytics.
    """

    signals = {
        "company": context["company"],
        "year": context["year"],
        "risk": {},
        "investigation": {},
        "anomalies": [],
        "benchmark": {}
    }

    risk_df = context["risk"]

    if risk_df is not None and not risk_df.empty:
        risk_row = risk_df[
            risk_df["company"] == context["company"]
        ]

        if not risk_row.empty:
            row = risk_row.iloc[0]

            signals["risk"] = {
                "health_score": float(row["health_score"]),
                "risk_score": float(row["risk_score"]),
                "classification": row["health_classification"]
            }

    investigation = context["investigation"] or {}

    evidence = investigation.get("evidence", {}) or {}

    signals["investigation"] = {
        "assessment": investigation.get("assessment"),
        "primary_driver": investigation.get("primary_driver"),
        "evidence_count": evidence.get("evidence_count", 0),
        "evidence": evidence,
        "investigation_chain": investigation.get(
            "investigation_chain", []
        )
    }

    anomalies = context["anomalies"]

    if anomalies is not None and not anomalies.empty:
        company_anomalies = anomalies[
            anomalies["company"] == context["company"]
        ]

        columns = [
            "year",
            "finding_type",
            "severity",
            "title",
            "metric",
            "change"
        ]

        available_columns = [
            col for col in columns
            if col in company_anomalies.columns
        ]

        signals["anomalies"] = company_anomalies[
            available_columns
        ].to_dict("records")

    benchmark = context["benchmark"]

    if benchmark is not None and not benchmark.empty:
        company_benchmark = benchmark[
            benchmark["company"] == context["company"]
        ]

        if not company_benchmark.empty:
            b = company_benchmark.iloc[0]

            signals["benchmark"] = {
                "peer_count": int(b["peer_count"]),
                "peer_status": b["peer_status"],
                "revenue_vs_peer_pct": b.get(
                    "revenue_vs_peer_pct"
                ),
                "net_income_vs_peer_pct": b.get(
                    "net_income_vs_peer_pct"
                ),
                "current_ratio_vs_peer_pct": b.get(
                    "current_ratio_vs_peer_pct"
                ),
                "debt_equity_vs_peer_pct": b.get(
                    "debt_equity_ratio_vs_peer_pct"
                )
            }

    return signals


def build_ai_investigation_prompt(signals):
    """
    Build a grounded prompt for the future LLM.
    """

    return f"""
You are the Financial Investigation Agent for FinSight AI.

Analyze {signals["company"]} for {signals["year"]} using ONLY
the structured evidence provided.

Rules:
- Do not invent financial values or causes.
- Do not recalculate financial metrics.
- Distinguish YoY changes from peer-relative differences.
- If evidence does not establish a root cause, say so.
- Treat anomalies as signals requiring review, not proof of wrongdoing.
- Mention unavailable data when relevant.
- Provide evidence-based recommendations.

RISK:
{json.dumps(signals["risk"], default=str, indent=2)}

INVESTIGATION:
{json.dumps(signals["investigation"], default=str, indent=2)}

ANOMALIES:
{json.dumps(signals["anomalies"], default=str, indent=2)}

PEER BENCHMARK:
{json.dumps(signals["benchmark"], default=str, indent=2)}

Return:
1. Executive Summary
2. Financial Health
3. Key Findings
4. Anomalies Requiring Review
5. Peer Benchmark Observations
6. Root Cause Assessment
7. Recommended Review Actions
""".strip()


def generate_mock_ai_report(signals):
    """
    Temporary AI report used until a real LLM API is connected.
    """

    risk = signals["risk"]
    investigation = signals["investigation"]
    benchmark = signals["benchmark"]

    return {
        "company": signals["company"],
        "year": signals["year"],
        "executive_summary": (
            f'{signals["company"]} is classified as '
            f'{risk.get("classification", "Unavailable")} '
            f'with a health score of '
            f'{risk.get("health_score", "Unavailable")} '
            f'and a risk score of '
            f'{risk.get("risk_score", "Unavailable")}.'
        ),
        "key_findings": investigation.get(
            "investigation_chain", []
        ),
        "root_cause_assessment": investigation.get(
            "assessment", "Unavailable"
        ),
        "primary_driver": investigation.get(
            "primary_driver", "Unavailable"
        ),
        "evidence_count": investigation.get(
            "evidence", {}
        ).get("evidence_count", 0),
        "anomalies_requiring_review": signals.get(
            "anomalies", []
        ),
        "peer_benchmark": benchmark,
        "recommended_review_actions": [
            (
                "Review the identified financial signals and "
                "supporting evidence before drawing conclusions."
            ),
            (
                "Investigate anomalies as review signals rather "
                "than treating them as confirmed causes."
            ),
            (
                "Consider peer-relative performance alongside "
                "year-over-year changes."
            )
        ],
        "grounding": (
            "All observations are based on FinSight-generated "
            "financial analytics and evidence."
        )
    }
