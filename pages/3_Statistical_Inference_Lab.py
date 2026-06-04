"""
AlphaLab AI — Statistical Inference Lab
T-tests, confidence intervals, and hypothesis testing.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import fetch_simple_returns, DEFAULT_START, DEFAULT_END
from utils.statistics import one_sample_ttest, two_sample_ttest, compute_confidence_interval

st.set_page_config(page_title="Statistical Inference — AlphaLab AI", page_icon="🔬", layout="wide")

st.markdown("""
<style>
.stApp{background:#0A0E1A}[data-testid="stSidebar"]{background:#070B16!important;border-right:1px solid #1E2D4A}
.stButton>button{background:linear-gradient(135deg,#00D4FF18,#00D4FF0A);border:1px solid #00D4FF;color:#00D4FF;font-weight:600;border-radius:6px}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stSelectbox>div>div{background:#0F1628!important;border:1px solid #1E2D4A!important;color:#E8F4FD!important}
[data-testid="metric-container"]{background:#0F1628!important;border:1px solid #1E2D4A!important;border-radius:8px!important;padding:16px!important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#00D4FF!important;font-family:JetBrains Mono,monospace!important}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='padding:30px 0 10px 0;'>
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;'>MODULE 03</div>
    <div style='font-size:32px;font-weight:700;color:#00D4FF;font-family:JetBrains Mono,monospace;margin-top:6px;'>🔬 Statistical Inference Lab</div>
    <div style='color:#6B8CAE;font-size:14px;margin-top:8px;'>Hypothesis testing, t-tests, and confidence intervals on market return series.</div>
</div>
""", unsafe_allow_html=True)

st.divider()

NAVY = "#0A0E1A"; PANEL = "#0F1628"; BLUE = "#00D4FF"; GOLD = "#FFD700"; RED = "#FF4B6E"; GRID = "#1E2D4A"; TEXT = "#E8F4FD"

# ─── Test Selector ────────────────────────────────────────────────────────────

test_type = st.selectbox(
    "Select Test",
    ["One-Sample t-Test (test if mean ≠ μ₀)",
     "Two-Sample t-Test (compare two assets)",
     "Confidence Interval for Mean"],
)

st.markdown("<br>", unsafe_allow_html=True)

# ─── ONE SAMPLE ──────────────────────────────────────────────────────────────

if test_type.startswith("One"):
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.text_input("Ticker Symbol", value="SPY", key="inf_1s_tick")
        c1, c2 = st.columns(2)
        with c1: start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START), key="inf_1s_start")
        with c2: end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END),   key="inf_1s_end")
    with col2:
        popmean = st.number_input("Hypothesized Mean (daily return)", value=0.0, format="%.6f", key="inf_1s_mu")
        alpha   = st.selectbox("Significance Level (α)", [0.01, 0.05, 0.10], index=1, key="inf_1s_alpha")

    if st.button("▶ Run One-Sample t-Test", key="inf_1s_run"):
        with st.spinner(f"Downloading {ticker} returns..."):
            returns = fetch_simple_returns([ticker.upper()], str(start), str(end))

        if returns.empty:
            st.error("Could not load data.")
        else:
            s = returns[ticker.upper()]
            res = one_sample_ttest(s, popmean, alpha)

            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("N",           str(res["n"]))
            m2.metric("Sample Mean", f"{res['sample_mean']:.6f}")
            m3.metric("t-Statistic", f"{res['t_statistic']:.4f}")
            m4.metric("p-Value",     f"{res['p_value']:.6f}")
            m5.metric("Decision",    "Reject H₀" if res["reject_null"] else "Fail to Reject H₀")

            st.markdown("<br>", unsafe_allow_html=True)

            col_sum, col_viz = st.columns([1, 2])
            with col_sum:
                st.markdown(f"""
                <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:20px;'>
                    <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:10px;'>HYPOTHESIS</div>
                    <div style='color:{TEXT};font-size:13px;line-height:2;'>
                    <strong>H₀:</strong> μ = {popmean:.6f}<br>
                    <strong>H₁:</strong> μ ≠ {popmean:.6f}<br>
                    <strong>α:</strong> {alpha}<br>
                    <strong>CI ({(1-alpha):.0%}):</strong> [{res["ci_lower"]:.6f}, {res["ci_upper"]:.6f}]
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_viz:
                # t-distribution plot
                df_t = res["n"] - 1
                x_t  = np.linspace(-5, 5, 500)
                y_t  = stats.t.pdf(x_t, df_t)
                t_stat = res["t_statistic"]
                crit_val = stats.t.ppf(1 - alpha / 2, df_t)

                fig = go.Figure()
                # Full curve
                fig.add_trace(go.Scatter(x=x_t, y=y_t, mode="lines",
                    line=dict(color=BLUE, width=2), name="t-distribution"))
                # Left rejection region
                mask_l = x_t <= -crit_val
                fig.add_trace(go.Scatter(x=x_t[mask_l], y=y_t[mask_l], fill="tozeroy",
                    fillcolor="rgba(255,75,110,0.20)", line=dict(width=0), name="Rejection Region"))
                # Right rejection region
                mask_r = x_t >= crit_val
                fig.add_trace(go.Scatter(x=x_t[mask_r], y=y_t[mask_r], fill="tozeroy",
                    fillcolor="rgba(255,75,110,0.20)", line=dict(width=0), showlegend=False))
                # t-stat
                fig.add_vline(x=t_stat, line_color=GOLD, line_dash="dash",
                    annotation_text=f"t={t_stat:.3f}", annotation_font_color=GOLD)
                fig.update_layout(
                    paper_bgcolor=NAVY, plot_bgcolor=PANEL,
                    font=dict(color=TEXT, family="monospace"),
                    xaxis=dict(title="t-value", gridcolor=GRID),
                    yaxis=dict(title="Density", gridcolor=GRID),
                    title=dict(text="t-Distribution with Rejection Regions", font=dict(color=BLUE, size=14)),
                    height=320, margin=dict(l=40, r=20, t=50, b=40),
                    legend=dict(bgcolor=PANEL, bordercolor=GRID),
                )
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.markdown("**Interpretation**")
            st.markdown(res["interpretation"])

# ─── TWO SAMPLE ──────────────────────────────────────────────────────────────

elif test_type.startswith("Two"):
    col1, col2 = st.columns(2)
    with col1:
        ticker_a = st.text_input("Asset A", value="SPY",  key="inf_2s_a")
        ticker_b = st.text_input("Asset B", value="QQQ",  key="inf_2s_b")
    with col2:
        start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START), key="inf_2s_start")
        end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END),   key="inf_2s_end")
        equal_var = st.checkbox("Assume equal variances (Student's)", value=False, key="inf_2s_eqvar")
        alpha     = st.selectbox("α", [0.01, 0.05, 0.10], index=1, key="inf_2s_alpha")

    if st.button("▶ Run Two-Sample t-Test", key="inf_2s_run"):
        with st.spinner("Downloading data..."):
            all_tickers = [ticker_a.upper(), ticker_b.upper()]
            returns = fetch_simple_returns(all_tickers, str(start), str(end))

        if returns.empty:
            st.error("Could not load data.")
        else:
            valid = [t for t in all_tickers if t in returns.columns]
            if len(valid) < 2:
                st.error("At least two valid tickers required.")
            else:
                a_ret = returns[valid[0]]
                b_ret = returns[valid[1]]
                res   = two_sample_ttest(a_ret, b_ret, equal_var, alpha)

                st.markdown("<br>", unsafe_allow_html=True)
                m1, m2, m3, m4, m5, m6 = st.columns(6)
                m1.metric(f"Mean {valid[0]}",  f"{res['mean_a']:.6f}")
                m2.metric(f"Mean {valid[1]}",  f"{res['mean_b']:.6f}")
                m3.metric("Difference",        f"{res['mean_difference']:.6f}")
                m4.metric("t-Statistic",       f"{res['t_statistic']:.4f}")
                m5.metric("p-Value",           f"{res['p_value']:.6f}")
                m6.metric("Decision",          "Reject H₀" if res["reject_null"] else "Fail to Reject")

                st.markdown("<br>")
                st.markdown(f"""
                <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:18px;'>
                    <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:10px;'>HYPOTHESIS</div>
                    <div style='color:{TEXT};font-size:13px;line-height:2;'>
                    <strong>H₀:</strong> μ_{valid[0]} = μ_{valid[1]}<br>
                    <strong>H₁:</strong> μ_{valid[0]} ≠ μ_{valid[1]}<br>
                    <strong>Test:</strong> {res["test"]}<br>
                    <strong>N_{valid[0]}:</strong> {res["n_a"]} &nbsp;|&nbsp; <strong>N_{valid[1]}:</strong> {res["n_b"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("**Interpretation**")
                st.markdown(res["interpretation"])

# ─── CONFIDENCE INTERVAL ─────────────────────────────────────────────────────

else:
    col1, col2 = st.columns([2, 1])
    with col1:
        ticker = st.text_input("Ticker", value="SPY", key="inf_ci_tick")
        c1, c2 = st.columns(2)
        with c1: start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START), key="inf_ci_start")
        with c2: end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END),   key="inf_ci_end")
    with col2:
        confidence = st.selectbox("Confidence Level", [0.90, 0.95, 0.99], index=1, key="inf_ci_conf")

    if st.button("▶ Compute Confidence Interval", key="inf_ci_run"):
        with st.spinner("Loading data..."):
            returns = fetch_simple_returns([ticker.upper()], str(start), str(end))

        if returns.empty:
            st.error("Could not load data.")
        else:
            s   = returns[ticker.upper()]
            res = compute_confidence_interval(s, confidence)

            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("N",               str(res["n"]))
            m2.metric("Sample Mean",     f"{res['mean']:.6f}")
            m3.metric("Std Dev",         f"{res['std']:.6f}")
            m4.metric("CI Lower",        f"{res['ci_lower']:.6f}")
            m5.metric("CI Upper",        f"{res['ci_upper']:.6f}")

            st.markdown("<br>")
            # Visualize CI
            x_range = np.linspace(res["mean"] - 5 * res["se"], res["mean"] + 5 * res["se"], 500)
            y_pdf   = stats.t.pdf(x_range, df=res["n"] - 1, loc=res["mean"], scale=res["se"])

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_range, y=y_pdf, mode="lines",
                line=dict(color=BLUE, width=2), name="Sampling Distribution"))
            mask_ci = (x_range >= res["ci_lower"]) & (x_range <= res["ci_upper"])
            fig.add_trace(go.Scatter(x=x_range[mask_ci], y=y_pdf[mask_ci], fill="tozeroy",
                fillcolor="rgba(0,212,255,0.15)", line=dict(width=0),
                name=f"{confidence:.0%} CI"))
            fig.add_vline(x=res["mean"], line_color=GOLD, line_dash="dash",
                annotation_text=f"Mean={res['mean']:.5f}", annotation_font_color=GOLD)
            fig.add_vline(x=res["ci_lower"], line_color=RED, line_width=1, line_dash="dot")
            fig.add_vline(x=res["ci_upper"], line_color=RED, line_width=1, line_dash="dot")
            fig.update_layout(
                paper_bgcolor=NAVY, plot_bgcolor=PANEL,
                font=dict(color=TEXT, family="monospace"),
                xaxis=dict(title="Mean Daily Return", gridcolor=GRID),
                yaxis=dict(title="Density", gridcolor=GRID),
                title=dict(text=f"{confidence:.0%} Confidence Interval for {ticker.upper()} Daily Mean Return",
                           font=dict(color=BLUE, size=14)),
                height=380, margin=dict(l=40, r=20, t=50, b=40),
                legend=dict(bgcolor=PANEL, bordercolor=GRID),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
            **Interpretation:** We are **{confidence:.0%}** confident that the true population mean daily return
            of {ticker.upper()} lies between **{res['ci_lower']:.6f}** and **{res['ci_upper']:.6f}**,
            based on {res['n']} observations. The margin of error is ±{res['margin_of_error']:.6f}.

            *Note: This interval is constructed under the assumption of approximately normally distributed returns
            (or large sample CLT). The t-distribution accounts for estimation uncertainty in the standard deviation.*
            """)

# ─── Disclaimer ──────────────────────────────────────────────────────────────

st.markdown("<br>")
st.markdown("""
<div style='background:rgba(255,215,0,0.04);border:1px solid #FFD70033;border-radius:6px;padding:12px 16px;color:#FFD70099;font-size:11px;'>
⚠ Statistical significance ≠ practical significance. P-values are sensitive to sample size.
Always consider effect sizes and economic meaningfulness alongside statistical test results.
</div>
""", unsafe_allow_html=True)
