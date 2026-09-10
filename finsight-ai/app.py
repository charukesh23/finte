from engine.validation import run_validation

import streamlit as st
import pandas as pd
import altair as alt

from engine.data_loader import (
    load_application_data,
    get_companies,
    get_years
)

from engine.dashboard import (
    get_company_snapshot,
    get_company_trend
)

from engine.financial_engine import calculate_financial_metrics
from engine.risk import build_health_risk_scores
from engine.investigation_report import generate_investigation_report
from engine.financial_map import build_financial_map
from engine.scenarios import compare_scenarios, run_scenario
from engine.anomaly import detect_anomalies
from engine.column_mapper import (
    map_financial_columns,
    derive_financial_columns
)
from engine.upload_validation import validate_uploaded_data
from engine.benchmark import build_peer_benchmark
from engine.ai_investigation import (
    build_ai_investigation_context,
    extract_ai_signals,
    build_ai_investigation_prompt,
    generate_mock_ai_report
)

from engine.llm import generate_ai_response, get_llm_status


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FinSight AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 34px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
    }

    .sub-title {
        font-size: 16px;
        opacity: 0.68;
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 650;
        margin-top: 24px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.25);
    }

    div[data-testid="stMetric"] {
        padding: 14px 16px;
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 10px;
        background: rgba(128, 128, 128, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 13px;
        font-weight: 500;
    }

    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 650;
    }

    .stCaption {
        opacity: 0.68;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    return load_application_data(
        "data/clean_data.csv"
    )


# ============================================================
# SIDEBAR - DATA SOURCE
# ============================================================

with st.sidebar:
    st.title("FinSight AI")

    st.caption(
        "Financial Intelligence & Investigation Agent"
    )

    st.divider()

    st.subheader("Data Source")

    uploaded_file = st.file_uploader(
        "Upload Financial Data",
        type=["csv", "xlsx", "xls"],
        help="Upload a financial CSV or Excel workbook for analysis."
    )

# ============================================================
# DATA SOURCE
# ============================================================

if uploaded_file is not None:
    try:
        file_name = uploaded_file.name.lower()

        if file_name.endswith(".csv"):
            uploaded_df = pd.read_csv(uploaded_file)

        elif file_name.endswith((".xlsx", ".xls")):
            uploaded_df = pd.read_excel(uploaded_file)

        else:
            st.error("Unsupported file format.")
            st.stop()

        df, column_mapping, unmapped_columns = map_financial_columns(
            uploaded_df
        )

        # Derive safe financial metrics from uploaded core fields
        df = derive_financial_columns(df)

        upload_validation = validate_uploaded_data(df)

        if not upload_validation["valid"]:
            st.error(
                "Uploaded financial data could not be validated."
            )

            for error in upload_validation["errors"]:
                st.error(error)

            for warning in upload_validation["warnings"]:
                st.warning(warning)

            st.stop()

        st.sidebar.success(
            f"Uploaded: {uploaded_file.name}"
        )

        if column_mapping:
            st.sidebar.caption(
                f"Mapped {len(column_mapping)} financial columns"
            )

        if unmapped_columns:
            st.sidebar.warning(
                f"{len(unmapped_columns)} column(s) not mapped"
            )

    except Exception as e:
        st.error(f"Unable to read uploaded file: {e}")
        st.stop()

else:
    df = load_data()

companies = get_companies(df)


# ============================================================
# SIDEBAR - ANALYSIS SELECTION
# ============================================================

with st.sidebar:

    st.divider()

    st.subheader("Analysis Selection")

    selected_company = st.selectbox(
        "Company",
        companies,
        index=companies.index("AAPL")
        if "AAPL" in companies
        else 0
    )

    company_years = get_years(
        df,
        selected_company
    )

    selected_year = st.selectbox(
        "Financial Year",
        company_years,
        index=len(company_years) - 1
    )

    st.divider()

    # Currency selector
    selected_currency = st.selectbox(
        "Display Currency",
        ["USD", "INR"],
        index=0
    )

    # Display-only conversion rate
    USD_TO_INR = 83.0

    if selected_currency == "INR":
        st.caption(
            "Display conversion: ₹83 per USD"
        )
    else:
        st.caption(
            "Source currency: USD"
        )

    st.divider()

    st.caption("AI & Data Analyst Hackathon")
    st.caption("FinSight AI v1.0")





# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">FinSight AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="sub-title">Financial Statement Review Agent | {selected_company} | FY {selected_year}</div>',
    unsafe_allow_html=True
)




# ============================================================
# MAIN NAVIGATION
# ============================================================

tab_overview, tab_investigate, tab_benchmark, tab_simulate, tab_report = st.tabs([
    "Overview",
    "Investigate",
    "Benchmark",
    "Simulate",
    "Report"
])

# ============================================================
# ANALYSIS DATA
# ============================================================

snapshot = get_company_snapshot(
    df,
    selected_company,
    selected_year
)

