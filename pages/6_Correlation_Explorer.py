"""AlphaLab AI — Correlation Explorer"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import inject_css, page_header, info_box
from utils.data_loader import fetch_simple_returns, DEFAULT_START, DEFAULT_END
from utils.statistics import compute_correlation_matrix, correlation_pairs, diversification_ratio
from utils.charts import correlation_heatmap, cumulative_return_chart

st.set_page_config(page_title="Correlation Explorer — AlphaLab AI", page_icon="⬡", layout="wide")
inject_css()

page_header("Correlation Explorer", "Correlation matrices, rolling correlation, and diversification analysis.")

BG = "#0d0d0d"; SURF = "#161616"; GRID = "#1f1f1f"; TEXT = "#e5e5e5"; BLUE = "#5865f2"

c1, c2 = st.columns(2)
with c1:
    tickers_raw    = st.text_input("Tickers (comma-separated, min 2)", value="SPY, QQQ, GLD, TLT, BTC-USD")
    method         = st.selectbox("Method", ["pearson", "spearman", "kendall"])
with c2:
    start          = st.date_input("Start", value=pd.to_datetime(DEFAULT_START))
    end            = st.date_input("End",   value=pd.to_datetime(DEFAULT_END))
    rolling_window = st.number_input("Rolling window (days)", value=60, min_value=10, max_value=252)

run_btn = st.button("Analyze", type="primary")

if run_btn:
    tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
    if len(tickers) < 2:
        st.error("Enter at least 2 tickers.")
        st.stop()

    with st.spinner("Downloading data..."):
        rets = fetch_simple_returns(tickers, str(start), str(end))

    valid = [t for t in tickers if t in rets.columns]
    if len(valid) < 2:
        st.error("Not enough valid tickers.")
        st.stop()

    rets     = rets[valid].dropna()
    corr_mx  = compute_correlation_matrix(rets, method)
    pairs_df = correlation_pairs(corr_mx)
    w_eq     = np.ones(len(valid)) / len(valid)
    div_r    = diversification_ratio(w_eq, rets.cov().values)
    avg_corr = pairs_df["Correlation"].mean()

    st.divider()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Assets",               str(len(valid)))
    m2.metric("Avg correlation",      f"{avg_corr:.3f}")
    m3.metric("Highest pair",         f'{pairs_df.iloc[0]["Asset A"]} / {pairs_df.iloc[0]["Asset B"]}',
              delta=f'{pairs_df.iloc[0]["Correlation"]:.3f}')
    m4.metric("Diversification ratio", f"{div_r:.3f}")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Heatmap", "Ranked Pairs", "Rolling Correlation", "Diversification"])

    with tab1:
        st.plotly_chart(correlation_heatmap(corr_mx, f"{method.title()} Correlation Matrix"), use_container_width=True)

    with tab2:
        col_h, col_l = st.columns(2)
        top_n = min(5, len(pairs_df))
        with col_h:
            st.markdown("**Most correlated**")
            st.dataframe(pairs_df.head(top_n).round(4), use_container_width=True, hide_index=True)
        with col_l:
            st.markdown("**Best diversifiers**")
            st.dataframe(pairs_df.tail(top_n)[::-1].round(4), use_container_width=True, hide_index=True)
        st.markdown("<br>", unsafe_allow_html=True)
        all_pairs = pairs_df.copy()
        all_pairs["Correlation"] = all_pairs["Correlation"].round(4)
        all_pairs["Relationship"] = all_pairs["Correlation"].apply(
            lambda r: "Strong positive" if r > 0.7 else "Moderate positive" if r > 0.4
            else "Weak positive" if r > 0.1 else "Near zero" if r > -0.1
            else "Weak negative" if r > -0.4 else "Moderate negative" if r > -0.7 else "Strong negative"
        )
        st.dataframe(all_pairs, use_container_width=True, hide_index=True)

    with tab3:
        pair_opts = [f"{r['Asset A']} / {r['Asset B']}" for _, r in pairs_df.iterrows()]
        chosen    = st.selectbox("Pair", pair_opts) if len(valid) > 2 else f"{valid[0]} / {valid[1]}"
        a_name, b_name = chosen.split(" / ")
        if a_name in rets.columns and b_name in rets.columns:
            rolling = rets[a_name].rolling(rolling_window).corr(rets[b_name]).dropna()
            full_r  = float(corr_mx.loc[a_name, b_name])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=rolling.index, y=rolling, mode="lines",
                                     line=dict(color=BLUE, width=1.8), name="Rolling corr",
                                     fill="tozeroy", fillcolor="rgba(88,101,242,0.06)"))
            fig.add_hline(y=full_r, line_color="#f59e0b", line_dash="dash",
                          annotation_text=f"Full period: {full_r:.3f}", annotation_font_color="#f59e0b")
            fig.update_layout(paper_bgcolor=BG, plot_bgcolor=SURF, font=dict(color=TEXT, family="Inter"),
                              height=340, margin=dict(l=30,r=20,t=20,b=30),
                              xaxis=dict(gridcolor=GRID), yaxis=dict(gridcolor=GRID, range=[-1.1, 1.1]),
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"Rolling {rolling_window}-day correlation: **{a_name} / {b_name}**. Full-period average: **{full_r:.3f}**.")

    with tab4:
        vols         = rets.std() * np.sqrt(252) * 100
        port_vol_eq  = np.sqrt(w_eq @ rets.cov().values @ w_eq) * np.sqrt(252) * 100
        weighted_avg = float(w_eq @ (rets.std().values * np.sqrt(252))) * 100
        reduction    = (weighted_avg - port_vol_eq) / weighted_avg * 100

        d1, d2, d3 = st.columns(3)
        d1.metric("Weighted-avg asset vol", f"{weighted_avg:.2f}%")
        d2.metric("Equal-weight port vol",  f"{port_vol_eq:.2f}%")
        d3.metric("Diversification ratio",  f"{div_r:.3f}")

        st.markdown(f"""
        Combining these {len(valid)} assets with equal weights reduces annualized volatility from **{weighted_avg:.2f}%** to **{port_vol_eq:.2f}%** — a reduction of **{reduction:.1f}%**.
        """)

        vol_df = pd.DataFrame({"Ticker": valid, "Ann. Volatility (%)": vols.round(2)})
        st.dataframe(vol_df, use_container_width=True, hide_index=True)

    info_box("Correlations are not stable over time and tend to increase during market stress. Historical correlation is an imperfect estimate of future co-movement.", "warning")

else:
    st.markdown("""
    <div style="text-align:center; padding:4rem 0; color:#2a2a2a;">
        <div style="font-size:2rem; margin-bottom:0.75rem;">⬡</div>
        <div style="font-size:0.875rem;">Enter tickers above and click Analyze.</div>
    </div>
    """, unsafe_allow_html=True)
