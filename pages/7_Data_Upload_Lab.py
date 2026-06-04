"""AlphaLab AI — Data Upload Lab"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import inject_css, page_header, info_box
from utils.data_loader import parse_uploaded_csv, describe_dataframe

st.set_page_config(page_title="Data Upload — AlphaLab AI", page_icon="⬡", layout="wide")
inject_css()

page_header("Data Upload", "Upload any CSV. AlphaLab auto-detects structure, flags issues, and recommends analyses.")

BG = "#0d0d0d"; SURF = "#161616"; GRID = "#1f1f1f"; TEXT = "#e5e5e5"; BLUE = "#5865f2"

uploaded = st.file_uploader("Upload CSV", type=["csv"])

if st.session_state.get("uploaded_df") is not None and uploaded is None:
    st.info("Showing previously uploaded dataset.")
    df = st.session_state["uploaded_df"]
elif uploaded is not None:
    df = parse_uploaded_csv(uploaded)
    if not df.empty:
        st.session_state["uploaded_df"] = df
else:
    df = None

if df is not None and not df.empty:
    summary      = describe_dataframe(df)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    total_miss   = sum(summary["missing_counts"].values())
    miss_pct     = total_miss / (summary["rows"] * summary["columns"]) * 100 if summary["rows"] * summary["columns"] > 0 else 0

    st.divider()

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Rows",             f"{summary['rows']:,}")
    m2.metric("Columns",          str(summary["columns"]))
    m3.metric("Numeric columns",  str(len(numeric_cols)))
    m4.metric("Missing cells",    f"{total_miss:,}")
    m5.metric("Missing %",        f"{miss_pct:.2f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Preview", "Statistics", "Distributions", "Missing Values", "Recommendations"])

    with tab1:
        n = st.slider("Rows to preview", 5, min(100, summary["rows"]), 20)
        st.dataframe(df.head(n), use_container_width=True)
        dtype_df = pd.DataFrame({
            "Column":    list(summary["dtypes"].keys()),
            "Type":      list(summary["dtypes"].values()),
            "Missing":   [summary["missing_counts"][c] for c in summary["dtypes"].keys()],
            "Missing %": [f"{summary['missing_pct'][c]:.1f}%" for c in summary["dtypes"].keys()],
        })
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    with tab2:
        if numeric_cols:
            desc = df[numeric_cols].describe().T.round(4).reset_index()
            desc.columns = ["Column"] + list(desc.columns[1:])
            st.dataframe(desc, use_container_width=True, hide_index=True)
            if len(numeric_cols) > 1:
                corr = df[numeric_cols].corr()
                from utils.charts import correlation_heatmap
                st.plotly_chart(correlation_heatmap(corr, "Pearson Correlation"), use_container_width=True)
        else:
            st.info("No numeric columns detected.")

    with tab3:
        if numeric_cols:
            col_sel  = st.selectbox("Column", numeric_cols)
            col_data = df[col_sel].dropna()
            fig = make_subplots(rows=1, cols=2, subplot_titles=["Histogram", "Box Plot"])
            fig.add_trace(go.Histogram(x=col_data, nbinsx=50, marker_color=BLUE, opacity=0.7), row=1, col=1)
            fig.add_trace(go.Box(y=col_data, marker_color="#818cf8", line_color="#818cf8", fillcolor="rgba(129,140,248,0.1)"), row=1, col=2)
            fig.update_layout(paper_bgcolor=BG, plot_bgcolor=SURF, font=dict(color=TEXT, family="Inter"),
                              height=340, margin=dict(l=30,r=20,t=40,b=30), showlegend=False)
            fig.update_xaxes(gridcolor=GRID)
            fig.update_yaxes(gridcolor=GRID)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"Mean **{col_data.mean():.4f}** · Median **{col_data.median():.4f}** · Std **{col_data.std():.4f}** · Skew **{float(col_data.skew()):.4f}** · Kurtosis **{float(col_data.kurtosis()):.4f}**")
        else:
            st.info("No numeric columns available.")

    with tab4:
        miss_data = df.isnull().sum()
        miss_data = miss_data[miss_data > 0]
        if miss_data.empty:
            st.success("No missing values detected.")
        else:
            miss_df = pd.DataFrame({
                "Column":    miss_data.index,
                "Missing":   miss_data.values,
                "Missing %": (miss_data / len(df) * 100).round(2).values,
            }).sort_values("Missing %", ascending=False)
            st.dataframe(miss_df, use_container_width=True, hide_index=True)
            fig = go.Figure(go.Bar(
                x=miss_df["Column"], y=miss_df["Missing %"],
                marker_color=[("#ef4444" if p > 20 else "#f59e0b" if p > 5 else BLUE) for p in miss_df["Missing %"]],
                text=[f"{p:.1f}%" for p in miss_df["Missing %"]], textposition="outside",
            ))
            fig.update_layout(paper_bgcolor=BG, plot_bgcolor=SURF, font=dict(color=TEXT, family="Inter"),
                              height=300, margin=dict(l=30,r=20,t=20,b=60), showlegend=False,
                              xaxis=dict(gridcolor=GRID), yaxis=dict(title="Missing %", gridcolor=GRID))
            st.plotly_chart(fig, use_container_width=True)

    with tab5:
        recs = []
        if len(numeric_cols) >= 2:
            recs += [
                ("Regression Lab",       f"{len(numeric_cols)} numeric columns detected. Test relationships between variables using OLS."),
                ("Correlation Explorer", "Multiple numeric columns available for correlation and diversification analysis."),
            ]
        if len(numeric_cols) >= 1:
            recs += [
                ("Statistical Inference", f"Run t-tests or confidence intervals on numeric columns."),
                ("Probability Lab",       "Model return distribution, VaR, and tail risk from numeric data."),
            ]
        if total_miss > 0:
            recs.append(("Data Quality", f"{total_miss} missing cells detected. Consider imputation or dropping incomplete rows before analysis."))

        for module, reason in recs:
            st.markdown(f"""
            <div style="padding:0.875rem 0; border-bottom:1px solid #1a1a1a; display:flex; align-items:flex-start; gap:1rem;">
                <span style="font-size:0.875rem; font-weight:500; color:#818cf8; white-space:nowrap; min-width:160px;">{module}</span>
                <span style="font-size:0.825rem; color:#666;">{reason}</span>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.download_button("Download as CSV", data=df.to_csv().encode("utf-8"),
                       file_name="alphalab_dataset.csv", mime="text/csv")

else:
    st.markdown("""
    <div style="text-align:center; padding:4rem 0; color:#2a2a2a;">
        <div style="font-size:2rem; margin-bottom:0.75rem;">⬡</div>
        <div style="font-size:0.875rem;">Upload a CSV file above to begin exploration.</div>
    </div>
    """, unsafe_allow_html=True)
