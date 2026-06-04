"""AlphaLab AI — Probability Lab"""

import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import inject_css, page_header, info_box
from utils.data_loader import fetch_simple_returns, fetch_prices, DEFAULT_START, DEFAULT_END, annualized_return, annualized_volatility
from utils.statistics import return_distribution_stats, prob_drawdown_parametric, historical_var, historical_cvar
from utils.charts import returns_histogram, probability_density_chart, drawdown_chart

st.set_page_config(page_title="Probability Lab — AlphaLab AI", page_icon="⬡", layout="wide")
inject_css()

page_header("Probability Lab", "Return distributions, tail risk, drawdown probability, and VaR / CVaR.")

# ── Config ────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    ticker       = st.text_input("Ticker", value="SPY")
    start        = st.date_input("Start", value=pd.to_datetime(DEFAULT_START))
    end          = st.date_input("End",   value=pd.to_datetime(DEFAULT_END))
with c2:
    threshold_pct= st.number_input("Drawdown threshold (%)", value=-5.0, min_value=-50.0, max_value=-0.1, step=0.5)
    horizon      = st.number_input("Horizon (trading days)", value=21, min_value=1, max_value=252)
with c3:
    var_conf     = st.selectbox("VaR confidence level", [0.90, 0.95, 0.99], index=1)

run_btn = st.button("Run Analysis", type="primary")

if run_btn:
    threshold = threshold_pct / 100.0
    with st.spinner(f"Loading {ticker.upper()}..."):
        rets   = fetch_simple_returns([ticker.upper()], str(start), str(end))
        prices = fetch_prices([ticker.upper()], str(start), str(end))

    if rets.empty or ticker.upper() not in rets.columns:
        st.error("Could not load data. Check the ticker symbol.")
        st.stop()

    s  = rets[ticker.upper()].dropna()
    p  = prices[ticker.upper()].dropna()

    ds         = return_distribution_stats(s)
    prob_res   = prob_drawdown_parametric(s, threshold, horizon)
    var_1d     = historical_var(s, var_conf)
    cvar_1d    = historical_cvar(s, var_conf)
    ann_ret    = annualized_return(s)
    ann_vol    = annualized_volatility(s)
    rf         = st.session_state.get("risk_free_rate", 0.05)
    sharpe     = (ann_ret - rf) / ann_vol if ann_vol > 0 else 0.0

    st.divider()

    # KPIs
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Ann. Return",      f"{ann_ret:.2%}")
    k2.metric("Ann. Volatility",  f"{ann_vol:.2%}")
    k3.metric("Sharpe Ratio",     f"{sharpe:.3f}")
    k4.metric(f"{var_conf:.0%} VaR",  f"{var_1d:.2%}")
    k5.metric(f"{var_conf:.0%} CVaR", f"{cvar_1d:.2%}")
    k6.metric("P(Positive day)",  f"{float((s>0).mean()):.1%}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Drawdown probability highlight
    pv    = prob_res["probability"]
    color = "#ef4444" if pv > 0.15 else "#f59e0b" if pv > 0.05 else "#22c55e"
    st.markdown(f"""
    <div style="background:#161616; border:1px solid #1f1f1f; border-left:3px solid {color};
                border-radius:0 10px 10px 0; padding:1.25rem 1.5rem; margin-bottom:1.5rem;">
        <div style="font-size:0.7rem; color:#444; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.4rem;">
            Drawdown probability estimate
        </div>
        <div style="font-size:2rem; font-weight:600; color:{color}; font-family:'Inter',sans-serif;">{pv:.2%}</div>
        <div style="font-size:0.825rem; color:#666; margin-top:0.3rem;">
            P({ticker.upper()} loses more than {abs(threshold_pct):.1f}% over {horizon} trading day{'s' if horizon>1 else ''}) · Normal approximation
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Charts
    tab1, tab2, tab3, tab4 = st.tabs(["Distribution", "Density", "Drawdown", "Statistics"])

    with tab1:
        st.plotly_chart(returns_histogram(s, ticker.upper(), bins=70), use_container_width=True)
    with tab2:
        st.plotly_chart(probability_density_chart(s, ticker.upper(), threshold), use_container_width=True)
    with tab3:
        st.plotly_chart(drawdown_chart(p, f"{ticker.upper()} Drawdown"), use_container_width=True)
        max_dd = ((p / p.cummax()) - 1).min()
        st.markdown(f"Max historical drawdown: **{max_dd:.2%}**")
    with tab4:
        stats_items = {
            "Observations": ds["count"], "Mean daily": f"{ds['mean_daily']:.6f}",
            "Std daily": f"{ds['std_daily']:.6f}", "Ann. return": f"{ds['mean_annual']:.4f}",
            "Ann. volatility": f"{ds['std_annual']:.4f}", "Skewness": f"{ds['skewness']:.4f}",
            "Excess kurtosis": f"{ds['excess_kurtosis']:.4f}", "5th pct": f"{ds['percentile_5']:.4f}",
            "95th pct": f"{ds['percentile_95']:.4f}", "Jarque-Bera p": f"{ds['jarque_bera_pvalue']:.6f}",
            "Normal?": "Yes" if ds["is_normal"] else "No",
        }
        st.dataframe(
            pd.DataFrame(stats_items.items(), columns=["Statistic", "Value"]),
            use_container_width=True, hide_index=True
        )

    info_box("Probability estimates assume i.i.d. normally distributed returns — an approximation. Financial returns exhibit fat tails, autocorrelation, and volatility clustering. Treat all estimates as indicative.", "warning")

else:
    st.markdown("""
    <div style="text-align:center; padding:4rem 0; color:#2a2a2a;">
        <div style="font-size:2rem; margin-bottom:0.75rem;">⬡</div>
        <div style="font-size:0.875rem;">Configure parameters above and click Run Analysis.</div>
    </div>
    """, unsafe_allow_html=True)
