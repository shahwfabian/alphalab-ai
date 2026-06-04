"""
AlphaLab AI — Probability Lab
Historical return distribution, tail risk, drawdown probability, VaR/CVaR.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import (
    fetch_simple_returns, fetch_prices, DEFAULT_START, DEFAULT_END,
    annualized_return, annualized_volatility,
)
from utils.statistics import (
    return_distribution_stats, prob_drawdown_parametric,
    historical_var, historical_cvar,
)
from utils.charts import (
    returns_histogram, cumulative_return_chart,
    probability_density_chart, drawdown_chart,
)

st.set_page_config(page_title="Probability Lab — AlphaLab AI", page_icon="🎲", layout="wide")

st.markdown("""
<style>
.stApp{background:#0A0E1A}
[data-testid="stSidebar"]{background:#070B16!important;border-right:1px solid #1E2D4A}
.stButton>button{background:linear-gradient(135deg,#00D4FF18,#00D4FF0A);border:1px solid #00D4FF;color:#00D4FF;font-weight:600;border-radius:6px}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stSelectbox>div>div{background:#0F1628!important;border:1px solid #1E2D4A!important;color:#E8F4FD!important}
[data-testid="metric-container"]{background:#0F1628!important;border:1px solid #1E2D4A!important;border-radius:8px!important;padding:16px!important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#00D4FF!important;font-family:JetBrains Mono,monospace!important}
.stTabs [data-baseweb="tab-list"]{background:#0F1628;border-radius:8px;gap:4px}
.stTabs [data-baseweb="tab"]{color:#6B8CAE;padding:8px 20px;border-radius:6px}
.stTabs [aria-selected="true"]{background:rgba(0,212,255,0.12)!important;color:#00D4FF!important}
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding:30px 0 10px 0;'>
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;'>MODULE 04</div>
    <div style='font-size:32px;font-weight:700;color:#00D4FF;font-family:JetBrains Mono,monospace;margin-top:6px;'>🎲 Probability Lab</div>
    <div style='color:#6B8CAE;font-size:14px;margin-top:8px;'>
        Analyze return distributions, estimate tail risk, model drawdown probabilities, and compute VaR / CVaR.
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

NAVY = "#0A0E1A"; PANEL = "#0F1628"; BLUE = "#00D4FF"; GOLD = "#FFD700"
RED = "#FF4B6E"; CYAN = "#00FFD4"; GRID = "#1E2D4A"; TEXT = "#E8F4FD"

# ─── Configuration Panel ─────────────────────────────────────────────────────

with st.container():
    col_cfg, col_run = st.columns([4, 1])

    with col_cfg:
        c1, c2, c3 = st.columns(3)
        with c1:
            ticker = st.text_input("Ticker Symbol", value="SPY", key="prob_tick")
        with c2:
            start = st.date_input("Start Date", value=pd.to_datetime(DEFAULT_START), key="prob_start")
        with c3:
            end   = st.date_input("End Date",   value=pd.to_datetime(DEFAULT_END),   key="prob_end")

        c4, c5, c6 = st.columns(3)
        with c4:
            threshold_pct = st.number_input(
                "Drawdown Threshold (%)", value=-5.0, min_value=-50.0, max_value=-0.1,
                step=0.5, key="prob_thresh",
                help="e.g. -5.0 = probability of losing more than 5%"
            )
        with c5:
            horizon = st.number_input(
                "Horizon (Trading Days)", value=21, min_value=1, max_value=252,
                key="prob_horizon",
                help="Number of trading days forward (21 ≈ 1 month, 63 ≈ 1 quarter)"
            )
        with c6:
            var_conf = st.selectbox("VaR Confidence Level", [0.90, 0.95, 0.99], index=1, key="prob_var_conf")

    with col_run:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        run_btn = st.button("▶ Run Analysis", use_container_width=True, key="prob_run")

# ─── Analysis Execution ───────────────────────────────────────────────────────

if run_btn:
    threshold = threshold_pct / 100.0

    with st.spinner(f"Loading {ticker.upper()} data..."):
        returns = fetch_simple_returns([ticker.upper()], str(start), str(end))
        prices  = fetch_prices([ticker.upper()], str(start), str(end))

    if returns.empty or ticker.upper() not in returns.columns:
        st.error(f"Could not load data for {ticker.upper()}. Check symbol and date range.")
        st.stop()

    ret_series   = returns[ticker.upper()].dropna()
    price_series = prices[ticker.upper()].dropna()

    # --- Core statistics ---
    dist_stats   = return_distribution_stats(ret_series)
    prob_result  = prob_drawdown_parametric(ret_series, threshold, horizon)
    var_1d       = historical_var(ret_series, var_conf)
    cvar_1d      = historical_cvar(ret_series, var_conf)
    prob_positive = float((ret_series > 0).mean())
    ann_ret      = annualized_return(ret_series)
    ann_vol      = annualized_volatility(ret_series)
    sharpe       = ann_ret / ann_vol if ann_vol > 0 else 0.0
    rf           = st.session_state.get("risk_free_rate", 0.05)
    sharpe_rf    = (ann_ret - rf) / ann_vol if ann_vol > 0 else 0.0

    # ─── KPI Row ─────────────────────────────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;margin-bottom:16px;'>
    KEY STATISTICS — {ticker.upper()} ({str(start)} → {str(end)})
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Ann. Return",   f"{ann_ret:.2%}")
    k2.metric("Ann. Volatility",f"{ann_vol:.2%}")
    k3.metric("Sharpe Ratio",  f"{sharpe_rf:.3f}", help="(Return - Risk-Free Rate) / Volatility")
    k4.metric(f"{var_conf:.0%} VaR (1-Day)", f"{var_1d:.2%}",
              help="Worst expected 1-day loss at this confidence level")
    k5.metric(f"{var_conf:.0%} CVaR",       f"{cvar_1d:.2%}",
              help="Expected loss given that loss exceeds VaR (Expected Shortfall)")
    k6.metric("P(Positive Day)", f"{prob_positive:.1%}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Drawdown probability callout ────────────────────────────────────────

    prob_val = prob_result["probability"]
    color_accent = RED if prob_val > 0.15 else GOLD if prob_val > 0.05 else CYAN
    st.markdown(f"""
    <div style='background:rgba(0,0,0,0.3);border:1px solid {color_accent}44;
                border-left:4px solid {color_accent};border-radius:8px;padding:20px 24px;margin-bottom:24px;'>
        <div style='color:{color_accent};font-family:JetBrains Mono,monospace;font-size:11px;
                    letter-spacing:3px;margin-bottom:8px;'>DRAWDOWN PROBABILITY ESTIMATE</div>
        <div style='font-size:36px;font-weight:700;color:{color_accent};font-family:JetBrains Mono,monospace;'>
            {prob_val:.2%}
        </div>
        <div style='color:{TEXT};font-size:14px;margin-top:8px;'>
            Probability of {ticker.upper()} losing more than
            <strong>{abs(threshold_pct):.1f}%</strong>
            over the next <strong>{horizon} trading day{"s" if horizon > 1 else ""}</strong>
        </div>
        <div style='color:#6B8CAE;font-size:12px;margin-top:8px;'>
            Based on Normal approximation · μ = {prob_result["mu_horizon"]:.4f} · σ = {prob_result["sigma_horizon"]:.4f} · Z = {prob_result["z_score"]:.3f}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Tabs for Visualizations ─────────────────────────────────────────────

    tab1, tab2, tab3, tab4 = st.tabs([
        "Return Distribution", "Probability Density", "Drawdown History", "Distribution Stats"
    ])

    with tab1:
        fig_hist = returns_histogram(ret_series, ticker.upper(), bins=70)
        st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown(f"""
        <div style='background:{PANEL};border:1px solid {GRID};border-radius:6px;padding:14px;font-size:13px;color:#6B8CAE;'>
        The histogram displays the empirical distribution of daily returns.
        The dashed gold line shows the fitted Normal distribution.
        The red dotted line marks the historical {var_conf:.0%} Value-at-Risk threshold ({var_1d:.2%}).
        Fat tails vs the Normal fit indicate leptokurtosis (excess kurtosis = {dist_stats["excess_kurtosis"]:.2f}).
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        fig_density = probability_density_chart(ret_series, ticker.upper(), threshold)
        st.plotly_chart(fig_density, use_container_width=True)
        st.markdown(f"""
        <div style='background:{PANEL};border:1px solid {GRID};border-radius:6px;padding:14px;font-size:13px;color:#6B8CAE;'>
        KDE (kernel density estimate) vs Normal fit. The red shaded area shows the probability mass
        below the {threshold_pct:.1f}% threshold. Divergence between KDE and Normal in the tails
        illustrates why Normal-based tail risk estimates may be inadequate for financial returns.
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        fig_dd = drawdown_chart(price_series, f"{ticker.upper()} Historical Drawdown (%)")
        st.plotly_chart(fig_dd, use_container_width=True)
        max_dd = ((price_series / price_series.cummax()) - 1).min()
        st.markdown(f"""
        <div style='background:{PANEL};border:1px solid {GRID};border-radius:6px;padding:14px;font-size:13px;color:#6B8CAE;'>
        Maximum historical drawdown: <span style='color:{RED};font-weight:700;'>{max_dd:.2%}</span>
        over the selected period. This represents the worst peak-to-trough decline recorded.
        Historical drawdowns are descriptive only and do not imply future outcomes.
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        # Distribution statistics table
        st.markdown("**Full Distribution Statistics**")
        stat_items = {
            "Observations":         dist_stats["count"],
            "Mean Daily Return":    f"{dist_stats['mean_daily']:.6f}",
            "Daily Std Dev":        f"{dist_stats['std_daily']:.6f}",
            "Annualized Return":    f"{dist_stats['mean_annual']:.4f}",
            "Annualized Volatility":f"{dist_stats['std_annual']:.4f}",
            "Skewness":             f"{dist_stats['skewness']:.4f}",
            "Excess Kurtosis":      f"{dist_stats['excess_kurtosis']:.4f}",
            "Min Return":           f"{dist_stats['min']:.4f}",
            "Max Return":           f"{dist_stats['max']:.4f}",
            "5th Percentile":       f"{dist_stats['percentile_5']:.4f}",
            "95th Percentile":      f"{dist_stats['percentile_95']:.4f}",
            "Jarque-Bera Stat":     f"{dist_stats['jarque_bera_stat']:.4f}",
            "Jarque-Bera p-value":  f"{dist_stats['jarque_bera_pvalue']:.6f}",
            "Approx. Normal?":      "Yes ✓" if dist_stats["is_normal"] else "No ✗",
        }
        stat_df = pd.DataFrame(stat_items.items(), columns=["Statistic", "Value"])
        st.dataframe(stat_df, use_container_width=True, hide_index=True)

        jb_note = (
            "The Jarque-Bera test fails to reject normality (p > 0.05), "
            "suggesting approximate normality for this return series."
        ) if dist_stats["is_normal"] else (
            f"The Jarque-Bera test rejects normality (p = {dist_stats['jarque_bera_pvalue']:.4f}). "
            "Returns exhibit significant skewness or excess kurtosis. "
            "Normal-based probability estimates may understate tail risk."
        )
        st.markdown(f"**Normality Test Result:** {jb_note}")

    # ─── VaR Summary Card ────────────────────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;margin-bottom:16px;'>
    RISK METRICS SUMMARY
    </div>
    """, unsafe_allow_html=True)

    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"""
        <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:18px;'>
            <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:10px;'>VALUE AT RISK</div>
            <div style='color:{TEXT};font-size:13px;line-height:1.9;'>
                <span style='color:#6B8CAE;'>90% VaR (1-Day):</span> {historical_var(ret_series,0.90):.2%}<br>
                <span style='color:#6B8CAE;'>95% VaR (1-Day):</span> {historical_var(ret_series,0.95):.2%}<br>
                <span style='color:#6B8CAE;'>99% VaR (1-Day):</span> {historical_var(ret_series,0.99):.2%}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        st.markdown(f"""
        <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:18px;'>
            <div style='color:{CYAN};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:10px;'>EXPECTED SHORTFALL (CVAR)</div>
            <div style='color:{TEXT};font-size:13px;line-height:1.9;'>
                <span style='color:#6B8CAE;'>90% CVaR (1-Day):</span> {historical_cvar(ret_series,0.90):.2%}<br>
                <span style='color:#6B8CAE;'>95% CVaR (1-Day):</span> {historical_cvar(ret_series,0.95):.2%}<br>
                <span style='color:#6B8CAE;'>99% CVaR (1-Day):</span> {historical_cvar(ret_series,0.99):.2%}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with r3:
        st.markdown(f"""
        <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:18px;'>
            <div style='color:{GOLD};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:10px;'>RETURN PROBABILITIES</div>
            <div style='color:{TEXT};font-size:13px;line-height:1.9;'>
                <span style='color:#6B8CAE;'>P(return > 0%):</span>  {float((ret_series > 0.00).mean()):.1%}<br>
                <span style='color:#6B8CAE;'>P(return > 0.5%):</span>{float((ret_series > 0.005).mean()):.1%}<br>
                <span style='color:#6B8CAE;'>P(return > 1%):</span>  {float((ret_series > 0.01).mean()):.1%}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── Methodological note ─────────────────────────────────────────────────

    st.markdown("<br>")
    st.markdown(f"""
    <div style='background:rgba(255,215,0,0.04);border:1px solid {GOLD}33;border-radius:6px;padding:14px 18px;'>
        <div style='color:{GOLD};font-size:12px;line-height:1.8;'>
        ⚠ <strong>Methodology Note:</strong> {prob_result["note"]}<br>
        Historical VaR uses the empirical return distribution without parametric assumptions.
        CVaR (Expected Shortfall) is a more coherent risk measure than VaR alone.
        All estimates are based on historical data and carry significant estimation uncertainty.
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center;padding:70px 0;'>
        <div style='font-size:52px;'>🎲</div>
        <div style='color:#6B8CAE;font-size:14px;margin-top:14px;'>
            Configure your analysis parameters above and click <strong style='color:#00D4FF;'>▶ Run Analysis</strong>
        </div>
        <div style='color:#1E2D4A;font-size:12px;margin-top:8px;'>
            Example: SPY · Threshold -5% · 21-day horizon
        </div>
    </div>
    """, unsafe_allow_html=True)
