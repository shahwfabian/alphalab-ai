"""
AlphaLab AI — Correlation Explorer
Correlation matrices, heatmaps, rolling correlation, and diversification analysis.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import fetch_simple_returns, DEFAULT_START, DEFAULT_END
from utils.statistics import (
    compute_correlation_matrix, correlation_pairs, diversification_ratio,
)
from utils.charts import correlation_heatmap, cumulative_return_chart

st.set_page_config(page_title="Correlation Explorer — AlphaLab AI", page_icon="🔗", layout="wide")

st.markdown("""
<style>
.stApp{background:#0A0E1A}
[data-testid="stSidebar"]{background:#070B16!important;border-right:1px solid #1E2D4A}
.stButton>button{background:linear-gradient(135deg,#00D4FF18,#00D4FF0A);border:1px solid #00D4FF;color:#00D4FF;font-weight:600;border-radius:6px}
.stTextInput>div>div>input,.stSelectbox>div>div{background:#0F1628!important;border:1px solid #1E2D4A!important;color:#E8F4FD!important}
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
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;'>MODULE 06</div>
    <div style='font-size:32px;font-weight:700;color:#00D4FF;font-family:JetBrains Mono,monospace;margin-top:6px;'>🔗 Correlation Explorer</div>
    <div style='color:#6B8CAE;font-size:14px;margin-top:8px;'>
        Analyze co-movement, identify diversification opportunities, and explore rolling correlations.
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
            value="SPY, QQQ, GLD, TLT, BTC-USD, VNQ",
            key="corr_tickers",
        )
    with c2:
        method = st.selectbox(
            "Correlation Method",
            ["pearson", "spearman", "kendall"],
            key="corr_method",
            help="Pearson: linear · Spearman: rank-based · Kendall: concordance",
        )

    c3, c4, c5 = st.columns(3)
    with c3:
        start = st.date_input("Start Date", value=pd.to_datetime(DEFAULT_START), key="corr_start")
    with c4:
        end   = st.date_input("End Date",   value=pd.to_datetime(DEFAULT_END),   key="corr_end")
    with c5:
        rolling_window = st.number_input(
            "Rolling Window (days)", value=60, min_value=10, max_value=252,
            key="corr_rolling",
            help="Window size for rolling correlation chart",
        )

with col_run:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    run_btn = st.button("▶ Analyze", use_container_width=True, key="corr_run")

# ─── Analysis ────────────────────────────────────────────────────────────────

if run_btn:
    tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]

    if len(tickers) < 2:
        st.error("Please enter at least 2 ticker symbols.")
        st.stop()

    with st.spinner(f"Downloading {', '.join(tickers)} returns..."):
        returns = fetch_simple_returns(tickers, str(start), str(end))

    valid = [t for t in tickers if t in returns.columns]
    if len(valid) < 2:
        st.error(f"Only {len(valid)} valid ticker(s) found: {valid}. Need at least 2.")
        st.stop()

    returns = returns[valid].dropna()
    corr_mx = compute_correlation_matrix(returns, method)
    pairs_df = correlation_pairs(corr_mx)

    # Equal-weight diversification ratio
    w_eq = np.ones(len(valid)) / len(valid)
    cov  = returns.cov().values
    div_ratio = diversification_ratio(w_eq, cov)

    # ─── Metrics ─────────────────────────────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    avg_corr    = pairs_df["Correlation"].mean()
    max_corr    = pairs_df.iloc[0]
    min_corr    = pairs_df.iloc[-1]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Assets Analyzed",   str(len(valid)))
    m2.metric("Avg Pairwise Corr", f"{avg_corr:.3f}")
    m3.metric("Highest Pair",      f'{max_corr["Asset A"]} / {max_corr["Asset B"]}',
              delta=f"{max_corr['Correlation']:.3f}")
    m4.metric("Diversification Ratio", f"{div_ratio:.3f}",
              help="Weighted-avg vol / portfolio vol. Higher = better diversification.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Tabs ─────────────────────────────────────────────────────────────────

    tab1, tab2, tab3, tab4 = st.tabs([
        "Correlation Heatmap", "Ranked Pairs", "Rolling Correlation", "Diversification"
    ])

    with tab1:
        fig_heat = correlation_heatmap(corr_mx, f"{method.title()} Correlation Matrix")
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown(f"""
        <div style='background:{PANEL};border:1px solid {GRID};border-radius:6px;padding:14px;font-size:13px;color:#6B8CAE;line-height:1.8;'>
        <strong style='color:{TEXT};'>How to read:</strong>
        Values range from <span style='color:{RED};'>–1 (perfect inverse)</span> to
        <span style='color:{BLUE};'>+1 (perfect co-movement)</span>.
        Assets with low or negative correlation provide diversification benefits.
        Values near 0 indicate little linear relationship.
        <strong>Method: {method.title()}</strong> — {
            "measures linear association between return series." if method == "pearson" else
            "measures monotonic rank-based association (more robust to outliers)." if method == "spearman" else
            "measures concordance between ranks (most robust, smaller values typical)."
        }
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        col_high, col_low = st.columns(2)

        top_n  = min(5, len(pairs_df))
        bottom = pairs_df.iloc[-top_n:][::-1]

        with col_high:
            st.markdown(f"**Highest Correlations (Most Co-Movement)**")
            high_df = pairs_df.head(top_n).copy()
            high_df["Correlation"] = high_df["Correlation"].round(4)
            st.dataframe(
                high_df.style.background_gradient(
                    subset=["Correlation"], cmap="Blues", vmin=-1, vmax=1
                ),
                use_container_width=True, hide_index=True,
            )
            st.markdown(f"""
            <div style='color:#6B8CAE;font-size:12px;padding:8px;'>
            High correlation pairs offer <strong>less diversification</strong>.
            Portfolios concentrated in highly correlated assets amplify systematic risk.
            </div>
            """, unsafe_allow_html=True)

        with col_low:
            st.markdown(f"**Lowest Correlations (Best Diversifiers)**")
            low_df = bottom.copy()
            low_df["Correlation"] = low_df["Correlation"].round(4)
            st.dataframe(
                low_df.style.background_gradient(
                    subset=["Correlation"], cmap="RdBu_r", vmin=-1, vmax=1
                ),
                use_container_width=True, hide_index=True,
            )
            st.markdown(f"""
            <div style='color:#6B8CAE;font-size:12px;padding:8px;'>
            Low / negative correlation pairs offer <strong>greater diversification</strong>.
            Combining them can reduce portfolio volatility without sacrificing expected return.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Full Pairwise Correlation Table**")
        all_pairs = pairs_df.copy()
        all_pairs["Correlation"] = all_pairs["Correlation"].round(4)
        all_pairs["Relationship"] = all_pairs["Correlation"].apply(
            lambda r: "Strong Positive" if r > 0.7
            else "Moderate Positive" if r > 0.4
            else "Weak Positive"   if r > 0.1
            else "Near Zero"       if r > -0.1
            else "Weak Negative"   if r > -0.4
            else "Moderate Negative" if r > -0.7
            else "Strong Negative"
        )
        st.dataframe(all_pairs, use_container_width=True, hide_index=True)

    with tab3:
        if len(valid) > 2:
            # For rolling: allow user to pick a pair
            pair_options = [f"{r['Asset A']} / {r['Asset B']}" for _, r in pairs_df.iterrows()]
            chosen_pair  = st.selectbox("Select Pair for Rolling Correlation", pair_options, key="corr_pair_sel")
            a_name, b_name = chosen_pair.split(" / ")
        else:
            a_name, b_name = valid[0], valid[1]

        if a_name in returns.columns and b_name in returns.columns:
            rolling = returns[a_name].rolling(rolling_window).corr(returns[b_name]).dropna()

            fig_roll = go.Figure()
            fig_roll.add_trace(go.Scatter(
                x=rolling.index, y=rolling,
                mode="lines", name=f"Rolling {rolling_window}-day Corr",
                line=dict(color=BLUE, width=1.8),
                fill="tozeroy", fillcolor="rgba(0,212,255,0.06)",
            ))
            fig_roll.add_hline(y=float(corr_mx.loc[a_name, b_name]),
                               line_dash="dash", line_color=GOLD,
                               annotation_text=f"Full-Period: {corr_mx.loc[a_name, b_name]:.3f}",
                               annotation_font_color=GOLD)
            fig_roll.add_hline(y=0, line_color=GRID, line_width=0.5)
            fig_roll.update_layout(
                paper_bgcolor=NAVY, plot_bgcolor=PANEL,
                font=dict(color=TEXT, family="monospace"),
                xaxis=dict(title="Date", gridcolor=GRID),
                yaxis=dict(title="Correlation", gridcolor=GRID, range=[-1.1, 1.1]),
                title=dict(text=f"Rolling {rolling_window}-Day Correlation: {a_name} / {b_name}",
                           font=dict(color=BLUE, size=14)),
                height=380, margin=dict(l=40, r=20, t=50, b=40),
                legend=dict(bgcolor=PANEL),
            )
            st.plotly_chart(fig_roll, use_container_width=True)

            st.markdown(f"""
            <div style='background:{PANEL};border:1px solid {GRID};border-radius:6px;padding:14px;font-size:13px;color:#6B8CAE;'>
            Rolling correlation reveals how the relationship between {a_name} and {b_name} has <strong>changed over time</strong>.
            A correlation that spikes toward +1 during market stress (correlation breakdown) is a common and dangerous portfolio risk.
            The dashed gold line shows the full-period average correlation of
            <strong style='color:{GOLD};'>{corr_mx.loc[a_name, b_name]:.3f}</strong>.
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("**Portfolio Diversification Analysis (Equal Weight)**")

        # Scatter: each asset's vol vs the portfolio vol contribution
        asset_vols  = returns.std() * np.sqrt(252) * 100
        port_vol_eq = np.sqrt(w_eq @ cov @ w_eq) * np.sqrt(252) * 100
        weighted_avg_vol = float(w_eq @ (returns.std().values * np.sqrt(252))) * 100

        d1, d2, d3 = st.columns(3)
        d1.metric("Weighted-Avg Asset Vol",  f"{weighted_avg_vol:.2f}%")
        d2.metric("Equal-Weight Port Vol",   f"{port_vol_eq:.2f}%")
        d3.metric("Diversification Ratio",   f"{div_ratio:.3f}",
                  help="Ratio > 1 means diversification is reducing portfolio risk")

        reduction = (weighted_avg_vol - port_vol_eq) / weighted_avg_vol * 100
        st.markdown(f"""
        <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:18px;margin-top:16px;'>
            <div style='color:{CYAN};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:12px;'>DIVERSIFICATION IMPACT</div>
            <div style='color:{TEXT};font-size:14px;line-height:1.9;'>
            Combining these {len(valid)} assets with equal weights reduces annualized volatility from the
            weighted-average of individual asset volatilities (<strong>{weighted_avg_vol:.2f}%</strong>) to
            the portfolio level (<strong>{port_vol_eq:.2f}%</strong>), a reduction of
            <strong style='color:{CYAN};'>{reduction:.1f}%</strong>.
            The diversification ratio of <strong>{div_ratio:.3f}x</strong> quantifies this benefit.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Individual Asset Volatilities (Annualized)**")
        vol_df = pd.DataFrame({
            "Ticker": valid,
            "Ann. Volatility (%)": asset_vols.round(2),
            "Equal Weight (%)":    [round(1/len(valid)*100, 2)] * len(valid),
        })
        st.dataframe(vol_df, use_container_width=True, hide_index=True)

    # ─── Interpretation ──────────────────────────────────────────────────────

    st.markdown("---")
    st.markdown("**Research Interpretation**")
    st.markdown(f"""
    Analysis based on **{len(returns)}** daily return observations across **{len(valid)}** assets
    using **{method.title()}** correlation ({str(start)} to {str(end)}).

    The average pairwise correlation is **{avg_corr:.3f}**.
    {"High average correlation suggests these assets tend to move together, limiting diversification." if avg_corr > 0.6
     else "Moderate average correlation suggests meaningful but incomplete diversification benefits." if avg_corr > 0.3
     else "Low average correlation suggests strong potential diversification benefits across this asset set."}

    Most co-moving pair: **{max_corr['Asset A']} / {max_corr['Asset B']}** (r = {max_corr['Correlation']:.3f}).
    Best diversifier pair: **{min_corr['Asset A']} / {min_corr['Asset B']}** (r = {min_corr['Correlation']:.3f}).

    *Important: Correlations are not stable. During market stress events, correlations between risk assets
    typically increase toward +1 — precisely when diversification is most needed. These estimates reflect
    the historical period only and may not generalize to future market conditions.*
    """)

    st.markdown("<br>")
    st.markdown(f"""
    <div style='background:rgba(255,215,0,0.04);border:1px solid {GOLD}33;border-radius:6px;padding:12px 16px;color:#FFD70099;font-size:11px;'>
    ⚠ Correlation ≠ causation. Correlation is not constant over time. Historical correlation is an imperfect
    estimate of future co-movement. Portfolio construction should consider conditional correlations,
    regime-dependent behavior, and tail dependence alongside simple linear correlations.
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center;padding:70px 0;'>
        <div style='font-size:52px;'>🔗</div>
        <div style='color:#6B8CAE;font-size:14px;margin-top:14px;'>
            Enter ticker symbols and click <strong style='color:#00D4FF;'>▶ Analyze</strong>.
        </div>
        <div style='color:#1E2D4A;font-size:12px;margin-top:8px;'>Example: SPY, QQQ, GLD, TLT, BTC-USD, VNQ</div>
    </div>
    """, unsafe_allow_html=True)
