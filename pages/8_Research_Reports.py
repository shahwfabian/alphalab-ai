"""
AlphaLab AI — Research Reports
Generate, preview, and export professional HTML research reports.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import (
    fetch_simple_returns, fetch_prices, DEFAULT_START, DEFAULT_END,
    annualized_return, annualized_volatility,
)
from utils.statistics import (
    run_ols_regression, interpret_regression, return_distribution_stats,
    compute_correlation_matrix,
)
from utils.portfolio import (
    optimize_max_sharpe, equal_weight_portfolio, compute_portfolio_stats,
)
from utils.charts import (
    scatter_regression, correlation_heatmap, returns_histogram,
    efficient_frontier_chart, portfolio_weights_bar,
)
from utils.report_generator import build_report

st.set_page_config(page_title="Research Reports — AlphaLab AI", page_icon="📄", layout="wide")

st.markdown("""
<style>
.stApp{background:#0A0E1A}
[data-testid="stSidebar"]{background:#070B16!important;border-right:1px solid #1E2D4A}
.stButton>button{background:linear-gradient(135deg,#00D4FF18,#00D4FF0A);border:1px solid #00D4FF;color:#00D4FF;font-weight:600;border-radius:6px}
.stTextInput>div>div>input,.stTextArea textarea,.stSelectbox>div>div{background:#0F1628!important;border:1px solid #1E2D4A!important;color:#E8F4FD!important;border-radius:6px!important}
[data-testid="metric-container"]{background:#0F1628!important;border:1px solid #1E2D4A!important;border-radius:8px!important;padding:16px!important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#00D4FF!important;font-family:JetBrains Mono,monospace!important}
.stTabs [data-baseweb="tab-list"]{background:#0F1628;border-radius:8px;gap:4px}
.stTabs [data-baseweb="tab"]{color:#6B8CAE;padding:8px 20px;border-radius:6px}
.stTabs [aria-selected="true"]{background:rgba(0,212,255,0.12)!important;color:#00D4FF!important}
</style>
""", unsafe_allow_html=True)

NAVY = "#0A0E1A"; PANEL = "#0F1628"; BLUE = "#00D4FF"; GOLD = "#FFD700"
RED = "#FF4B6E"; CYAN = "#00FFD4"; GRID = "#1E2D4A"; TEXT = "#E8F4FD"

# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding:30px 0 10px 0;'>
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;'>MODULE 08</div>
    <div style='font-size:32px;font-weight:700;color:#00D4FF;font-family:JetBrains Mono,monospace;margin-top:6px;'>📄 Research Reports</div>
    <div style='color:#6B8CAE;font-size:14px;margin-top:8px;'>
        Generate a professional research report complete with methodology, results, and visualizations. Export to HTML.
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── Report Builder ───────────────────────────────────────────────────────────

report_type = st.selectbox(
    "Report Type",
    [
        "Regression Analysis Report",
        "Portfolio Optimization Report",
        "Correlation Analysis Report",
        "Return Distribution Report",
        "Custom Research Report",
    ],
    key="rpt_type",
)

st.markdown("<br>", unsafe_allow_html=True)

# ─── REGRESSION REPORT ───────────────────────────────────────────────────────

if report_type == "Regression Analysis Report":
    st.markdown(f"""
    <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:20px;margin-bottom:20px;'>
        <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:12px;'>REPORT CONFIGURATION</div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        dep_tick = st.text_input("Dependent Variable (Y)", value="NVDA", key="rpt_reg_y")
        indep_raw = st.text_input("Independent Variable(s) (X)", value="SPY, QQQ", key="rpt_reg_x")
    with c2:
        start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START), key="rpt_reg_start")
        end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END),   key="rpt_reg_end")

    rq = st.text_area("Research Question",
        value=f"Does QQQ explain NVDA returns better than SPY over the selected period?",
        height=80, key="rpt_reg_rq")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("▶ Generate Regression Report", use_container_width=False, key="rpt_reg_gen"):
        indep_tickers = [t.strip().upper() for t in indep_raw.split(",") if t.strip()]
        all_tickers   = [dep_tick.upper()] + indep_tickers

        with st.spinner("Fetching data and running regression..."):
            returns = fetch_simple_returns(all_tickers, str(start), str(end))

        if returns.empty:
            st.error("Could not load data.")
            st.stop()

        valid_indep = [t for t in indep_tickers if t in returns.columns]
        if not valid_indep or dep_tick.upper() not in returns.columns:
            st.error("Invalid ticker symbols.")
            st.stop()

        y = returns[dep_tick.upper()]
        X = returns[valid_indep]
        results = run_ols_regression(y, X, add_constant=True)
        interp  = interpret_regression(results)

        figures = []
        if len(valid_indep) == 1:
            coefs     = results["coef_df"]["Coefficient"]
            slope     = float(coefs.iloc[-1])
            intercept = float(coefs.get("const", 0.0))
            fig_sc    = scatter_regression(results["X"].iloc[:,-1], results["y"],
                                           valid_indep[0], dep_tick.upper(), slope, intercept)
            figures.append(fig_sc)

        from utils.charts import residual_plot as rplot
        fig_res = rplot(results["fitted"], results["residuals"])
        figures.append(fig_res)

        metrics = {
            "R²":           f"{results['r_squared']:.4f}",
            "Adj. R²":      f"{results['adj_r_squared']:.4f}",
            "F-Statistic":  f"{results['f_statistic']:.4f}",
            "F p-value":    f"{results['f_pvalue']:.4f}",
            "Observations": str(results["n_obs"]),
            "AIC":          f"{results['aic']:.2f}",
        }

        assumptions = [
            "Linear relationship between dependent and independent variable(s)",
            "Errors are normally distributed with mean zero",
            "Homoscedasticity: constant variance of residuals",
            "No perfect multicollinearity among predictors",
            "Observations are independent (no autocorrelation)",
        ]
        limitations = [
            "OLS results assume stationarity; financial returns may exhibit regime changes",
            "Heteroscedasticity common in financial data — consider robust standard errors",
            "R² measures explanatory power only, not predictive accuracy on new data",
            "Correlation in regression coefficients does not imply economic causation",
            "Results are specific to the historical period analyzed",
        ]

        html = build_report(
            title=f"Regression Analysis: {dep_tick.upper()} ~ {' + '.join(valid_indep)}",
            question=rq,
            methodology=(
                f"Ordinary Least Squares (OLS) regression of {dep_tick.upper()} daily simple returns "
                f"on {', '.join(valid_indep)} returns, with a constant term. "
                f"Implemented using statsmodels OLS."
            ),
            assumptions=assumptions,
            data_description=(
                f"Daily simple returns for {', '.join(all_tickers)} downloaded from Yahoo Finance "
                f"via yfinance. Period: {start} to {end}. N = {results['n_obs']} observations."
            ),
            results_text=(
                f"OLS regression results: R² = {results['r_squared']:.4f}, "
                f"Adjusted R² = {results['adj_r_squared']:.4f}, "
                f"F-statistic = {results['f_statistic']:.4f} (p = {results['f_pvalue']:.4f})."
            ),
            interpretation=interp,
            limitations=limitations,
            conclusion=(
                f"The regression model {'explains a statistically significant' if results['f_pvalue'] < 0.05 else 'does not demonstrate a statistically significant'} "
                f"portion of variance in {dep_tick.upper()} returns. "
                f"R² = {results['r_squared']:.4f} indicates that approximately "
                f"{results['r_squared']:.1%} of return variation is explained by the model. "
                f"Results are historically descriptive and should not be used for prediction without validation."
            ),
            metrics=metrics,
            tables=[results["coef_df"].round(6).reset_index()],
            figures=figures,
            tickers=all_tickers,
            date_range=(str(start), str(end)),
        )

        st.session_state["generated_report_html"] = html
        st.session_state["generated_report_title"] = f"Regression_{dep_tick}_{'_'.join(valid_indep)}"
        st.success("✅ Report generated successfully.")

# ─── PORTFOLIO REPORT ─────────────────────────────────────────────────────────

elif report_type == "Portfolio Optimization Report":
    c1, c2 = st.columns(2)
    with c1:
        tickers_raw = st.text_input("Tickers (comma-separated)", value="SPY, QQQ, GLD, TLT, VNQ", key="rpt_port_tickers")
        rf_input    = st.number_input("Risk-Free Rate (%)", value=5.0, step=0.1, key="rpt_port_rf")
    with c2:
        start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START), key="rpt_port_start")
        end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END),   key="rpt_port_end")

    rq = st.text_area("Research Question",
        value="What is the optimal asset allocation to maximize the Sharpe ratio among the selected assets?",
        height=80, key="rpt_port_rq")

    if st.button("▶ Generate Portfolio Report", key="rpt_port_gen"):
        tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
        rf      = rf_input / 100.0

        with st.spinner("Running portfolio optimization..."):
            returns = fetch_simple_returns(tickers, str(start), str(end))

        valid = [t for t in tickers if t in returns.columns]
        if len(valid) < 2:
            st.error("Need at least 2 valid tickers.")
            st.stop()

        returns = returns[valid].dropna()
        mu  = returns.mean().values
        cov = returns.cov().values

        ms_port = optimize_max_sharpe(mu, cov, rf)
        eq_port = equal_weight_portfolio(mu, cov, rf)

        from utils.portfolio import generate_efficient_frontier, generate_random_portfolios
        frontier = generate_efficient_frontier(mu, cov, rf, n_points=80)
        random   = generate_random_portfolios(mu, cov, rf, n=2000)

        portfolios_chart = {
            "Max Sharpe":   {"return": ms_port["return"], "volatility": ms_port["volatility"]},
            "Equal Weight": {"return": eq_port["return"],  "volatility": eq_port["volatility"]},
        }
        fig_ef  = efficient_frontier_chart(frontier, random, portfolios_chart, valid)
        fig_wts = portfolio_weights_bar(valid, ms_port["weights"], "Max Sharpe Portfolio Weights")

        weight_df = pd.DataFrame({"Ticker": valid, "Weight (%)": (ms_port["weights"]*100).round(2)})
        metrics   = {
            "Ann. Return":  f"{ms_port['return']:.2%}",
            "Ann. Vol":     f"{ms_port['volatility']:.2%}",
            "Sharpe Ratio": f"{ms_port['sharpe']:.3f}",
            "Assets":       str(len(valid)),
            "RF Rate":      f"{rf:.2%}",
        }

        html = build_report(
            title=f"Portfolio Optimization Report: {', '.join(valid[:4])}{'...' if len(valid)>4 else ''}",
            question=rq,
            methodology=(
                "Mean-Variance Optimization (Modern Portfolio Theory, Markowitz 1952). "
                "Expected returns estimated from historical daily returns. Covariance matrix "
                "estimated from historical daily return covariance. Optimization via scipy SLSQP "
                "with long-only constraints (weights ≥ 0, sum = 1)."
            ),
            assumptions=[
                "Returns are jointly normally distributed",
                "Historical mean returns are representative of future expected returns",
                "Historical covariance matrix is representative of future co-movement",
                "No transaction costs, taxes, or trading constraints beyond long-only",
                "Investors are mean-variance rational (maximize return for given risk)",
            ],
            data_description=(
                f"Daily simple returns for {', '.join(valid)} from Yahoo Finance. "
                f"Period: {start} to {end}. N = {len(returns)} observations per asset."
            ),
            results_text=(
                f"Maximum Sharpe Portfolio: Return = {ms_port['return']:.2%}, "
                f"Volatility = {ms_port['volatility']:.2%}, Sharpe = {ms_port['sharpe']:.3f}. "
                f"Largest allocation: {valid[int(np.argmax(ms_port['weights']))]} "
                f"({ms_port['weights'].max():.1%})."
            ),
            interpretation=(
                f"The Maximum Sharpe portfolio achieves an estimated annualized return of {ms_port['return']:.2%} "
                f"with {ms_port['volatility']:.2%} volatility, yielding a Sharpe ratio of {ms_port['sharpe']:.3f}. "
                f"This is the portfolio with the highest expected excess return per unit of risk. "
                f"The efficient frontier shows the set of all portfolios that cannot be improved "
                f"(higher return for same risk, or lower risk for same return)."
            ),
            limitations=[
                "MPT is highly sensitive to estimated expected returns — small errors cause large weight changes",
                "Historical covariance is an imperfect predictor of future co-movement",
                "Optimization tends to concentrate heavily in a few assets (corner solutions)",
                "Long-only constraint may prevent full diversification benefit",
                "Results are in-sample; out-of-sample performance typically degrades significantly",
            ],
            conclusion=(
                "The optimal asset allocation subject to long-only constraints and historical data "
                f"is presented above. Users should treat this as a starting point for analysis, "
                "not a trading recommendation. Regular rebalancing, transaction costs, taxes, and "
                "regime changes are not modeled here."
            ),
            metrics=metrics,
            tables=[weight_df],
            figures=[fig_ef, fig_wts],
            tickers=valid,
            date_range=(str(start), str(end)),
        )

        st.session_state["generated_report_html"] = html
        st.session_state["generated_report_title"] = f"Portfolio_{'_'.join(valid[:3])}"
        st.success("✅ Report generated successfully.")

# ─── CORRELATION REPORT ───────────────────────────────────────────────────────

elif report_type == "Correlation Analysis Report":
    c1, c2 = st.columns(2)
    with c1:
        tickers_raw = st.text_input("Tickers", value="SPY, QQQ, GLD, TLT, BTC-USD", key="rpt_corr_t")
    with c2:
        start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START), key="rpt_corr_start")
        end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END),   key="rpt_corr_end")

    rq = st.text_area("Research Question",
        value="What is the co-movement structure among these assets and what are the diversification implications?",
        height=80, key="rpt_corr_rq")

    if st.button("▶ Generate Correlation Report", key="rpt_corr_gen"):
        tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]

        with st.spinner("Computing correlations..."):
            returns = fetch_simple_returns(tickers, str(start), str(end))

        valid = [t for t in tickers if t in returns.columns]
        returns = returns[valid].dropna()
        corr_mx = compute_correlation_matrix(returns)

        from utils.statistics import correlation_pairs as cp
        pairs = cp(corr_mx)
        fig_heat = correlation_heatmap(corr_mx)
        avg_corr = pairs["Correlation"].mean()

        metrics = {
            "Assets":       str(len(valid)),
            "Avg Corr":     f"{avg_corr:.3f}",
            "Max Corr":     f"{pairs.iloc[0]['Correlation']:.3f}",
            "Min Corr":     f"{pairs.iloc[-1]['Correlation']:.3f}",
            "Observations": str(len(returns)),
        }

        html = build_report(
            title=f"Correlation Analysis: {', '.join(valid[:5])}{'...' if len(valid)>5 else ''}",
            question=rq,
            methodology=(
                "Pearson correlation analysis on daily simple returns. "
                "Pairwise correlations computed across all asset combinations. "
                "Rolling correlation computed with 60-day window."
            ),
            assumptions=[
                "Linear relationship between asset returns (Pearson assumes linearity)",
                "Returns are approximately normally distributed",
                "Stationarity: correlation structure is stable over the analysis period",
                "No significant outliers distorting pairwise estimates",
            ],
            data_description=(
                f"Daily simple returns for {', '.join(valid)} from Yahoo Finance. "
                f"Period: {start} to {end}. N = {len(returns)} observations."
            ),
            results_text=f"Average pairwise correlation: {avg_corr:.3f}. "
                f"Most correlated: {pairs.iloc[0]['Asset A']} / {pairs.iloc[0]['Asset B']} (r = {pairs.iloc[0]['Correlation']:.3f}). "
                f"Least correlated: {pairs.iloc[-1]['Asset A']} / {pairs.iloc[-1]['Asset B']} (r = {pairs.iloc[-1]['Correlation']:.3f}).",
            interpretation=(
                f"The asset set shows an average pairwise correlation of {avg_corr:.3f}. "
                f"{'High average correlation limits diversification potential.' if avg_corr > 0.6 else 'Moderate-to-low correlations suggest meaningful diversification opportunities.'} "
                f"The best diversifying pair is {pairs.iloc[-1]['Asset A']} / {pairs.iloc[-1]['Asset B']}."
            ),
            limitations=[
                "Correlations are not stable over time — they tend to increase during market stress",
                "Pearson correlation only captures linear relationships",
                "Historical correlation is an imperfect estimate of future co-movement",
                "Correlation says nothing about directionality or causation",
            ],
            conclusion=(
                "The correlation structure suggests opportunities for portfolio diversification, "
                "particularly through combining low-correlation asset pairs. "
                "Users should monitor correlations over time and consider regime-conditional behavior."
            ),
            metrics=metrics,
            tables=[pairs.head(10).round(4)],
            figures=[fig_heat],
            tickers=valid,
            date_range=(str(start), str(end)),
        )

        st.session_state["generated_report_html"] = html
        st.session_state["generated_report_title"] = f"Correlation_{'_'.join(valid[:3])}"
        st.success("✅ Report generated successfully.")

