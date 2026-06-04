"""
AlphaLab AI — Regression Lab
OLS regression with full diagnostics, visualization, and interpretation.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import (
    fetch_returns, fetch_simple_returns, parse_uploaded_csv,
    DEFAULT_START, DEFAULT_END,
)
from utils.statistics import run_ols_regression, interpret_regression
from utils.charts import scatter_regression, residual_plot, price_chart, cumulative_return_chart
from utils.ai_explainer import explain_results

st.set_page_config(page_title="Regression Lab — AlphaLab AI", page_icon="📈", layout="wide")

st.markdown("""
<style>
.stApp{background:#0A0E1A}
[data-testid="stSidebar"]{background:#070B16!important;border-right:1px solid #1E2D4A}
.stButton>button{background:linear-gradient(135deg,#00D4FF18,#00D4FF0A);border:1px solid #00D4FF;color:#00D4FF;font-weight:600;border-radius:6px}
.stTextInput>div>div>input,.stSelectbox>div>div,.stMultiSelect>div>div{background:#0F1628!important;border:1px solid #1E2D4A!important;color:#E8F4FD!important}
[data-testid="metric-container"]{background:#0F1628!important;border:1px solid #1E2D4A!important;border-radius:8px!important;padding:16px!important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#00D4FF!important;font-family:JetBrains Mono,monospace!important}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='padding:30px 0 10px 0;'>
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;'>MODULE 02</div>
    <div style='font-size:32px;font-weight:700;color:#00D4FF;font-family:JetBrains Mono,monospace;margin-top:6px;'>📈 Regression Lab</div>
    <div style='color:#6B8CAE;font-size:14px;margin-top:8px;'>Fit OLS regression models on market data or uploaded CSV. Full diagnostics, visualizations, and interpretation.</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── Configuration ────────────────────────────────────────────────────────────

col_cfg, col_run = st.columns([3, 1])

with col_cfg:
    tabs = st.tabs(["Market Data", "Upload CSV"])

    with tabs[0]:
        c1, c2 = st.columns(2)
        with c1:
            dep_ticker = st.text_input("Dependent Variable (Y)", value="NVDA", key="reg_y")
        with c2:
            indep_raw = st.text_input("Independent Variable(s) (X) — comma-separated", value="SPY, QQQ", key="reg_x")

        c3, c4 = st.columns(2)
        with c3:
            start_date = st.date_input("Start Date", value=pd.to_datetime(DEFAULT_START), key="reg_start")
        with c4:
            end_date   = st.date_input("End Date",   value=pd.to_datetime(DEFAULT_END),   key="reg_end")

        return_type = st.selectbox("Return Type", ["Simple (Arithmetic)", "Log"], key="reg_ret_type")
        add_const   = st.checkbox("Include Intercept (Constant)", value=True, key="reg_const")
        data_source = "market"

    with tabs[1]:
        uploaded = st.file_uploader("Upload CSV", type=["csv"], key="reg_csv")
        if uploaded:
            df_up = parse_uploaded_csv(uploaded)
            if not df_up.empty:
                st.success(f"Loaded {len(df_up)} rows × {len(df_up.columns)} columns")
                numeric_cols = df_up.select_dtypes(include=[np.number]).columns.tolist()
                dep_col  = st.selectbox("Dependent Variable (Y)",    numeric_cols, key="reg_y_csv")
                indep_col = st.multiselect("Independent Variable(s) (X)", [c for c in numeric_cols if c != dep_col], key="reg_x_csv")
                add_const_csv = st.checkbox("Include Intercept", value=True, key="reg_const_csv")
                data_source = "csv"

with col_run:
    st.markdown("<br><br>", unsafe_allow_html=True)
    run_btn = st.button("▶ Run Regression", use_container_width=True)

# ─── Execution ────────────────────────────────────────────────────────────────

if run_btn:
    api_key = st.session_state.get("openai_api_key", "")

    if data_source == "market" or "df_up" not in dir():
        indep_tickers = [t.strip().upper() for t in indep_raw.split(",") if t.strip()]
        all_tickers   = [dep_ticker.upper()] + indep_tickers
        start_str     = str(start_date)
        end_str       = str(end_date)

        with st.spinner(f"Downloading {', '.join(all_tickers)} returns..."):
            if return_type.startswith("Simple"):
                returns = fetch_simple_returns(all_tickers, start_str, end_str)
            else:
                returns = fetch_returns(all_tickers, start_str, end_str)

        if returns.empty:
            st.error("Could not download data. Check ticker symbols and date range.")
            st.stop()

        y  = returns[dep_ticker.upper()]
        X  = returns[[t for t in indep_tickers if t in returns.columns]]
        const_flag = add_const
        y_label    = dep_ticker.upper()
        x_labels   = list(X.columns)

    else:
        y  = df_up[dep_col]
        X  = df_up[indep_col] if indep_col else df_up.drop(columns=[dep_col]).select_dtypes(include=[np.number])
        const_flag = add_const_csv
        y_label    = dep_col
        x_labels   = list(X.columns)
        start_str  = end_str = "CSV data"
        returns    = pd.concat([y, X], axis=1)
        indep_tickers = x_labels
        all_tickers   = [y_label] + x_labels

    if X.empty or y.empty:
        st.error("No valid data for the selected variables.")
        st.stop()

    with st.spinner("Running OLS regression..."):
        results = run_ols_regression(y, X, add_constant=const_flag)

    st.session_state["last_regression_results"] = {
        "results": results,
        "y_label": y_label,
        "x_labels": x_labels,
        "tickers": all_tickers,
        "start": start_str,
        "end": end_str,
    }

# ─── Results Display ──────────────────────────────────────────────────────────

if st.session_state.get("last_regression_results"):
    res_store = st.session_state["last_regression_results"]
    results   = res_store["results"]
    y_label   = res_store["y_label"]
    x_labels  = res_store["x_labels"]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:JetBrains Mono,monospace;font-size:12px;color:#6B8CAE;letter-spacing:3px;margin-bottom:18px;'>
    REGRESSION RESULTS
    </div>
    """, unsafe_allow_html=True)

    # Key metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("R²",          f"{results['r_squared']:.4f}")
    m2.metric("Adj. R²",     f"{results['adj_r_squared']:.4f}")
    m3.metric("F-Statistic", f"{results['f_statistic']:.2f}")
    m4.metric("F p-value",   f"{results['f_pvalue']:.4f}")
    m5.metric("Observations",f"{results['n_obs']}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_coef, col_viz = st.columns([2, 3])

    with col_coef:
        st.markdown("**Coefficient Table**")
        coef_df = results["coef_df"].copy()
        coef_df = coef_df.round(6)

        def style_pval(val):
            if val < 0.01:  return "color: #00FFD4; font-weight:700"
            if val < 0.05:  return "color: #00D4FF"
            if val < 0.10:  return "color: #FFD700"
            return "color: #FF4B6E"

        st.dataframe(
            coef_df.style.applymap(style_pval, subset=["P-Value"])
                         .format("{:.6f}"),
            use_container_width=True, height=250,
        )
        st.markdown("<small style='color:#6B8CAE;'>Green=p<0.01 · Blue=p<0.05 · Gold=p<0.10 · Red=p≥0.10</small>", unsafe_allow_html=True)

        # AIC / BIC / DW
        st.markdown(f"""
        <div style='background:#0F1628;border:1px solid #1E2D4A;border-radius:6px;padding:12px;margin-top:12px;font-size:12px;color:#6B8CAE;'>
        AIC: <span style='color:#E8F4FD'>{results['aic']:.2f}</span> &nbsp;|&nbsp;
        BIC: <span style='color:#E8F4FD'>{results['bic']:.2f}</span> &nbsp;|&nbsp;
        Durbin-Watson: <span style='color:#E8F4FD'>{results['dw_statistic']:.4f}</span>
        </div>
        """, unsafe_allow_html=True)

    with col_viz:
        if len(x_labels) == 1:
            x_col = results["X"].iloc[:, -1]
            y_col = results["y"]
            coefs = results["coef_df"]["Coefficient"]
            slope     = float(coefs.iloc[-1])
            intercept = float(coefs.get("const", 0))
            fig_scatter = scatter_regression(x_col, y_col, x_labels[0], y_label, slope, intercept)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Scatter plot available for simple regression (one predictor). Showing residuals only.")

    # Residual diagnostics
    st.markdown("<br>", unsafe_allow_html=True)
    fig_resid = residual_plot(results["fitted"], results["residuals"])
    st.plotly_chart(fig_resid, use_container_width=True)

    # Interpretation
    st.markdown("---")
    st.markdown("**Plain-English Interpretation**")
    st.markdown(interpret_regression(results))

    # AI explanation
    with st.expander("🤖 Ask AI to Explain These Results"):
        if st.button("Generate AI Explanation", key="reg_ai"):
            context = f"""
OLS Regression: {y_label} ~ {' + '.join(x_labels)}
R² = {results['r_squared']:.4f}, Adjusted R² = {results['adj_r_squared']:.4f}
F-statistic = {results['f_statistic']:.4f}, p-value = {results['f_pvalue']:.4f}
N = {results['n_obs']}
Coefficients:
{results['coef_df'].to_string()}
"""
            api_key = st.session_state.get("openai_api_key", "")
            with st.spinner("Generating AI explanation..."):
                explanation = explain_results(context, api_key or None)
            st.markdown(explanation)

    # Full statsmodels summary
    with st.expander("Full OLS Summary (statsmodels)"):
        st.text(str(results["summary"]))

    # Export
    st.markdown("---")
    if st.button("Save Results to Report", key="reg_save_report"):
        st.session_state["report_regression"] = res_store
        st.success("Results saved. Navigate to Research Reports to export.")

    st.markdown("""
    <div style='background:rgba(255,215,0,0.04);border:1px solid #FFD70033;border-radius:6px;padding:12px 16px;color:#FFD70099;font-size:11px;margin-top:16px;'>
    ⚠ OLS assumptions: linearity, homoscedasticity, normality of errors, no perfect multicollinearity, independence of observations.
    Always validate results with residual diagnostics before drawing conclusions.
    </div>
    """, unsafe_allow_html=True)
