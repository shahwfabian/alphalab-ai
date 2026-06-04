"""AlphaLab AI — Regression Lab"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import inject_css, page_header, info_box
from utils.data_loader import fetch_simple_returns, fetch_returns, parse_uploaded_csv, DEFAULT_START, DEFAULT_END
from utils.statistics import run_ols_regression, interpret_regression
from utils.charts import scatter_regression, residual_plot
from utils.ai_explainer import explain_results

st.set_page_config(page_title="Regression Lab — AlphaLab AI", page_icon="⬡", layout="wide")
inject_css()

page_header("Regression Lab", "Ordinary Least Squares regression with full diagnostics and plain-English interpretation.")

# ── Configuration ─────────────────────────────────────────────────────────────
tab_market, tab_csv = st.tabs(["Market Data", "Upload CSV"])

data_source = "market"
df_up = None

with tab_market:
    c1, c2 = st.columns(2)
    with c1:
        dep_ticker  = st.text_input("Dependent variable (Y)", value="NVDA")
        indep_raw   = st.text_input("Independent variable(s) (X)", value="SPY, QQQ", help="Comma-separated")
    with c2:
        start_date  = st.date_input("Start date", value=pd.to_datetime(DEFAULT_START))
        end_date    = st.date_input("End date",   value=pd.to_datetime(DEFAULT_END))

    c3, c4 = st.columns(2)
    with c3:
        return_type = st.selectbox("Return type", ["Simple (Arithmetic)", "Log"])
    with c4:
        add_const   = st.checkbox("Include intercept", value=True)

with tab_csv:
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        df_up = parse_uploaded_csv(uploaded)
        if not df_up.empty:
            st.success(f"{len(df_up):,} rows loaded")
            numeric_cols  = df_up.select_dtypes(include=[np.number]).columns.tolist()
            dep_col       = st.selectbox("Dependent variable (Y)", numeric_cols)
            indep_col     = st.multiselect("Independent variable(s) (X)", [c for c in numeric_cols if c != dep_col])
            add_const_csv = st.checkbox("Include intercept", value=True, key="csv_const")
            data_source   = "csv"

run_btn = st.button("Run Regression", type="primary")

# ── Run ───────────────────────────────────────────────────────────────────────
if run_btn:
    api_key = st.session_state.get("openai_api_key", "")

    if data_source == "csv" and df_up is not None and not df_up.empty:
        y         = df_up[dep_col]
        X         = df_up[indep_col] if indep_col else pd.DataFrame()
        const_flag= add_const_csv
        y_label   = dep_col
        x_labels  = list(X.columns)
        all_tickers = [y_label] + x_labels
        start_str = end_str = "CSV"
    else:
        indep_tickers = [t.strip().upper() for t in indep_raw.split(",") if t.strip()]
        all_tickers   = [dep_ticker.upper()] + indep_tickers
        start_str, end_str = str(start_date), str(end_date)

        with st.spinner("Downloading data..."):
            rets = fetch_simple_returns(all_tickers, start_str, end_str) if return_type.startswith("Simple") \
                   else fetch_returns(all_tickers, start_str, end_str)

        if rets.empty:
            st.error("Could not download data. Check ticker symbols.")
            st.stop()

        valid_indep = [t for t in indep_tickers if t in rets.columns]
        if not valid_indep or dep_ticker.upper() not in rets.columns:
            st.error("One or more tickers could not be loaded.")
            st.stop()

        y, X        = rets[dep_ticker.upper()], rets[valid_indep]
        const_flag  = add_const
        y_label     = dep_ticker.upper()
        x_labels    = valid_indep

    if X.empty:
        st.error("No independent variables available.")
        st.stop()

    with st.spinner("Running OLS..."):
        results = run_ols_regression(y, X, add_constant=const_flag)

    st.session_state["last_regression_results"] = {
        "results": results, "y_label": y_label, "x_labels": x_labels,
        "tickers": all_tickers, "start": start_str, "end": end_str,
    }

# ── Display results ───────────────────────────────────────────────────────────
if st.session_state.get("last_regression_results"):
    res_store = st.session_state["last_regression_results"]
    results   = res_store["results"]
    y_label   = res_store["y_label"]
    x_labels  = res_store["x_labels"]

    st.divider()

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("R²",           f"{results['r_squared']:.4f}")
    m2.metric("Adj. R²",      f"{results['adj_r_squared']:.4f}")
    m3.metric("F-statistic",  f"{results['f_statistic']:.2f}")
    m4.metric("F p-value",    f"{results['f_pvalue']:.4f}")
    m5.metric("Observations", str(results["n_obs"]))

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Coefficients", "Diagnostics", "Interpretation"])

    with tab1:
        st.dataframe(results["coef_df"].round(6), use_container_width=True)
        st.markdown(f"""
        <p style="font-size:0.75rem; color:#444; margin-top:0.5rem;">
        AIC {results['aic']:.1f} &nbsp;·&nbsp; BIC {results['bic']:.1f} &nbsp;·&nbsp; Durbin-Watson {results['dw_statistic']:.3f}
        </p>
        """, unsafe_allow_html=True)

    with tab2:
        if len(x_labels) == 1:
            coefs     = results["coef_df"]["Coefficient"]
            slope     = float(coefs.iloc[-1])
            intercept = float(coefs.get("const", 0))
            fig_sc    = scatter_regression(results["X"].iloc[:, -1], results["y"], x_labels[0], y_label, slope, intercept)
            st.plotly_chart(fig_sc, use_container_width=True)
        fig_res = residual_plot(results["fitted"], results["residuals"])
        st.plotly_chart(fig_res, use_container_width=True)

    with tab3:
        st.markdown(interpret_regression(results))
        with st.expander("AI explanation"):
            if st.button("Generate", key="reg_ai"):
                ctx = f"OLS: {y_label} ~ {' + '.join(x_labels)}\nR²={results['r_squared']:.4f}, F p={results['f_pvalue']:.4f}, N={results['n_obs']}\n{results['coef_df'].to_string()}"
                with st.spinner("Generating..."):
                    st.markdown(explain_results(ctx, st.session_state.get("openai_api_key") or None))
        with st.expander("Full statsmodels summary"):
            st.text(str(results["summary"]))

    info_box("OLS assumes linearity, homoscedasticity, normality of errors, no multicollinearity, and independence. Always validate with diagnostics.", "warning")