# ─── RETURN DISTRIBUTION REPORT ──────────────────────────────────────────────

elif report_type == "Return Distribution Report":
    c1, c2 = st.columns(2)
    with c1:
        ticker = st.text_input("Ticker", value="SPY", key="rpt_dist_t")
    with c2:
        start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START), key="rpt_dist_start")
        end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END),   key="rpt_dist_end")

    rq = st.text_area("Research Question",
        value="What is the empirical return distribution of SPY and how does it deviate from normality?",
        height=80, key="rpt_dist_rq")

    if st.button("▶ Generate Distribution Report", key="rpt_dist_gen"):
        with st.spinner("Loading data..."):
            returns = fetch_simple_returns([ticker.upper()], str(start), str(end))

        if returns.empty or ticker.upper() not in returns.columns:
            st.error("Invalid ticker.")
            st.stop()

        ret = returns[ticker.upper()]
        ds  = return_distribution_stats(ret)
        from utils.statistics import historical_var, historical_cvar
        var95 = historical_var(ret, 0.95)
        cvar95 = historical_cvar(ret, 0.95)

        fig_hist = returns_histogram(ret, ticker.upper(), bins=70)

        metrics = {
            "Ann. Return":  f"{ds['mean_annual']:.2%}",
            "Ann. Vol":     f"{ds['std_annual']:.2%}",
            "Skewness":     f"{ds['skewness']:.4f}",
            "Exc. Kurtosis":f"{ds['excess_kurtosis']:.4f}",
            "95% VaR":      f"{var95:.2%}",
            "95% CVaR":     f"{cvar95:.2%}",
        }

        html = build_report(
            title=f"Return Distribution Analysis: {ticker.upper()}",
            question=rq,
            methodology=(
                "Empirical return distribution analysis using historical daily simple returns. "
                "Jarque-Bera test for normality. Historical Value-at-Risk (VaR) and Conditional VaR (CVaR / Expected Shortfall). "
                "Kernel Density Estimation (KDE) compared to fitted Normal distribution."
            ),
            assumptions=[
                "Returns are i.i.d. (independently and identically distributed) — this is often violated",
                "Historical distribution is representative of future return behavior",
                "Yahoo Finance adjusted price data is accurate and complete",
            ],
            data_description=f"Daily simple returns for {ticker.upper()} from Yahoo Finance. Period: {start} to {end}. N = {ds['count']} observations.",
            results_text=(
                f"Mean daily return: {ds['mean_daily']:.6f} ({ds['mean_annual']:.2%} annualized). "
                f"Daily standard deviation: {ds['std_daily']:.6f} ({ds['std_annual']:.2%} annualized). "
                f"Skewness: {ds['skewness']:.4f}. Excess kurtosis: {ds['excess_kurtosis']:.4f}. "
                f"Jarque-Bera p-value: {ds['jarque_bera_pvalue']:.6f} ({'Normal' if ds['is_normal'] else 'Non-Normal'})."
            ),
            interpretation=(
                f"{ticker.upper()} daily returns show {'approximate normality' if ds['is_normal'] else 'significant departure from normality'} "
                f"(Jarque-Bera p = {ds['jarque_bera_pvalue']:.4f}). "
                f"Skewness of {ds['skewness']:.4f} indicates {'slight left tail' if ds['skewness'] < 0 else 'slight right tail'}. "
                f"Excess kurtosis of {ds['excess_kurtosis']:.4f} indicates {'fat tails (leptokurtic)' if ds['excess_kurtosis'] > 0 else 'thin tails (platykurtic)'} "
                f"relative to the Normal distribution."
            ),
            limitations=[
                "i.i.d. assumption is typically violated for financial returns (autocorrelation, volatility clustering)",
                "Historical distribution does not guarantee future tail behavior",
                "Normal distribution systematically underestimates extreme event probabilities",
                "VaR is not a coherent risk measure (lacks sub-additivity); CVaR is preferred",
            ],
            conclusion=(
                f"The historical analysis of {ticker.upper()} returns reveals "
                f"{'departures from normality that should be considered in risk modeling' if not ds['is_normal'] else 'approximately normal behavior, though caution is warranted for tail risk'}. "
                f"The 95% CVaR of {cvar95:.2%} represents the average loss on the worst 5% of trading days historically."
            ),
            metrics=metrics,
            figures=[fig_hist],
            tickers=[ticker.upper()],
            date_range=(str(start), str(end)),
        )

        st.session_state["generated_report_html"] = html
        st.session_state["generated_report_title"] = f"Distribution_{ticker.upper()}"
        st.success("✅ Report generated successfully.")

