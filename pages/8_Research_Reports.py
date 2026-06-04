"""AlphaLab AI — Research Reports"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import inject_css, page_header, info_box
from utils.data_loader import fetch_simple_returns, fetch_prices, DEFAULT_START, DEFAULT_END, annualized_return, annualized_volatility
from utils.statistics import run_ols_regression, interpret_regression, return_distribution_stats, compute_correlation_matrix
from utils.portfolio import optimize_max_sharpe, equal_weight_portfolio
from utils.charts import scatter_regression, correlation_heatmap, returns_histogram, efficient_frontier_chart, portfolio_weights_bar
from utils.report_generator import build_report

st.set_page_config(page_title="Research Reports — AlphaLab AI", page_icon="⬡", layout="wide")
inject_css()

page_header("Research Reports", "Generate a professional research report and export it as HTML.")

report_type = st.selectbox("Report type", [
    "Regression Analysis",
    "Portfolio Optimization",
    "Correlation Analysis",
    "Return Distribution",
    "Custom",
])

st.markdown("<br>", unsafe_allow_html=True)

# ── REGRESSION ────────────────────────────────────────────────────────────────
if report_type == "Regression Analysis":
    c1, c2 = st.columns(2)
    with c1:
        dep     = st.text_input("Dependent (Y)", value="NVDA")
        indep   = st.text_input("Independent(s) (X)", value="SPY, QQQ")
    with c2:
        start   = st.date_input("Start", value=pd.to_datetime(DEFAULT_START))
        end     = st.date_input("End",   value=pd.to_datetime(DEFAULT_END))
    rq = st.text_area("Research question", value="Does QQQ explain NVDA returns better than SPY?", height=70)

    if st.button("Generate Report", type="primary"):
        tickers = [dep.upper()] + [t.strip().upper() for t in indep.split(",") if t.strip()]
        with st.spinner("Fetching data and running regression..."):
            rets = fetch_simple_returns(tickers, str(start), str(end))
        valid_x = [t for t in tickers[1:] if t in rets.columns]
        if not valid_x or dep.upper() not in rets.columns:
            st.error("Invalid tickers.")
            st.stop()
        results = run_ols_regression(rets[dep.upper()], rets[valid_x])
        interp  = interpret_regression(results)
        figs    = []
        if len(valid_x) == 1:
            coefs = results["coef_df"]["Coefficient"]
            figs.append(scatter_regression(results["X"].iloc[:, -1], results["y"], valid_x[0], dep.upper(), float(coefs.iloc[-1]), float(coefs.get("const", 0))))
        from utils.charts import residual_plot as rplot
        figs.append(rplot(results["fitted"], results["residuals"]))
        html = build_report(
            title=f"Regression: {dep.upper()} ~ {' + '.join(valid_x)}",
            question=rq,
            methodology="Ordinary Least Squares (OLS) regression via statsmodels.",
            assumptions=["Linear relationship", "Normally distributed errors", "Homoscedasticity", "No perfect multicollinearity", "Independent observations"],
            data_description=f"Daily simple returns for {', '.join(tickers)} from Yahoo Finance. Period: {start} to {end}. N = {results['n_obs']}.",
            results_text=f"R² = {results['r_squared']:.4f}, Adj. R² = {results['adj_r_squared']:.4f}, F p-value = {results['f_pvalue']:.4f}.",
            interpretation=interp,
            limitations=["OLS may be affected by heteroscedasticity", "Correlation ≠ causation", "In-sample results may not generalize"],
            conclusion=f"The model {'significantly' if results['f_pvalue'] < 0.05 else 'does not significantly'} explains {dep.upper()} return variation (R² = {results['r_squared']:.4f}).",
            metrics={"R²": f"{results['r_squared']:.4f}", "Adj. R²": f"{results['adj_r_squared']:.4f}", "F p-value": f"{results['f_pvalue']:.4f}", "N": str(results['n_obs'])},
            tables=[results["coef_df"].round(6).reset_index()], figures=figs, tickers=tickers, date_range=(str(start), str(end)),
        )
        st.session_state["generated_report_html"]  = html
        st.session_state["generated_report_title"] = f"Regression_{dep}_{'+'.join(valid_x)}"
        st.success("Report ready.")

# ── PORTFOLIO ─────────────────────────────────────────────────────────────────
elif report_type == "Portfolio Optimization":
    c1, c2 = st.columns(2)
    with c1:
        tickers_raw = st.text_input("Tickers", value="SPY, QQQ, GLD, TLT, VNQ")
        rf_in       = st.number_input("Risk-free rate (%)", value=5.0, step=0.1)
    with c2:
        start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START))
        end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END))
    rq = st.text_area("Research question", value="What allocation maximizes the Sharpe ratio?", height=70)

    if st.button("Generate Report", type="primary"):
        tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
        rf      = rf_in / 100.0
        with st.spinner("Running optimization..."):
            rets = fetch_simple_returns(tickers, str(start), str(end))
        valid = [t for t in tickers if t in rets.columns]
        if len(valid) < 2: st.error("Need at least 2 valid tickers."); st.stop()
        rets  = rets[valid].dropna()
        mu    = rets.mean().values; cov = rets.cov().values
        ms    = optimize_max_sharpe(mu, cov, rf)
        eq    = equal_weight_portfolio(mu, cov, rf)
        from utils.portfolio import generate_efficient_frontier, generate_random_portfolios
        frontier = generate_efficient_frontier(mu, cov, rf, n_points=60)
        random   = generate_random_portfolios(mu, cov, rf, n=1500)
        fig_ef   = efficient_frontier_chart(frontier, random, {"Max Sharpe": {"return": ms["return"], "volatility": ms["volatility"]}, "Equal Weight": {"return": eq["return"], "volatility": eq["volatility"]}}, valid)
        fig_wts  = portfolio_weights_bar(valid, ms["weights"], "Max Sharpe Weights")
        wdf      = pd.DataFrame({"Ticker": valid, "Weight (%)": (ms["weights"]*100).round(2)})
        html = build_report(
            title=f"Portfolio Optimization: {', '.join(valid[:4])}{'...' if len(valid)>4 else ''}",
            question=rq,
            methodology="Mean-Variance Optimization (Markowitz 1952) via scipy SLSQP, long-only constraints.",
            assumptions=["Normally distributed returns", "Stable historical covariance", "No transaction costs"],
            data_description=f"Daily simple returns for {', '.join(valid)}. Period: {start} to {end}. N = {len(rets)}.",
            results_text=f"Max Sharpe: Return = {ms['return']:.2%}, Vol = {ms['volatility']:.2%}, Sharpe = {ms['sharpe']:.3f}.",
            interpretation=f"The Maximum Sharpe portfolio achieves {ms['return']:.2%} return, {ms['volatility']:.2%} volatility, Sharpe {ms['sharpe']:.3f}.",
            limitations=["MPT is sensitive to input estimates", "In-sample optimization overfits", "Correlations are not stable"],
            conclusion="Optimal allocation presented above. Results are research-oriented, not investment advice.",
            metrics={"Ann. Return": f"{ms['return']:.2%}", "Ann. Vol": f"{ms['volatility']:.2%}", "Sharpe": f"{ms['sharpe']:.3f}", "Assets": str(len(valid))},
            tables=[wdf], figures=[fig_ef, fig_wts], tickers=valid, date_range=(str(start), str(end)),
        )
        st.session_state["generated_report_html"]  = html
        st.session_state["generated_report_title"] = f"Portfolio_{'_'.join(valid[:3])}"
        st.success("Report ready.")

# ── CORRELATION ───────────────────────────────────────────────────────────────
elif report_type == "Correlation Analysis":
    c1, c2 = st.columns(2)
    with c1: tickers_raw = st.text_input("Tickers", value="SPY, QQQ, GLD, TLT, BTC-USD")
    with c2:
        start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START))
        end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END))
    rq = st.text_area("Research question", value="What is the co-movement structure among these assets?", height=70)

    if st.button("Generate Report", type="primary"):
        tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
        with st.spinner("Computing correlations..."):
            rets = fetch_simple_returns(tickers, str(start), str(end))
        valid = [t for t in tickers if t in rets.columns]
        rets  = rets[valid].dropna()
        corr  = compute_correlation_matrix(rets)
        from utils.statistics import correlation_pairs as cp
        pairs = cp(corr)
        fig_h = correlation_heatmap(corr)
        avg   = pairs["Correlation"].mean()
        html  = build_report(
            title=f"Correlation Analysis: {', '.join(valid[:5])}",
            question=rq,
            methodology="Pearson correlation on daily simple returns.",
            assumptions=["Linear relationships", "Approximate normality", "Stationarity"],
            data_description=f"Daily returns for {', '.join(valid)}. Period: {start} to {end}. N = {len(rets)}.",
            results_text=f"Average pairwise correlation: {avg:.3f}. Highest: {pairs.iloc[0]['Asset A']}/{pairs.iloc[0]['Asset B']} ({pairs.iloc[0]['Correlation']:.3f}). Lowest: {pairs.iloc[-1]['Asset A']}/{pairs.iloc[-1]['Asset B']} ({pairs.iloc[-1]['Correlation']:.3f}).",
            interpretation=f"Average correlation {avg:.3f}. {'High correlation limits diversification.' if avg > 0.6 else 'Meaningful diversification opportunities exist.'}",
            limitations=["Correlations are not stable over time", "Pearson captures only linear relationships", "Tail dependence not modeled"],
            conclusion="Correlation structure analyzed. Monitor rolling correlations for regime changes.",
            metrics={"Assets": str(len(valid)), "Avg Corr": f"{avg:.3f}", "N": str(len(rets))},
            tables=[pairs.head(10).round(4)], figures=[fig_h], tickers=valid, date_range=(str(start), str(end)),
        )
        st.session_state["generated_report_html"]  = html
        st.session_state["generated_report_title"] = f"Correlation_{'_'.join(valid[:3])}"
        st.success("Report ready.")

# ── DISTRIBUTION ──────────────────────────────────────────────────────────────
elif report_type == "Return Distribution":
    c1, c2 = st.columns(2)
    with c1: ticker = st.text_input("Ticker", value="SPY")
    with c2:
        start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START))
        end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END))
    rq = st.text_area("Research question", value="How does the empirical return distribution deviate from normality?", height=70)

    if st.button("Generate Report", type="primary"):
        with st.spinner("Loading..."):
            rets = fetch_simple_returns([ticker.upper()], str(start), str(end))
        if rets.empty or ticker.upper() not in rets.columns:
            st.error("Invalid ticker.")
            st.stop()
        s   = rets[ticker.upper()]
        ds  = return_distribution_stats(s)
        from utils.statistics import historical_var, historical_cvar
        var95  = historical_var(s, 0.95)
        cvar95 = historical_cvar(s, 0.95)
        fig_h  = returns_histogram(s, ticker.upper(), bins=70)
        html   = build_report(
            title=f"Return Distribution: {ticker.upper()}",
            question=rq,
            methodology="Empirical distribution analysis, Jarque-Bera normality test, historical VaR/CVaR.",
            assumptions=["i.i.d. returns (approximate)", "Historical distribution is representative"],
            data_description=f"Daily simple returns for {ticker.upper()}. Period: {start} to {end}. N = {ds['count']}.",
            results_text=f"Ann. return {ds['mean_annual']:.2%}, vol {ds['std_annual']:.2%}. Skew {ds['skewness']:.4f}, kurtosis {ds['excess_kurtosis']:.4f}. JB p = {ds['jarque_bera_pvalue']:.4f}.",
            interpretation=f"Returns are {'approximately normal' if ds['is_normal'] else 'non-normal'} (JB p = {ds['jarque_bera_pvalue']:.4f}). 95% CVaR = {cvar95:.2%}.",
            limitations=["i.i.d. assumption violated in practice", "Normal distribution underestimates tail risk"],
            conclusion=f"Historical CVaR of {cvar95:.2%} represents expected loss beyond the 95% VaR threshold.",
            metrics={"Ann. Return": f"{ds['mean_annual']:.2%}", "Ann. Vol": f"{ds['std_annual']:.2%}", "Skew": f"{ds['skewness']:.4f}", "Kurtosis": f"{ds['excess_kurtosis']:.4f}", "95% CVaR": f"{cvar95:.2%}"},
            figures=[fig_h], tickers=[ticker.upper()], date_range=(str(start), str(end)),
        )
        st.session_state["generated_report_html"]  = html
        st.session_state["generated_report_title"] = f"Distribution_{ticker.upper()}"
        st.success("Report ready.")

# ── CUSTOM ────────────────────────────────────────────────────────────────────
else:
    title   = st.text_input("Title", value="Custom Research Report")
    rq      = st.text_area("Research question", height=70)
    data    = st.text_area("Data description", height=70)
    method  = st.text_area("Methodology", height=70)
    assump  = st.text_area("Assumptions (one per line)", height=90)
    results_t = st.text_area("Results", height=70)
    interp  = st.text_area("Interpretation", height=70)
    limits  = st.text_area("Limitations (one per line)", height=90)
    conc    = st.text_area("Conclusion", height=70)

    if st.button("Generate Report", type="primary"):
        html = build_report(
            title=title or "Custom Report", question=rq or "N/A",
            methodology=method or "N/A",
            assumptions=[l.strip() for l in assump.splitlines() if l.strip()] or ["N/A"],
            data_description=data or "N/A", results_text=results_t or "N/A",
            interpretation=interp or "N/A",
            limitations=[l.strip() for l in limits.splitlines() if l.strip()] or ["N/A"],
            conclusion=conc or "N/A",
        )
        st.session_state["generated_report_html"]  = html
        st.session_state["generated_report_title"] = "Custom_Report"
        st.success("Report ready.")

# ── Export ────────────────────────────────────────────────────────────────────
if st.session_state.get("generated_report_html"):
    html_content = st.session_state["generated_report_html"]
    report_name  = st.session_state.get("generated_report_title", "AlphaLab_Report")
    st.divider()
    c1, c2 = st.columns([1, 1])
    with c1:
        st.download_button("Download HTML Report", data=html_content.encode("utf-8"),
                           file_name=f"{report_name}.html", mime="text/html", use_container_width=True)
    with c2:
        if st.button("Preview", use_container_width=True):
            st.session_state["show_preview"] = not st.session_state.get("show_preview", False)
    if st.session_state.get("show_preview", False):
        st.components.v1.html(html_content, height=800, scrolling=True)

info_box("All reports are for research and educational use only. Not financial advice.", "warning")