trend = get_company_trend(
    df,
    selected_company
)

# Keep trend analysis aligned with the selected financial year.
# This makes Revenue Trend, Net Income Trend,
# Profitability Analysis, and Recent Performance
# respond to the selected year.
trend = trend[
    trend["year"].astype(int) <= int(selected_year)
].copy()

trend = trend.sort_values("year").reset_index(drop=True)


# ============================================================
# DISPLAY CONVERSION
# ============================================================

def format_money(value):
    """
    Format monetary values according to selected currency.
    Source data is USD millions.
    """

    if selected_currency == "INR":

        # USD million × 83 = INR million
        inr_million = value * USD_TO_INR

        # Display large values in lakh crore
        lakh_crore = inr_million / 1_000_000

        return f"₹{lakh_crore:,.2f} Lakh Cr"

    else:

        usd_billion = value / 1000

        return f"${usd_billion:,.2f}B"


def convert_chart_values(series):
    """
    Convert monetary values for display only.

    Source data:
    USD millions

    Display:
    USD -> USD billions
    INR -> INR lakh crore
    """

    if selected_currency == "INR":
        # USD million -> INR million -> INR lakh crore
        return (series * USD_TO_INR) / 1_000_000

    # USD million -> USD billion
    return series / 1000


# ============================================================
# DISPLAY CONVERSION
# ============================================================

def format_money(value):
    """
    Format monetary values according to selected currency.
    Source data is USD millions.
    """

    if selected_currency == "INR":

        # USD million × 83 = INR million
        inr_million = value * USD_TO_INR

        # Display large values in lakh crore
        lakh_crore = inr_million / 1_000_000

        return f"₹{lakh_crore:,.2f} Lakh Cr"

    else:

        usd_billion = value / 1000

        return f"${usd_billion:,.2f}B"


def convert_chart_values(series):
    """
    Convert monetary values for display only.

    Source data:
    USD millions

    Display:
    USD -> USD billions
    INR -> INR lakh crore
    """

    if selected_currency == "INR":
        # USD million -> INR million -> INR lakh crore
        return (series * USD_TO_INR) / 1_000_000

    # USD million -> USD billion
    return series / 1000


with tab_overview:
    # ============================================================
    # FINANCIAL HEALTH & RISK
    # ============================================================

    risk_df = build_health_risk_scores(
        calculate_financial_metrics(df.copy()),
        selected_year
    )

    selected_risk = risk_df[
        (risk_df["company"] == selected_company) &
        (risk_df["year"] == selected_year)
    ]

    if not selected_risk.empty:

        health_score = float(selected_risk.iloc[0]["health_score"])
        risk_score = float(selected_risk.iloc[0]["risk_score"])

        # Derive health status from the existing health score
        if health_score >= 80:
            health_status = "Excellent"
        elif health_score >= 65:
            health_status = "Healthy"
        elif health_score >= 50:
            health_status = "Moderate"
        elif health_score >= 35:
            health_status = "Watch"
        else:
            health_status = "High Risk"

        st.markdown(
            '<div class="section-title">Financial Health Assessment</div>',
            unsafe_allow_html=True
        )

        health_col1, health_col2, health_col3 = st.columns(3)

        with health_col1:
            st.metric(
                "Financial Health Score",
                f"{health_score:.1f}/100"
            )

        with health_col2:
            st.metric(
                "Risk Score",
                f"{risk_score:.1f}/100"
            )

        with health_col3:
            st.metric(
                "Overall Status",
                health_status
            )

        st.caption(
            "Composite assessment based on profitability, growth, liquidity, leverage and cash flow indicators."
        )


    # ============================================================
    # FINANCIAL OVERVIEW
    # ============================================================

    st.markdown(
        '<div class="section-title">Financial Overview</div>',
        unsafe_allow_html=True
    )


    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Revenue",
            format_money(snapshot["revenue"])
        )

    with col2:
        st.metric(
            "Net Income",
            format_money(snapshot["net_income"])
        )

    with col3:
        st.metric(
            "EBITDA",
            format_money(snapshot["ebitda"])
        )

    with col4:
        st.metric(
            "Net Profit Margin",
            f"{snapshot['net_profit_margin']:.2f}%"
        )


    col5, col6, col7, col8 = st.columns(4)

    with col5:
        st.metric(
            "Gross Profit",
            format_money(snapshot["gross_profit"])
        )

    with col6:
        st.metric(
            "Operating Cash Flow",
            format_money(snapshot["operating_cash_flow"])
        )

    with col7:
        st.metric(
            "Current Ratio",
            f"{snapshot['current_ratio']:.2f}x"
        )

    with col8:
        st.metric(
            "Debt / Equity",
            f"{snapshot['debt_equity_ratio']:.2f}x"
        )