# ─── CUSTOM REPORT ────────────────────────────────────────────────────────────

else:  # Custom
    st.markdown("**Build a custom report by filling in each section manually.**")
    rpt_title   = st.text_input("Report Title", value="Custom Research Report", key="rpt_cust_title")
    rpt_q       = st.text_area("Research Question", height=80, key="rpt_cust_rq")
    rpt_data    = st.text_area("Data Description", height=80, key="rpt_cust_data")
    rpt_method  = st.text_area("Methodology", height=100, key="rpt_cust_method")
    rpt_assump  = st.text_area("Assumptions (one per line)", height=100, key="rpt_cust_assump")
    rpt_results = st.text_area("Results", height=100, key="rpt_cust_results")
    rpt_interp  = st.text_area("Interpretation", height=100, key="rpt_cust_interp")
    rpt_limits  = st.text_area("Limitations (one per line)", height=100, key="rpt_cust_limits")
    rpt_conc    = st.text_area("Conclusion", height=100, key="rpt_cust_conc")

    if st.button("▶ Generate Custom Report", key="rpt_cust_gen"):
        html = build_report(
            title=rpt_title or "Custom Research Report",
            question=rpt_q or "N/A",
            methodology=rpt_method or "N/A",
            assumptions=[l.strip() for l in rpt_assump.splitlines() if l.strip()] or ["N/A"],
            data_description=rpt_data or "N/A",
            results_text=rpt_results or "N/A",
            interpretation=rpt_interp or "N/A",
            limitations=[l.strip() for l in rpt_limits.splitlines() if l.strip()] or ["N/A"],
            conclusion=rpt_conc or "N/A",
        )
        st.session_state["generated_report_html"] = html
        st.session_state["generated_report_title"] = "Custom_Report"
        st.success("✅ Custom report generated.")

