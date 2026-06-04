"""AlphaLab AI — Statistical Inference Lab"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import inject_css, page_header, info_box
from utils.data_loader import fetch_simple_returns, DEFAULT_START, DEFAULT_END
from utils.statistics import one_sample_ttest, two_sample_ttest, compute_confidence_interval

st.set_page_config(page_title="Statistical Inference — AlphaLab AI", page_icon="⬡", layout="wide")
inject_css()

page_header("Statistical Inference", "Hypothesis testing, t-tests, and confidence intervals.")

BG    = "#0d0d0d"
SURF  = "#161616"
GRID  = "#1f1f1f"
TEXT  = "#e5e5e5"
BLUE  = "#5865f2"
GREEN = "#22c55e"
RED   = "#ef4444"
GOLD  = "#f59e0b"

test_type = st.selectbox("Test", [
    "One-sample t-test",
    "Two-sample t-test",
    "Confidence interval for mean",
])

st.markdown("<br>", unsafe_allow_html=True)

# ── ONE SAMPLE ────────────────────────────────────────────────────────────────
if test_type == "One-sample t-test":
    c1, c2 = st.columns([3, 1])
    with c1:
        ticker = st.text_input("Ticker", value="SPY")
        cc1, cc2 = st.columns(2)
        with cc1: start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START))
        with cc2: end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END))
    with c2:
        popmean = st.number_input("Hypothesized mean (daily return)", value=0.0, format="%.6f")
        alpha   = st.selectbox("Significance level α", [0.01, 0.05, 0.10], index=1)

    if st.button("Run Test", type="primary"):
        with st.spinner("Loading data..."):
            rets = fetch_simple_returns([ticker.upper()], str(start), str(end))
        if rets.empty or ticker.upper() not in rets.columns:
            st.error("Could not load data.")
        else:
            res = one_sample_ttest(rets[ticker.upper()], popmean, alpha)
            st.divider()
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("N",           str(res["n"]))
            m2.metric("Sample mean", f"{res['sample_mean']:.6f}")
            m3.metric("t-statistic", f"{res['t_statistic']:.4f}")
            m4.metric("p-value",     f"{res['p_value']:.6f}")
            m5.metric("Decision",    "Reject H₀" if res["reject_null"] else "Fail to reject H₀")

            st.markdown("<br>", unsafe_allow_html=True)
            col_sum, col_viz = st.columns([1, 2])

            with col_sum:
                st.markdown(f"""
                <div style="background:{SURF}; border:1px solid {GRID}; border-radius:10px; padding:1.25rem; font-size:0.875rem; line-height:2;">
                    <b style="color:{TEXT};">H₀:</b> <span style="color:#888;">μ = {popmean:.6f}</span><br>
                    <b style="color:{TEXT};">H₁:</b> <span style="color:#888;">μ ≠ {popmean:.6f}</span><br>
                    <b style="color:{TEXT};">α:</b>  <span style="color:#888;">{alpha}</span><br>
                    <b style="color:{TEXT};">CI:</b> <span style="color:#888;">[{res['ci_lower']:.6f}, {res['ci_upper']:.6f}]</span>
                </div>
                """, unsafe_allow_html=True)

            with col_viz:
                df_t = res["n"] - 1
                x_t  = np.linspace(-5, 5, 500)
                y_t  = stats.t.pdf(x_t, df_t)
                crit = stats.t.ppf(1 - alpha / 2, df_t)
                t_s  = res["t_statistic"]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_t, y=y_t, mode="lines", line=dict(color=BLUE, width=2), name="t-dist"))
                for mask in [x_t <= -crit, x_t >= crit]:
                    fig.add_trace(go.Scatter(x=x_t[mask], y=y_t[mask], fill="tozeroy", fillcolor="rgba(239,68,68,0.15)", line=dict(width=0), showlegend=False))
                fig.add_vline(x=t_s, line_color=GOLD, line_dash="dash", annotation_text=f"t={t_s:.3f}", annotation_font_color=GOLD)
                fig.update_layout(paper_bgcolor=BG, plot_bgcolor=SURF, font=dict(color=TEXT, family="Inter"),
                                  height=280, margin=dict(l=30,r=20,t=20,b=30), showlegend=False,
                                  xaxis=dict(title="t", gridcolor=GRID), yaxis=dict(title="Density", gridcolor=GRID))
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.markdown(res["interpretation"])
            info_box("Statistical significance does not imply practical or economic significance. Effect size matters.", "warning")

# ── TWO SAMPLE ────────────────────────────────────────────────────────────────
elif test_type == "Two-sample t-test":
    c1, c2 = st.columns(2)
    with c1:
        ticker_a  = st.text_input("Asset A", value="SPY")
        ticker_b  = st.text_input("Asset B", value="QQQ")
    with c2:
        start     = st.date_input("Start", value=pd.to_datetime(DEFAULT_START))
        end       = st.date_input("End",   value=pd.to_datetime(DEFAULT_END))
        equal_var = st.checkbox("Assume equal variances", value=False)
        alpha     = st.selectbox("α", [0.01, 0.05, 0.10], index=1)

    if st.button("Run Test", type="primary"):
        with st.spinner("Downloading data..."):
            tickers = [ticker_a.upper(), ticker_b.upper()]
            rets    = fetch_simple_returns(tickers, str(start), str(end))
        valid = [t for t in tickers if t in rets.columns]
        if len(valid) < 2:
            st.error("Need two valid tickers.")
        else:
            res = two_sample_ttest(rets[valid[0]], rets[valid[1]], equal_var, alpha)
            st.divider()
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            m1.metric(f"Mean {valid[0]}", f"{res['mean_a']:.6f}")
            m2.metric(f"Mean {valid[1]}", f"{res['mean_b']:.6f}")
            m3.metric("Difference",       f"{res['mean_difference']:.6f}")
            m4.metric("t-statistic",      f"{res['t_statistic']:.4f}")
            m5.metric("p-value",          f"{res['p_value']:.6f}")
            m6.metric("Decision",         "Reject H₀" if res["reject_null"] else "Fail to reject")
            st.divider()
            st.markdown(res["interpretation"])
            info_box("Welch's t-test (unequal variances) is recommended by default. Consider effect size alongside p-value.", "warning")

# ── CONFIDENCE INTERVAL ───────────────────────────────────────────────────────
else:
    c1, c2 = st.columns([3, 1])
    with c1:
        ticker = st.text_input("Ticker", value="SPY")
        cc1, cc2 = st.columns(2)
        with cc1: start = st.date_input("Start", value=pd.to_datetime(DEFAULT_START))
        with cc2: end   = st.date_input("End",   value=pd.to_datetime(DEFAULT_END))
    with c2:
        confidence = st.selectbox("Confidence level", [0.90, 0.95, 0.99], index=1)

    if st.button("Compute", type="primary"):
        with st.spinner("Loading..."):
            rets = fetch_simple_returns([ticker.upper()], str(start), str(end))
        if rets.empty or ticker.upper() not in rets.columns:
            st.error("Could not load data.")
        else:
            res = compute_confidence_interval(rets[ticker.upper()], confidence)
            st.divider()
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("N",           str(res["n"]))
            m2.metric("Mean",        f"{res['mean']:.6f}")
            m3.metric("Std dev",     f"{res['std']:.6f}")
            m4.metric("CI lower",    f"{res['ci_lower']:.6f}")
            m5.metric("CI upper",    f"{res['ci_upper']:.6f}")

            x_r  = np.linspace(res["mean"] - 5 * res["se"], res["mean"] + 5 * res["se"], 500)
            y_pdf= stats.t.pdf(x_r, df=res["n"]-1, loc=res["mean"], scale=res["se"])
            fig  = go.Figure()
            fig.add_trace(go.Scatter(x=x_r, y=y_pdf, mode="lines", line=dict(color=BLUE, width=2)))
            ci_mask = (x_r >= res["ci_lower"]) & (x_r <= res["ci_upper"])
            fig.add_trace(go.Scatter(x=x_r[ci_mask], y=y_pdf[ci_mask], fill="tozeroy", fillcolor="rgba(88,101,242,0.15)", line=dict(width=0), name=f"{confidence:.0%} CI"))
            fig.add_vline(x=res["mean"], line_color=GOLD, line_dash="dash")
            fig.update_layout(paper_bgcolor=BG, plot_bgcolor=SURF, font=dict(color=TEXT, family="Inter"),
                              height=300, margin=dict(l=30,r=20,t=20,b=30), showlegend=False,
                              xaxis=dict(title="Mean Daily Return", gridcolor=GRID),
                              yaxis=dict(title="Density", gridcolor=GRID))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"We are **{confidence:.0%}** confident the true mean daily return of **{ticker.upper()}** lies between **{res['ci_lower']:.6f}** and **{res['ci_upper']:.6f}**.")
            info_box("Confidence intervals are constructed under approximate normality. Interpret alongside effect size and economic context.", "warning")