with tab_investigate:
    # ============================================================
    # VALIDATION CENTER
    # ============================================================

    validation_df = run_validation(
        calculate_financial_metrics(df.copy())
    )

    validation_pass = int(
        (validation_df["status"] == "PASS").sum()
    )

    validation_review = int(
        (validation_df["status"] == "REVIEW").sum()
    )

    st.markdown(
        '<div class="section-title"> Validation Center</div>',
        unsafe_allow_html=True
    )

    val_col1, val_col2, val_col3 = st.columns(3)

    with val_col1:
        st.metric(
            "Validation Tests",
            len(validation_df)
        )

    with val_col2:
        st.metric(
            "Passed",
            validation_pass
        )

    with val_col3:
        st.metric(
            "Needs Review",
            validation_review
        )

    for _, test in validation_df.iterrows():

        test_name = test["test_name"]
        status = str(test["status"]).upper()
        records_failed = int(test["records_failed"])

        if status == "PASS":

            st.success(
                f" **{test_name}** — PASS  |  "
                f"Records checked: {int(test['records_checked'])}"
            )

        else:

            max_diff = test["max_difference"]

            if pd.notna(max_diff):
                detail = f"Max difference: {float(max_diff):.2f}"
            else:
                detail = "Review required"

            st.warning(
                f" **{test_name}** — REVIEW  |  "
                f"Failed records: {records_failed}  |  {detail}"
            )

    # ============================================================
    # AI INVESTIGATION
    # ============================================================

    # Detect anomalies first so they can feed the investigation layer
    anomaly_input_df = calculate_financial_metrics(df.copy())
    anomaly_df = detect_anomalies(anomaly_input_df)

    if anomaly_df.empty:
        selected_anomalies = anomaly_df.copy()
    else:
        selected_anomalies = anomaly_df[
            (anomaly_df["company"] == selected_company) &
            (anomaly_df["year"] == selected_year)
        ].copy()

    analysis_df = calculate_financial_metrics(df.copy())

    investigation = generate_investigation_report(
        analysis_df,
        selected_company,
        selected_year
    )

    st.markdown(
        '<div class="section-title"> AI Investigation</div>',
        unsafe_allow_html=True
    )

    if investigation:

        primary_driver = investigation.get(
            "primary_driver",
            "No Material Driver Detected"
        )

        driver_count = investigation.get("driver_count", 0)
        evidence_count = investigation.get("evidence", {}).get("evidence_count", 0)

        # If anomaly exists but root-cause engine has no driver,
        # promote the strongest anomaly into the investigation view.
        if not selected_anomalies.empty:

            first_anomaly = selected_anomalies.iloc[0]

            if driver_count == 0:
                primary_driver = first_anomaly.get(
                    "finding_type",
                    "Financial Anomaly"
                )

                driver_count = len(selected_anomalies)
                evidence_count = len(selected_anomalies)

        if not primary_driver:
            primary_driver = "No Material Driver Detected"

        inv_col1, inv_col2, inv_col3 = st.columns(3)

        with inv_col1:
            st.markdown("**Primary Driver**")
            st.info(primary_driver)

        with inv_col2:
            st.metric(
                "Drivers Detected",
                driver_count
            )

        with inv_col3:
            st.metric(
                "Evidence Points",
                evidence_count
            )

        if not selected_anomalies.empty:

            st.markdown("** Investigation Evidence**")

            for _, finding in selected_anomalies.iterrows():

                severity = str(
                    finding.get("severity", "REVIEW")
                ).upper()

                metric = finding.get(
                    "metric",
                    "Financial Metric"
                )

                change = finding.get(
                    "change",
                    None
                )

                anomaly_type = finding.get(
                    "finding_type",
                    "Financial Anomaly"
                )

                if pd.notna(change):
                    change_text = f"{float(change):+.2f}%"
                else:
                    change_text = "Material movement detected"

                if severity == "HIGH":
                    st.error(
                        f" **{anomaly_type}** — {metric}\n\n"
                        f"Severity: **High** | Change: **{change_text}**"
                    )

                else:
                    st.warning(
                        f" **{anomaly_type}** — {metric}\n\n"
                        f"Severity: **{severity.title()}** | Change: **{change_text}**"
                    )

            st.info(
                "**AI Assessment**\n\n"
                "The detected anomaly has been promoted into the investigation "
                "workflow for further financial review and supporting evidence analysis."
            )

        else:

            st.success(
                " **Routine Review — No Material Driver Detected**\n\n"
                "The selected financial period does not show a significant "
                "root-cause movement based on the current investigation rules."
            )

        # ========================================================
        # GROUNDED AI INVESTIGATION REPORT
        # ========================================================

        # Build the structured AI context from FinSight analytics
        ai_context = build_ai_investigation_context({
            "company": selected_company,
            "year": selected_year,
            "financial_data": analysis_df,
            "validation": None,
            "anomalies": anomaly_df,
            "benchmark": build_peer_benchmark(
                analysis_df,
                selected_year
            ),
            "risk": build_health_risk_scores(
                analysis_df,
                selected_year
            ),
            "investigation": investigation,
            "scenarios": None,
            "financial_map": None
        })

        ai_signals = extract_ai_signals(ai_context)

        # Generate the grounded structured AI report
        ai_report = generate_mock_ai_report(ai_signals)

        # Send the grounded prompt through the LLM interface.
        # Current implementation runs in DEMO mode until a real
        # LLM provider/API key is configured.
        ai_prompt = build_ai_investigation_prompt(ai_signals)

        llm_response = generate_ai_response(
            prompt=ai_prompt,
            context=ai_signals
        )

        llm_status = get_llm_status()

        st.markdown("### AI Financial Assessment")

        st.info(
            "Demo AI mode — this assessment is grounded in "
            "FinSight's deterministic financial analytics. "
            "A real LLM will be connected later."
        )

        st.markdown(
            "**Executive Summary**"
        )
        st.write(
            ai_report["executive_summary"]
        )

        st.markdown(
            "**Key Findings**"
        )

        if ai_report["key_findings"]:
            for finding in ai_report["key_findings"]:
                st.write(f"• {finding}")
        else:
            st.write("No key findings identified.")

        st.markdown(
            "**Root Cause Assessment**"
        )
        st.write(
            ai_report["root_cause_assessment"]
        )

        st.markdown(
            "**Peer Benchmark Observations**"
        )

        benchmark_report = ai_report["peer_benchmark"]

        if benchmark_report:
            st.write(
                f"Peer benchmark status: "
                f"{benchmark_report.get('peer_status', 'Unavailable')}"
            )

            if benchmark_report.get("peer_count") is not None:
                st.write(
                    f"Peers available: "
                    f"{benchmark_report['peer_count']}"
                )

            if benchmark_report.get("revenue_vs_peer_pct") is not None:
                st.write(
                    f"Revenue vs peer average: "
                    f"{float(benchmark_report['revenue_vs_peer_pct']):+.2f}%"
                )

            if benchmark_report.get("net_income_vs_peer_pct") is not None:
                st.write(
                    f"Net income vs peer average: "
                    f"{float(benchmark_report['net_income_vs_peer_pct']):+.2f}%"
                )

            if benchmark_report.get("current_ratio_vs_peer_pct") is not None:
                st.write(
                    f"Current ratio vs peer average: "
                    f"{float(benchmark_report['current_ratio_vs_peer_pct']):+.2f}%"
                )

            if benchmark_report.get("debt_equity_vs_peer_pct") is not None:
                st.write(
                    f"Debt-to-equity vs peer average: "
                    f"{float(benchmark_report['debt_equity_vs_peer_pct']):+.2f}%"
                )

        st.caption(
            ai_report["grounding"]
        )


    # ============================================================
    # ANOMALY DETECTION
    # ============================================================

    anomaly_input_df = calculate_financial_metrics(df.copy())
    anomaly_df = detect_anomalies(anomaly_input_df)

    if anomaly_df.empty:
        selected_anomalies = anomaly_df.copy()
    else:
        selected_anomalies = anomaly_df[
            (anomaly_df["company"] == selected_company) &
            (anomaly_df["year"] == selected_year)
        ].copy()

    st.markdown(
        '<div class="section-title"> Anomaly Detection</div>',
        unsafe_allow_html=True
    )

    if selected_anomalies.empty:

        st.success(
            " **No significant anomalies detected**\n\n"
            "The selected financial period does not trigger any of the "
            "current anomaly detection rules."
        )

    else:

        high_count = len(
            selected_anomalies[
                selected_anomalies["severity"].str.upper() == "HIGH"
            ]
        )

        medium_count = len(
            selected_anomalies[
                selected_anomalies["severity"].str.upper() == "MEDIUM"
            ]
        )

        anomaly_col1, anomaly_col2, anomaly_col3 = st.columns(3)

        with anomaly_col1:
            st.metric(
                "Total Findings",
                len(selected_anomalies)
            )

        with anomaly_col2:
            st.metric(
                "High Severity",
                high_count
            )

        with anomaly_col3:
            st.metric(
                "Medium Severity",
                medium_count
            )

        # Display available anomaly information
        display_columns = [
            col for col in [
                "severity",
                "anomaly_type",
                "metric",
                "message",
                "change"
            ]
            if col in selected_anomalies.columns
        ]

        if display_columns:
            st.dataframe(
                selected_anomalies[display_columns],
                width="stretch",
                hide_index=True
            )
        else:
            st.dataframe(
                selected_anomalies,
                width="stretch",
                hide_index=True
            )