# ─── Report Output ────────────────────────────────────────────────────────────

if st.session_state.get("generated_report_html"):
    html_content = st.session_state["generated_report_html"]
    report_name  = st.session_state.get("generated_report_title", "AlphaLab_Report")

    st.markdown("---")
    st.markdown(f"""
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;margin-bottom:16px;'>
    REPORT READY — EXPORT OPTIONS
    </div>
    """, unsafe_allow_html=True)

    col_dl, col_prev = st.columns([1, 1])

    with col_dl:
        st.download_button(
            label="⬇ Download HTML Report",
            data=html_content.encode("utf-8"),
            file_name=f"{report_name}.html",
            mime="text/html",
            use_container_width=True,
        )
        st.markdown(f"""
        <div style='color:#6B8CAE;font-size:12px;margin-top:8px;'>
        Open the downloaded HTML file in any browser for the full formatted report.
        Print to PDF using your browser's print function (Ctrl+P → Save as PDF).
        </div>
        """, unsafe_allow_html=True)

    with col_prev:
        if st.button("👁 Preview in Browser (Inline)", use_container_width=True, key="rpt_preview"):
            st.session_state["show_report_preview"] = True

    if st.session_state.get("show_report_preview", False):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Report Preview:**")
        st.components.v1.html(html_content, height=900, scrolling=True)
        if st.button("Hide Preview", key="rpt_hide"):
            st.session_state["show_report_preview"] = False
            st.rerun()

st.markdown("<br>")
st.markdown(f"""
<div style='background:rgba(255,215,0,0.04);border:1px solid {GOLD}33;border-radius:6px;padding:12px 16px;color:#FFD70099;font-size:11px;'>
⚠ All reports generated by AlphaLab AI are for research and educational purposes only.
They do not constitute financial advice, investment recommendations, or performance guarantees.
</div>
""", unsafe_allow_html=True)
