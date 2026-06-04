"""AlphaLab AI — Portfolio Optimization"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import inject_css, page_header, info_box
from utils.data_loader import fetch_simple_returns, DEFAULT_START, DEFAULT_END
from utils.portfolio import (optimize_max_sharpe, optimize_min_variance, equal_weight_portfolio,
                              generate_efficient_frontier, generate_random_portfolios, build_portfolio_summary)
from utils.charts import efficient_frontier_chart, portfolio_weights_bar, cumulative_return_chart

st.set_page_config(page_title="Portfolio Optimization — AlphaLab AI", page_icon="⬡", layout="wide")
inject_css()

page_header("Portfolio Optimization", "Modern Portfolio Theory — Maximum Sharpe, Minimum Variance, and Efficient Frontier.")

# ── Config ────────────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    tickers_raw  = st.text_input("Tickers (comma-separated, min 2)", value="SPY, QQQ, GLD, TLT, VNQ")
    rf_input     = st.number_input("Risk-free rate (%)", value=float(st.session_state.get("risk_free_rate", 0.05)) * 100, min_value=0.0, max_value=20.0, step=0.1)
with c2:
    start        = st.date_input("Start", value=pd.to_datetime(DEFAULT_START))
    end          = st.date_input("End",   value=pd.to_datetime(DEFAULT_END))
    allow_short  = st.checkbox("Allow short selling", value=False)

run_btn = st.button("Optimize", type="primary")

if run_btn:
    tickers  = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
    rf       = rf_input / 100.0
    w_bounds = (-1.0, 1.0) if allow_short else (0.0, 1.0)

    if len(tickers) < 2:
        st.error("Enter at least 2 ticker symbols.")
        st.stop()

    with st.spinner("Downloading data..."):
        rets = fetch_simple_returns(tickers, str(start), str(end))

    valid = [t for t in tickers if t in rets.columns]
    if len(valid) < 2:
        st.error(f"Could not load enough data. Valid tickers: {valid}")
        st.stop()

    rets = rets[valid].dropna()
    mu   = rets.mean().values
    cov  = rets.cov().values

    with st.spinner("Running optimization..."):
        ms_port  = optimize_max_sharpe(mu, cov, rf, w_bounds)
        mv_port  = optimize_min_variance(mu, cov, w_bounds)
        eq_port  = equal_weight_portfolio(mu, cov, rf)
        frontier = generate_efficient_frontier(mu, cov, rf, n_points=100, weight_bounds=w_bounds)
        random   = generate_random_portfolios(mu, cov, rf, n=3000)

    st.session_state["last_portfolio_results"] = {
        "tickers": valid, "max_sharpe": ms_port, "min_var": mv_port,
        "eq_weight": eq_port, "frontier": frontier, "returns": rets, "rf": rf,
        "start": str(start), "end": str(end),
    }

    st.divider()

    # Portfolio comparison
    col1, col2, col3 = st.columns(3)
    for col, label, port in [(col1, "Max Sharpe", ms_port), (col2, "Min Variance", mv_port), (col3, "Equal Weight", eq_port)]:
        with col:
            col.metric(f"{label} — Return",     f"{port['return']:.2%}")
            col.metric(f"{label} — Volatility", f"{port['volatility']:.2%}")
            col.metric(f"{label} — Sharpe",     f"{port['sharpe']:.3f}")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Efficient Frontier", "Weights", "Returns", "Covariance"])

    with tab1:
        ports_chart = {
            "Max Sharpe":   {"return": ms_port["return"], "volatility": ms_port["volatility"]},
            "Min Variance": {"return": mv_port["return"], "volatility": mv_port["volatility"]},
            "Equal Weight": {"return": eq_port["return"], "volatility": eq_port["volatility"]},
        }
        st.plotly_chart(efficient_frontier_chart(frontier, random, ports_chart, valid), use_container_width=True)

    with tab2:
        wc1, wc2, wc3 = st.columns(3)
        with wc1: st.plotly_chart(portfolio_weights_bar(valid, ms_port["weights"], "Max Sharpe"),   use_container_width=True)
        with wc2: st.plotly_chart(portfolio_weights_bar(valid, mv_port["weights"], "Min Variance"), use_container_width=True)
        with wc3: st.plotly_chart(portfolio_weights_bar(valid, eq_port["weights"], "Equal Weight"), use_container_width=True)

        weight_df = pd.DataFrame({
            "Ticker":           valid,
            "Max Sharpe (%)":   (ms_port["weights"] * 100).round(2),
            "Min Variance (%)": (mv_port["weights"] * 100).round(2),
            "Equal Weight (%)": (eq_port["weights"] * 100).round(2),
        })
        st.dataframe(weight_df, use_container_width=True, hide_index=True)

    with tab3:
        port_rets = pd.DataFrame(index=rets.index)
        port_rets["Max Sharpe"]   = rets.values @ ms_port["weights"]
        port_rets["Min Variance"] = rets.values @ mv_port["weights"]
        port_rets["Equal Weight"] = rets.values @ eq_port["weights"]
        st.plotly_chart(cumulative_return_chart(port_rets, "Cumulative Returns by Strategy"), use_container_width=True)
        st.dataframe(build_portfolio_summary(valid, ms_port["weights"], mu, cov, rf), use_container_width=True, hide_index=True)

    with tab4:
        cov_df = pd.DataFrame(cov * 252, index=valid, columns=valid)
        st.dataframe(cov_df.style.format("{:.6f}"), use_container_width=True)

    dominant      = valid[int(np.argmax(ms_port["weights"]))]
    dominant_wt   = ms_port["weights"].max()
    st.divider()
    st.markdown(f"""
    The **Maximum Sharpe portfolio** achieves an estimated annualized return of **{ms_port['return']:.2%}**
    with volatility **{ms_port['volatility']:.2%}** and Sharpe ratio **{ms_port['sharpe']:.3f}** (RF = {rf*100:.2f}%).
    Largest allocation: **{dominant}** at **{dominant_wt:.1%}**.
    """)
    info_box("MPT is highly sensitive to input estimates. Historical covariance and expected returns are imperfect predictors of future behavior. Results are research-oriented and not investment advice.", "warning")

else:
    st.markdown("""
    <div style="text-align:center; padding:4rem 0; color:#2a2a2a;">
        <div style="font-size:2rem; margin-bottom:0.75rem;">⬡</div>
        <div style="font-size:0.875rem;">Enter tickers above and click Optimize.</div>
    </div>
    """, unsafe_allow_html=True)