with tab_benchmark:
    # ============================================================
    # PEER BENCHMARK
    # ============================================================

    benchmark_df = build_peer_benchmark(df, selected_year)

    selected_benchmark = benchmark_df[
        benchmark_df["company"] == selected_company
    ].copy()

    st.markdown(
        '<div class="section-title"> Peer Benchmark</div>',
        unsafe_allow_html=True
    )

    if selected_benchmark.empty:

        st.info(
            "No benchmark information is available for the selected company."
        )

    else:

        benchmark_row = selected_benchmark.iloc[0]
        peer_count = int(benchmark_row["peer_count"])

        if peer_count == 0:

            st.info(
                " **No comparable peer group available**\n\n"
                "The selected company does not have enough companies in the "
                "same category for a meaningful peer comparison."
            )

        else:

            st.caption(
                f"Category: {benchmark_row['category']}  |  "
                f"Peer companies: {peer_count}  |  "
                f"Benchmark year: {int(benchmark_row['year'])}"
            )

            # ----------------------------------------------------
            # Benchmark summary metrics
            # Optional metrics such as ROE/ROA are displayed only
            # when they are actually available in the uploaded data.
            # ----------------------------------------------------

            benchmark_cards = [
                ("Revenue vs Peers", "revenue_vs_peer_pct", "%"),
                ("Net Income vs Peers", "net_income_vs_peer_pct", "%"),
                ("Net Margin vs Peers", "net_profit_margin_vs_peer_pct", "%")
            ]

            if "roa_vs_peer_pct" in benchmark_row.index:
                benchmark_cards.append(
                    ("ROA vs Peers", "roa_vs_peer_pct", "%")
                )

            bench_cols = st.columns(len(benchmark_cards))

            for col, (label, key, suffix) in zip(
                bench_cols,
                benchmark_cards
            ):
                with col:
                    value = benchmark_row.get(key)

                    if pd.notna(value):
                        st.metric(
                            label,
                            f"{float(value):+.2f}{suffix}"
                        )
                    else:
                        st.metric(label, "N/A")

            st.markdown("**Company vs Peer Average**")

            benchmark_rows = [
                (
                    "Revenue",
                    "revenue_company",
                    "revenue_peer_avg",
                    ",.2f"
                ),
                (
                    "Net Income",
                    "net_income_company",
                    "net_income_peer_avg",
                    ",.2f"
                ),
                (
                    "Net Profit Margin",
                    "net_profit_margin_company",
                    "net_profit_margin_peer_avg",
                    ".2f%"
                ),
                (
                    "Current Ratio",
                    "current_ratio_company",
                    "current_ratio_peer_avg",
                    ".2fx"
                ),
                (
                    "Debt / Equity",
                    "debt_equity_ratio_company",
                    "debt_equity_ratio_peer_avg",
                    ".2fx"
                )
            ]

            # Add optional profitability-return metrics only when
            # supplied by the uploaded financial dataset.
            if (
                "roe_company" in benchmark_row.index
                and "roe_peer_avg" in benchmark_row.index
            ):
                benchmark_rows.insert(
                    3,
                    (
                        "ROE",
                        "roe_company",
                        "roe_peer_avg",
                        ".2f%"
                    )
                )

            if (
                "roa_company" in benchmark_row.index
                and "roa_peer_avg" in benchmark_row.index
            ):
                insert_position = 4 if any(
                    row[0] == "ROE"
                    for row in benchmark_rows
                ) else 3

                benchmark_rows.insert(
                    insert_position,
                    (
                        "ROA",
                        "roa_company",
                        "roa_peer_avg",
                        ".2f%"
                    )
                )

            metrics = []
            company_values = []
            peer_values = []

            for metric_name, company_key, peer_key, fmt in benchmark_rows:
                metrics.append(metric_name)

                company_value = benchmark_row.get(company_key)
                peer_value = benchmark_row.get(peer_key)

                if pd.notna(company_value):
                    value = float(company_value)

                    if fmt.endswith("%"):
                        company_values.append(f"{value:.2f}%")
                    elif fmt.endswith("x"):
                        company_values.append(f"{value:.2f}x")
                    else:
                        company_values.append(f"{value:,.2f}")
                else:
                    company_values.append("N/A")

                if pd.notna(peer_value):
                    value = float(peer_value)

                    if fmt.endswith("%"):
                        peer_values.append(f"{value:.2f}%")
                    elif fmt.endswith("x"):
                        peer_values.append(f"{value:.2f}x")
                    else:
                        peer_values.append(f"{value:,.2f}")
                else:
                    peer_values.append("N/A")

            benchmark_display = pd.DataFrame({
                "Metric": metrics,
                "Company": company_values,
                "Peer Average": peer_values
            })

            st.dataframe(
                benchmark_display,
                width="stretch",
                hide_index=True
            )

    # ============================================================
    # FINANCIAL INTELLIGENCE MAP
    # ============================================================

    st.markdown(
        '<div class="section-title"> Financial Intelligence Map</div>',
        unsafe_allow_html=True
    )

    map_data = build_financial_map(df, selected_company, selected_year)

    st.caption(
        "AI-powered view of how key financial metrics connect and influence overall performance."
    )

    roe_display = (
        f"{float(snapshot['roe']):.2f}%"
        if snapshot.get("roe") is not None
        else "N/A"
    )

    roa_display = (
        f"{float(snapshot['roa']):.2f}%"
        if snapshot.get("roa") is not None
        else "N/A"
    )

    roi_display = (
        f"{float(snapshot['roi']):.2f}%"
        if snapshot.get("roi") is not None
        else "N/A"
    )

    map_dot = f"""
    digraph G {{
        rankdir=LR;
        bgcolor="transparent";
        graph [pad="0.3", nodesep="0.5", ranksep="0.8"];

        node [
            shape=box,
            style="rounded,filled",
            fontname="Arial",
            fontsize=11,
            margin="0.18,0.12",
            fontcolor="white"
        ];

        edge [
            fontname="Arial",
            fontsize=9,
            color="#AAB4C0",
            fontcolor="#D6DCE3",
            penwidth=1.4
        ];

        revenue [
            label="Revenue\\n${float(snapshot['revenue']):,.0f}M",
            fillcolor="#163A2B"
        ];

        gross [
            label="Gross Profit\\n${float(snapshot['gross_profit']):,.0f}M",
            fillcolor="#173B4D"
        ];

        ebitda [
            label="EBITDA\\n${float(snapshot['ebitda']):,.0f}M",
            fillcolor="#403A17"
        ];

        net_income [
            label="Net Income\\n${float(snapshot['net_income']):,.0f}M",
            fillcolor="#3B1F3F"
        ];

        cashflow [
            label="Operating Cash Flow\\n${float(snapshot['operating_cash_flow']):,.0f}M",
            fillcolor="#173A35"
        ];

        ratios [
            label="Financial Health Metrics\\nNPM: {float(snapshot['net_profit_margin']):.2f}%\\nROE: {roe_display}\\nROA: {roa_display}\\nROI: {roi_display}",
            fillcolor="#25252D"
        ];

        liquidity [
            label="Liquidity & Leverage\\nCurrent Ratio: {float(snapshot['current_ratio']):.2f}x\\nDebt / Equity: {float(snapshot['debt_equity_ratio']):.2f}x",
            fillcolor="#25252D"
        ];

        revenue -> gross [label="profit generation"];
        gross -> ebitda [label="operating efficiency"];
        ebitda -> net_income [label="bottom-line impact"];
        net_income -> cashflow [label="cash conversion"];
        net_income -> ratios [label="performance"];
        liquidity -> net_income [label="financial context"];
    }}
    """

    st.graphviz_chart(map_dot, width="stretch")

    st.info(
        " **AI Insight:** The map connects operating performance, profitability, "
        "cash generation, liquidity and leverage so reviewers can investigate "
        "the financial story rather than looking at isolated numbers."
    )


