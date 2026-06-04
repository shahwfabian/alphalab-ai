"""
AlphaLab AI — Portfolio Optimization Lab
Modern Portfolio Theory: Max-Sharpe, Min-Variance, Equal Weight, Efficient Frontier.
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import (
    fetch_simple_returns, DEFAULT_START, DEFAULT_END,
)
from utils.portfolio import (
    optimize_max_sharpe, optimize_min_variance, equal_weight_portfolio,
    generate_efficient_frontier, generate_random_portfolios,
    build_portfolio_summary, compute_portfolio_stats,
)
from utils.charts import (
    efficient_frontier_chart, portfolio_weights_bar,
    cumulative_return_chart,
)

st.set_page_config(page_title="Portfolio Optimization — AlphaLab AI", page_icon="💼", layout="wide")

st.markdown("""
<style>
.stApp{background:#0A0E1A}
[data-testid="stSidebar"]{background:#070B16!important;border-right:1px solid #1E2D4A}
.stButton>button{background:linear-gradient(135deg,#00D4FF18,#00D4FF0A);border:1px solid #00D4FF;color:#00D4FF;font-weight:600;border-radius:6px}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stSelectbox>div>div,.stSlider{background:#0F1628!important;border:1px solid #1E2D4A!important;color:#E8F4FD!important}
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
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;'>MODULE 05</div>
    <div style='font-size:32px;font-weight:700;color:#00D4FF;font-family:JetBrains Mono,monospace;margin-top:6px;'>💼 Portfolio Optimization Lab</div>
    <div style='color:#6B8CAE;font-size:14px;margin-top:8px;'>
        Modern Portfolio Theory — find the Maximum Sharpe, Minimum Variance, and trace the Efficient Frontier.
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── Configuration ────────────────────────────────────────────────────────────

col_cfg, col_run = st.columns([4, 1])

with col_cfg:
    c1, c2 = st.columns(2)
    with c1:
        tickers_raw = st.text_input(
            "Ticker Symbols (comma-separated, min 2)",
            value="SPY, QQQ, GLD, TLT, VNQ",
            key="port_tickers",
        )
    with c2:
        rf_input = st.number_input(
            "Risk-Free Rate (annual %)",
            value=float(st.session_state.get("risk_free_rate", 0.05)) * 100,
            min_value=0.0, max_value=20.0, step=0.1,
            key="port_rf",
            help="Annual risk-free rate used to compute Sharpe ratio (e.g., 5.0 = 5%)",
        )

    c3, c4, c5 = st.columns(3)
    with c3:
        start = st.date_input("Start Date", value=pd.to_datetime(DEFAULT_START), key="port_start")
    with c4:
        end   = st.date_input("End Date",   value=pd.to_datetime(DEFAULT_END),   key="port_end")
    with c5:
        allow_short = st.checkbox("Allow Short Selling", value=False, key="port_short",
                                  help="If enabled, weights may be negative (short positions)")

with col_run:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    run_btn = st.button("▶ Optimize", use_container_width=True, key="port_run")

# ─── Optimization Engine ──────────────────────────────────────────────────────

if run_btn:
    tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
    rf      = rf_input / 100.0
    w_bounds = (-1.0, 1.0) if allow_short else (0.0, 1.0)

    if len(tickers) < 2:
        st.error("Please enter at least 2 ticker symbols.")
        st.stop()

    with st.spinner(f"Downloading {', '.join(tickers)} returns..."):
        returns = fetch_simple_returns(tickers, str(start), str(end))

    valid_tickers = [t for t in tickers if t in returns.columns]
    if len(valid_tickers) < 2:
        st.error(f"Could not load data for enough tickers. Valid: {valid_tickers}")
        st.stop()

    returns = returns[valid_tickers].dropna()
    n_obs   = len(returns)
    if n_obs < 60:
        st.warning(f"Only {n_obs} observations — results may be unreliable. Try a wider date range.")

    mean_returns = returns.mean().values
    cov_matrix   = returns.cov().values

    with st.spinner("Running optimization — computing Efficient Frontier..."):
        max_sharpe_port = optimize_max_sharpe(mean_returns, cov_matrix, rf, w_bounds)
        min_var_port    = optimize_min_variance(mean_returns, cov_matrix, w_bounds)
        eq_weight_port  = equal_weight_portfolio(mean_returns, cov_matrix, rf)
        frontier_df     = generate_efficient_frontier(mean_returns, cov_matrix, rf, n_points=120, weight_bounds=w_bounds)
        random_df       = generate_random_portfolios(mean_returns, cov_matrix, rf, n=4000)

    # Store for report
    st.session_state["last_portfolio_results"] = {
        "tickers": valid_tickers,
        "max_sharpe": max_sharpe_port,
        "min_var":    min_var_port,
        "eq_weight":  eq_weight_port,
        "frontier":   frontier_df,
        "returns":    returns,
        "rf":         rf,
        "start":      str(start),
        "end":        str(end),
    }

    # ─── KPI Summary ─────────────────────────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;margin-bottom:16px;'>
    PORTFOLIO COMPARISON — {', '.join(valid_tickers)}
    </div>
    """, unsafe_allow_html=True)

    def port_card(label, p, accent):
        return f"""
        <div style='background:{PANEL};border:1px solid {GRID};border-top:3px solid {accent};
                    border-radius:8px;padding:20px;'>
            <div style='color:{accent};font-family:JetBrains Mono,monospace;font-size:11px;
                        letter-spacing:2px;margin-bottom:12px;'>{label.upper()}</div>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>
                <div>
                    <div style='color:#6B8CAE;font-size:10px;text-transform:uppercase;letter-spacing:1px;'>Ann. Return</div>
                    <div style='color:{TEXT};font-family:JetBrains Mono,monospace;font-size:18px;margin-top:2px;'>{p["return"]:.2%}</div>
                </div>
                <div>
                    <div style='color:#6B8CAE;font-size:10px;text-transform:uppercase;letter-spacing:1px;'>Ann. Volatility</div>
                    <div style='color:{TEXT};font-family:JetBrains Mono,monospace;font-size:18px;margin-top:2px;'>{p["volatility"]:.2%}</div>
                </div>
                <div>
                    <div style='color:#6B8CAE;font-size:10px;text-transform:uppercase;letter-spacing:1px;'>Sharpe Ratio</div>
                    <div style='color:{accent};font-family:JetBrains Mono,monospace;font-size:18px;font-weight:700;margin-top:2px;'>{p["sharpe"]:.3f}</div>
                </div>
                <div>
                    <div style='color:#6B8CAE;font-size:10px;text-transform:uppercase;letter-spacing:1px;'>Status</div>
                    <div style='color:{accent};font-size:13px;margin-top:4px;'>{"✓ Converged" if p.get("success", True) else "⚠ Check result"}</div>
                </div>
            </div>
        </div>
        """

    pc1, pc2, pc3 = st.columns(3)
    with pc1:  st.markdown(port_card("⭐ Maximum Sharpe",    max_sharpe_port, GOLD),  unsafe_allow_html=True)
    with pc2:  st.markdown(port_card("🔵 Minimum Variance",  min_var_port,    BLUE),  unsafe_allow_html=True)
    with pc3:  st.markdown(port_card("⚪ Equal Weight",       eq_weight_port,  CYAN),  unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Tabs ─────────────────────────────────────────────────────────────────

    tab1, tab2, tab3, tab4 = st.tabs([
        "Efficient Frontier", "Portfolio Weights", "Return Analysis", "Covariance"
    ])

    with tab1:
        portfolios_for_chart = {
            "Max Sharpe":   {"return": max_sharpe_port["return"], "volatility": max_sharpe_port["volatility"]},
            "Min Variance": {"return": min_var_port["return"],    "volatility": min_var_port["volatility"]},
            "Equal Weight": {"return": eq_weight_port["return"],  "volatility": eq_weight_port["volatility"]},
        }
        fig_ef = efficient_frontier_chart(frontier_df, random_df, portfolios_for_chart, valid_tickers)
        st.plotly_chart(fig_ef, use_container_width=True)

        st.markdown(f"""
        <div style='background:{PANEL};border:1px solid {GRID};border-radius:6px;padding:14px;font-size:13px;color:#6B8CAE;line-height:1.8;'>
        <strong style='color:{TEXT};'>Reading the chart:</strong>
        Each dot represents a random portfolio allocation. The blue curve is the Efficient Frontier —
        the set of portfolios with the highest expected return for each level of risk.
        ⭐ Max Sharpe maximizes return-per-unit-risk. 🔵 Min Variance minimizes total risk.
        Portfolios <em>below</em> the frontier are suboptimal and dominated.
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        w_col1, w_col2, w_col3 = st.columns(3)

        with w_col1:
            fig_ms = portfolio_weights_bar(valid_tickers, max_sharpe_port["weights"], "Max Sharpe Weights")
            st.plotly_chart(fig_ms, use_container_width=True)

        with w_col2:
            fig_mv = portfolio_weights_bar(valid_tickers, min_var_port["weights"], "Min Variance Weights")
            st.plotly_chart(fig_mv, use_container_width=True)

        with w_col3:
            fig_ew = portfolio_weights_bar(valid_tickers, eq_weight_port["weights"], "Equal Weight")
            st.plotly_chart(fig_ew, use_container_width=True)

        # Weights comparison table
        st.markdown("**Detailed Weight Comparison**")
        weight_df = pd.DataFrame({
            "Ticker":          valid_tickers,
            "Max Sharpe (%)":  (max_sharpe_port["weights"] * 100).round(2),
            "Min Variance (%)":( min_var_port["weights"]   * 100).round(2),
            "Equal Weight (%)": (eq_weight_port["weights"]  * 100).round(2),
        })
        st.dataframe(weight_df, use_container_width=True, hide_index=True)

    with tab3:
        # Cumulative return comparison
        port_returns_df = pd.DataFrame(index=returns.index)

        port_returns_df["Max Sharpe"]   = returns.values @ max_sharpe_port["weights"]
        port_returns_df["Min Variance"] = returns.values @ min_var_port["weights"]
        port_returns_df["Equal Weight"] = returns.values @ eq_weight_port["weights"]

        fig_cr = cumulative_return_chart(port_returns_df, "Cumulative Return by Portfolio Strategy")
        st.plotly_chart(fig_cr, use_container_width=True)

        # Per-asset stats
        st.markdown("**Individual Asset Statistics**")
        asset_df = build_portfolio_summary(
            valid_tickers, max_sharpe_port["weights"], mean_returns, cov_matrix, rf
        )
        st.dataframe(asset_df, use_container_width=True, hide_index=True)

    with tab4:
        st.markdown("**Annualized Covariance Matrix**")
        cov_annual = pd.DataFrame(cov_matrix * 252, index=valid_tickers, columns=valid_tickers)
        st.dataframe(cov_annual.style.background_gradient(cmap="Blues", axis=None).format("{:.6f}"),
                     use_container_width=True)

        st.markdown("**Annualized Volatility per Asset**")
        vols = pd.DataFrame({
            "Ticker":              valid_tickers,
            "Annualized Vol (%)":  (np.sqrt(np.diag(cov_matrix) * 252) * 100).round(2),
            "Daily Mean Return (%)": (mean_returns * 100).round(4),
        })
        st.dataframe(vols, use_container_width=True, hide_index=True)

    # ─── Interpretation ──────────────────────────────────────────────────────

    st.markdown("---")
    st.markdown("**Plain-English Interpretation**")
    best = max_sharpe_port
    best_ticker_idx = int(np.argmax(max_sharpe_port["weights"]))
    dominant = valid_tickers[best_ticker_idx]
    dominant_wt = max_sharpe_port["weights"][best_ticker_idx]

    st.markdown(f"""
    The **Maximum Sharpe portfolio** achieves an estimated annualized return of **{best["return"]:.2%}**
    with annualized volatility of **{best["volatility"]:.2%}**, yielding a Sharpe ratio of
    **{best["sharpe"]:.3f}** (using {rf*100:.2f}% risk-free rate).
    The largest allocation is **{dominant}** at **{dominant_wt:.1%}** of the portfolio.

    The **Minimum Variance portfolio** (return: {min_var_port["return"]:.2%}, vol: {min_var_port["volatility"]:.2%})
    achieves the lowest possible risk for this asset set — useful for risk-minimizing mandates.

    The **Equal Weight portfolio** provides a naive baseline with no optimization. Comparing it to the
    optimal portfolios reveals the potential benefit (or cost) of optimization.

    *Important: MPT expected returns are estimated from historical data, which is an imperfect predictor
    of future returns. Small changes in input estimates can produce dramatically different optimal weights.
    These results are for research purposes and do not constitute investment advice.*
    """)

    # ─── Save to Report ───────────────────────────────────────────────────────

    if st.button("Save Results to Report", key="port_save_report"):
        st.success("Portfolio results saved. Navigate to Research Reports to export.")

    st.markdown("<br>")
    st.markdown(f"""
    <div style='background:rgba(255,215,0,0.04);border:1px solid {GOLD}33;border-radius:6px;padding:12px 16px;color:#FFD70099;font-size:11px;'>
    ⚠ MPT assumes normally distributed returns, stable covariances, and rational investors. These assumptions
    are regularly violated in financial markets. Optimization results are highly sensitive to input parameters
    and should not be used as sole basis for investment decisions.
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center;padding:70px 0;'>
        <div style='font-size:52px;'>💼</div>
        <div style='color:#6B8CAE;font-size:14px;margin-top:14px;'>
            Enter ticker symbols above and click <strong style='color:#00D4FF;'>▶ Optimize</strong> to run portfolio analysis.
        </div>
        <div style='color:#1E2D4A;font-size:12px;margin-top:8px;'>
            Example: SPY, QQQ, GLD, TLT, VNQ
        </div>
    </div>
    """, unsafe_allow_html=True)
