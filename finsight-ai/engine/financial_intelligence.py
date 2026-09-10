
from engine.financial_engine import calculate_financial_metrics
from engine.validation import run_validation
from engine.anomaly import detect_anomalies
from engine.benchmark import build_peer_benchmark
from engine.risk import build_health_risk_scores
from engine.investigation_report import generate_investigation_report
from engine.scenarios import run_scenario
from engine.financial_map import build_financial_map


def run_financial_intelligence(financial_df, company, year):
    """
    Master orchestration engine for FinSight AI.

    Connects:
    - Financial calculations
    - Validation
    - Anomaly detection
    - Peer benchmarking
    - Health & risk
    - AI investigation
    - What-if scenarios
    - Financial intelligence map
    """

    # 1. Financial calculations
    calculated_df = calculate_financial_metrics(
        financial_df
    )

    # 2. Validation
    validation_results = run_validation(
        calculated_df
    )

    # 3. Anomaly detection
    anomaly_results = detect_anomalies(
        calculated_df
    )

    # 4. Peer benchmarking
    benchmark_results = build_peer_benchmark(
        calculated_df,
        year
    )

    # 5. Health & risk
    risk_results = build_health_risk_scores(
        calculated_df,
        year
    )

    # 6. Investigation
    investigation = generate_investigation_report(
        calculated_df,
        company,
        year
    )

    # 7. What-if scenarios
    scenarios = run_scenario(
        calculated_df,
        company,
        year
    )

    # 8. Financial Intelligence Map
    financial_map = build_financial_map(
        calculated_df,
        company,
        year
    )

    return {
        "company": company,
        "year": year,
        "financial_data": calculated_df,
        "validation": validation_results,
        "anomalies": anomaly_results,
        "benchmark": benchmark_results,
        "risk": risk_results,
        "investigation": investigation,
        "scenarios": scenarios,
        "financial_map": financial_map
    }