with tab_simulate:
    # ============================================================
    # WHAT-IF SCENARIO ANALYSIS
    # ============================================================

    st.markdown(
        '<div class="section-title"> What-If Scenario Analysis</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Explore how changes in revenue growth and profitability could affect "
        "the company's financial outcome."
    )

    scenario_col1, scenario_col2 = st.columns(2)

    with scenario_col1:
        revenue_growth_input = st.slider(
            "Revenue Growth (%)",
            min_value=-30.0,
            max_value=50.0,
            value=10.0,
            step=1.0
        )

    with scenario_col2:
        margin_input = st.slider(
            "Target Net Profit Margin (%)",
            min_value=5.0,
            max_value=50.0,
            value=30.0,
            step=1.0
        )

    current_revenue = float(snapshot["revenue"])
    current_net_income = float(snapshot["net_income"])
    current_margin = float(snapshot["net_profit_margin"])

    def format_scenario_money(value):
        if selected_currency == "INR":
            # Source data is USD million.
            # Convert to INR million, then display as lakh crore.
            inr_lakh_crore = (value * USD_TO_INR) / 1_000_000
            return f"₹{inr_lakh_crore:,.2f} Lakh Cr"
        else:
            usd_billion = value / 1000
            return f"${usd_billion:,.2f}B"

    projected_revenue = current_revenue * (1 + revenue_growth_input / 100)

    projected_net_income = projected_revenue * (margin_input / 100)

    income_change = projected_net_income - current_net_income
    income_change_pct = (
        (income_change / current_net_income) * 100
        if current_net_income != 0
        else 0
    )

    st.markdown("**Scenario Impact**")

    scenario_metric1, scenario_metric2, scenario_metric3 = st.columns(3)

    with scenario_metric1:
        st.metric(
            "Projected Revenue",
            format_scenario_money(projected_revenue),
            f"{revenue_growth_input:+.0f}%"
        )

    with scenario_metric2:
        st.metric(
            "Projected Net Income",
            format_scenario_money(projected_net_income),
            f"{income_change_pct:+.2f}%"
        )

    with scenario_metric3:
        st.metric(
            "Projected Net Margin",
            f"{margin_input:.2f}%",
            f"{margin_input - current_margin:+.2f} pp"
        )

    scenario_display = pd.DataFrame({
        "Metric": [
            "Revenue",
            "Net Income",
            "Net Profit Margin"
        ],
        "Current": [
            format_scenario_money(current_revenue),
            format_scenario_money(current_net_income),
            f"{current_margin:.2f}%"
        ],
        "What-If Scenario": [
            format_scenario_money(projected_revenue),
            format_scenario_money(projected_net_income),
            f"{margin_input:.2f}%"
        ]
    })

    st.dataframe(
        scenario_display,
        width="stretch",
        hide_index=True
    )

    st.info(
        " **Scenario Note:** This is a what-if analysis based on the selected "
        "assumptions, not a financial forecast."
    )


with tab_report:
    # ============================================================
    # AI REVIEW REPORT
    # ============================================================

    st.markdown(
        '<div class="section-title"> AI Review Report</div>',
        unsafe_allow_html=True
    )

    report = generate_investigation_report(
        analysis_df,
        selected_company,
        selected_year
    )

    st.caption(
        "Evidence-backed review observations generated from the selected financial period."
    )

    report_col1, report_col2, report_col3 = st.columns(3)

    with report_col1:
        primary_driver_text = report.get(
            "primary_driver",
            "No major driver"
        )

        st.markdown(
            f"""
            <div style="
                background-color: #111827;
                border: 1px solid #374151;
                border-radius: 10px;
                padding: 14px 16px;
                min-height: 82px;
            ">
                <div style="
                    font-size: 14px;
                    color: #9CA3AF;
                    margin-bottom: 8px;
                ">
                    Primary Driver
                </div>
                <div style="
                    font-size: 20px;
                    font-weight: 600;
                    line-height: 1.25;
                    color: #F9FAFB;
                    word-wrap: break-word;
                ">
                    {primary_driver_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with report_col2:
        drivers = report.get("drivers", [])
        st.metric(
            "Drivers Detected",
            len(drivers) if isinstance(drivers, list) else 0
        )

    with report_col3:
        evidence_data = report.get("evidence", {})
        evidence_count = (
            evidence_data.get("evidence_count", 0)
            if isinstance(evidence_data, dict)
            else 0
        )
        st.metric(
            "Evidence Points",
            evidence_count
        )

    st.markdown("**Recommendation**")

    recommendation = report.get(
        "recommendation",
        "No specific recommendation generated for this period."
    )

    st.info(
        f" **Observation:** {recommendation}"
    )

    def format_report_money(value):
        if value is None:
            return "—"

        value = float(value)

        if selected_currency == "INR":
            inr_lakh_crore = (value * USD_TO_INR) / 1_000_000
            return f"₹{inr_lakh_crore:,.2f} Lakh Cr"
        else:
            usd_billion = value / 1000
            return f"${usd_billion:,.2f}B"


    def format_report_value(metric, value):
        if value is None:
            return "—"

        value = float(value)

        if metric in ["Revenue", "Net Income"]:
            return format_report_money(value)

        if metric in ["Gross Margin", "EBITDA Margin"]:
            return f"{value:,.2f}%"

        if metric in ["Current Ratio", "Debt/Equity"]:
            return f"{value:,.2f}x"

        return f"{value:,.2f}"


    evidence_data = report.get("evidence", {})
    evidence_items = (
        evidence_data.get("changes", [])
        if isinstance(evidence_data, dict)
        else []
    )

    if evidence_items:
        st.markdown("**Supporting Evidence**")

        report_evidence = []

        for item in evidence_items:
            metric = item.get("metric", "Financial Metric")
            current_value = item.get("current")
            previous_value = item.get("previous")
            change_value = item.get("change")
            unit = item.get("unit", "")
            evidence_type = item.get("evidence_type", "Financial Analysis")

            if unit == "%":
                change_text = f"{float(change_value):+.2f}%"
            elif unit == "percentage points":
                change_text = f"{float(change_value):+.2f} pp"
            elif unit == "x":
                change_text = f"{float(change_value):+.2f}x"
            else:
                change_text = f"{float(change_value):+.2f}"

            report_evidence.append({
                "Metric": metric,
                "Current": format_report_value(metric, current_value),
                "Previous": format_report_value(metric, previous_value),
                "Change": change_text,
                "Evidence Type": evidence_type
            })

        st.dataframe(
            pd.DataFrame(report_evidence),
            width="stretch",
            hide_index=True
        )
    else:
        st.success(
            "No supporting evidence points were identified for the selected period."
        )

    st.caption(
        " AI-generated review support. Conclusions should be validated against "
        "the underlying financial statements and source documents."
    )

    # ============================================================
    # PERFORMANCE TRENDS
    # ============================================================

    st.markdown(
        '<div class="section-title">Performance Trends</div>',
        unsafe_allow_html=True
    )


    chart_col1, chart_col2 = st.columns(2)


    # ------------------------------------------------------------
    # REVENUE
    # ------------------------------------------------------------

    with chart_col1:

        st.write("### Revenue Trend")

        revenue_data = trend[
            ["year", "revenue"]
        ].copy()

        revenue_data["display_value"] = convert_chart_values(
            revenue_data["revenue"]
        )

        revenue_chart = alt.Chart(
            revenue_data
        ).mark_line(
            point=True
        ).encode(

            x=alt.X(
                "year:O",
                title="Year"
            ),

            y=alt.Y(
                "display_value:Q",
                title=(
                    "INR Lakh Crore"
                    if selected_currency == "INR"
                    else "USD Billion"
                )
            ),

            tooltip=[
                alt.Tooltip(
                    "year:O",
                    title="Year"
                ),
                alt.Tooltip(
                    "display_value:Q",
                    title=(
                        "₹ Lakh Cr"
                        if selected_currency == "INR"
                        else "$ Billion"
                    ),
                    format=",.2f"
                )
            ]
        ).properties(
            height=350
        )

        st.altair_chart(
            revenue_chart,
            width="stretch"
        )


    # ------------------------------------------------------------
    # NET INCOME
    # ------------------------------------------------------------

    with chart_col2:

        st.write("### Net Income Trend")

        income_data = trend[
            ["year", "net_income"]
        ].copy()

        income_data["display_value"] = convert_chart_values(
            income_data["net_income"]
        )

        income_chart = alt.Chart(
            income_data
        ).mark_line(
            point=True
        ).encode(

            x=alt.X(
                "year:O",
                title="Year"
            ),

            y=alt.Y(
                "display_value:Q",
                title=(
                    "INR Lakh Crore"
                    if selected_currency == "INR"
                    else "USD Billion"
                )
            ),

            tooltip=[
                alt.Tooltip(
                    "year:O",
                    title="Year"
                ),
                alt.Tooltip(
                    "display_value:Q",
                    title=(
                        "₹ Lakh Cr"
                        if selected_currency == "INR"
                        else "$ Billion"
                    ),
                    format=",.2f"
                )
            ]
        ).properties(
            height=350
        )

        st.altair_chart(
            income_chart,
            width="stretch"
        )


    # ============================================================
    # PROFITABILITY ANALYSIS
    # ============================================================

    st.markdown(
        '<div class="section-title">Profitability Analysis</div>',
        unsafe_allow_html=True
    )

    margin_data = trend[
        [
            "year",
            "gross_margin",
            "ebitda_margin",
            "net_profit_margin"
        ]
    ].copy()

    margin_long = margin_data.melt(
        id_vars="year",
        value_vars=[
            "gross_margin",
            "ebitda_margin",
            "net_profit_margin"
        ],
        var_name="metric",
        value_name="margin"
    )

    metric_names = {
        "gross_margin": "Gross Margin",
        "ebitda_margin": "EBITDA Margin",
        "net_profit_margin": "Net Profit Margin"
    }

    margin_long["metric"] = (
        margin_long["metric"]
        .map(metric_names)
    )


    margin_chart = alt.Chart(
        margin_long
    ).mark_line(
        point=True
    ).encode(

        x=alt.X(
            "year:O",
            title="Year"
        ),

        y=alt.Y(
            "margin:Q",
            title="Margin (%)"
        ),

        color=alt.Color(
            "metric:N",
            title="Metric"
        ),

        tooltip=[
            alt.Tooltip(
                "year:O",
                title="Year"
            ),
            alt.Tooltip(
                "metric:N",
                title="Metric"
            ),
            alt.Tooltip(
                "margin:Q",
                title="Margin",
                format=".2f"
            )
        ]
    ).properties(
        height=400
    )

    st.altair_chart(
        margin_chart,
        width="stretch"
    )


    # ============================================================
    # RECENT PERFORMANCE
    # ============================================================

    st.markdown(
        '<div class="section-title">Recent Financial Performance</div>',
        unsafe_allow_html=True
    )

    recent = trend.tail(5).copy()

    recent_display = recent[
        [
            "year",
            "revenue",
            "net_income",
            "ebitda",
            "gross_margin",
            "ebitda_margin",
            "net_profit_margin"
        ]
    ].copy()

    # Convert monetary columns for display
    recent_display["revenue"] = convert_chart_values(
        recent_display["revenue"]
    )

    recent_display["net_income"] = convert_chart_values(
        recent_display["net_income"]
    )

    recent_display["ebitda"] = convert_chart_values(
        recent_display["ebitda"]
    )

    recent_display.columns = [
        "Year",
        f"Revenue ({selected_currency})",
        f"Net Income ({selected_currency})",
        f"EBITDA ({selected_currency})",
        "Gross Margin %",
        "EBITDA Margin %",
        "Net Profit Margin %"
    ]

    st.dataframe(
        recent_display,
        width="stretch",
        hide_index=True
    )
