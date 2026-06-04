"""
AlphaLab AI — Data Upload Lab
CSV upload, automatic exploration, summary statistics, and analysis recommendations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import parse_uploaded_csv, describe_dataframe

st.set_page_config(page_title="Data Upload Lab — AlphaLab AI", page_icon="📂", layout="wide")

st.markdown("""
<style>
.stApp{background:#0A0E1A}
[data-testid="stSidebar"]{background:#070B16!important;border-right:1px solid #1E2D4A}
.stButton>button{background:linear-gradient(135deg,#00D4FF18,#00D4FF0A);border:1px solid #00D4FF;color:#00D4FF;font-weight:600;border-radius:6px}
.stTextInput>div>div>input,.stSelectbox>div>div,.stMultiSelect>div>div{background:#0F1628!important;border:1px solid #1E2D4A!important;color:#E8F4FD!important}
[data-testid="metric-container"]{background:#0F1628!important;border:1px solid #1E2D4A!important;border-radius:8px!important;padding:16px!important}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#00D4FF!important;font-family:JetBrains Mono,monospace!important}
.stTabs [data-baseweb="tab-list"]{background:#0F1628;border-radius:8px;gap:4px}
.stTabs [data-baseweb="tab"]{color:#6B8CAE;padding:8px 20px;border-radius:6px}
.stTabs [aria-selected="true"]{background:rgba(0,212,255,0.12)!important;color:#00D4FF!important}
</style>
""", unsafe_allow_html=True)

NAVY = "#0A0E1A"; PANEL = "#0F1628"; BLUE = "#00D4FF"; GOLD = "#FFD700"
RED = "#FF4B6E"; CYAN = "#00FFD4"; GRID = "#1E2D4A"; TEXT = "#E8F4FD"
PALETTE = ["#00D4FF","#00FFD4","#FFD700","#FF4B6E","#A855F7","#F97316","#22D3EE","#4ADE80"]

# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding:30px 0 10px 0;'>
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;'>MODULE 07</div>
    <div style='font-size:32px;font-weight:700;color:#00D4FF;font-family:JetBrains Mono,monospace;margin-top:6px;'>📂 Data Upload Lab</div>
    <div style='color:#6B8CAE;font-size:14px;margin-top:8px;'>
        Upload any CSV dataset. AlphaLab will auto-detect structure, identify issues, and recommend analyses.
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── Upload Area ──────────────────────────────────────────────────────────────

col_up, col_info = st.columns([2, 3])

with col_up:
    st.markdown("""
    <div style='background:#0F1628;border:1px dashed #1E2D4A;border-radius:8px;padding:24px;text-align:center;margin-bottom:16px;'>
        <div style='font-size:32px;margin-bottom:10px;'>📁</div>
        <div style='color:#6B8CAE;font-size:13px;'>Drag & drop or browse to upload</div>
        <div style='color:#1E2D4A;font-size:11px;margin-top:6px;'>Supports CSV files up to 200MB</div>
    </div>
    """, unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["csv"], key="upload_file", label_visibility="collapsed")

with col_info:
    st.markdown(f"""
    <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:20px;'>
        <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:12px;'>WHAT ALPHALAB DETECTS AUTOMATICALLY</div>
        <div style='color:{TEXT};font-size:13px;line-height:2.1;'>
            ✓ Date/time columns and sets them as index<br>
            ✓ Numeric vs categorical columns<br>
            ✓ Missing values and their percentage<br>
            ✓ Summary statistics for all numeric columns<br>
            ✓ Potential outliers<br>
            ✓ Recommended analysis modules
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Also allow using previously uploaded data ────────────────────────────────

if st.session_state.get("uploaded_df") is not None and uploaded is None:
    st.info("Showing previously uploaded dataset. Upload a new file to replace it.")
    df = st.session_state["uploaded_df"]
elif uploaded is not None:
    df = parse_uploaded_csv(uploaded)
    if not df.empty:
        st.session_state["uploaded_df"] = df
else:
    df = None

# ─── Dataset Exploration ──────────────────────────────────────────────────────

if df is not None and not df.empty:
    summary = describe_dataframe(df)
    numeric_cols  = df.select_dtypes(include=[np.number]).columns.tolist()
    category_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    # ─── Overview Metrics ────────────────────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;margin-bottom:16px;'>
    DATASET OVERVIEW
    </div>
    """, unsafe_allow_html=True)

    total_missing = sum(summary["missing_counts"].values())
    total_cells   = summary["rows"] * summary["columns"]
    missing_pct   = total_missing / total_cells * 100 if total_cells > 0 else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Rows",            f"{summary['rows']:,}")
    m2.metric("Columns",         str(summary["columns"]))
    m3.metric("Numeric Columns", str(len(numeric_cols)))
    m4.metric("Missing Cells",   f"{total_missing:,}")
    m5.metric("Missing %",       f"{missing_pct:.2f}%",
              delta=None if missing_pct == 0 else f"{missing_pct:.1f}% data quality issue",
              delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Tabs ─────────────────────────────────────────────────────────────────

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Preview", "Summary Statistics", "Distributions", "Missing Values", "Analysis Recommendations"
    ])

    with tab1:
        n_preview = st.slider("Rows to preview", 5, min(100, summary["rows"]), 20, key="up_preview_n")
        st.dataframe(df.head(n_preview), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_dtypes1, col_dtypes2 = st.columns(2)
        with col_dtypes1:
            st.markdown("**Column Types**")
            dtype_df = pd.DataFrame({
                "Column": list(summary["dtypes"].keys()),
                "Type":   list(summary["dtypes"].values()),
                "Missing": [summary["missing_counts"][c] for c in summary["dtypes"].keys()],
                "Missing %": [f"{summary['missing_pct'][c]:.1f}%" for c in summary["dtypes"].keys()],
            })
            st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    with tab2:
        if numeric_cols:
            st.markdown("**Descriptive Statistics — Numeric Columns**")
            desc = df[numeric_cols].describe().T.round(4)
            desc.index.name = "Column"
            desc = desc.reset_index()
            st.dataframe(desc, use_container_width=True, hide_index=True)

            # Correlation matrix for numeric columns (if > 1 col)
            if len(numeric_cols) > 1:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Pearson Correlation (Numeric Columns)**")
                corr_up = df[numeric_cols].corr()
                z       = corr_up.values.round(3)
                labels  = numeric_cols

                fig_heat = go.Figure(go.Heatmap(
                    z=z, x=labels, y=labels,
                    colorscale=[[0, RED],[0.5, PANEL],[1, BLUE]],
                    zmin=-1, zmax=1,
                    text=z, texttemplate="%{text:.2f}",
                    textfont=dict(size=11, color=TEXT),
                    colorbar=dict(title="r", tickfont=dict(color=TEXT)),
                ))
                fig_heat.update_layout(
                    paper_bgcolor=NAVY, plot_bgcolor=PANEL,
                    font=dict(color=TEXT, family="monospace"),
                    height=max(300, 60 * len(labels)),
                    margin=dict(l=40, r=20, t=30, b=40),
                    xaxis=dict(gridcolor=GRID), yaxis=dict(gridcolor=GRID),
                )
                st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("No numeric columns detected in this dataset.")

    with tab3:
        if numeric_cols:
            col_sel = st.selectbox("Select column to visualize", numeric_cols, key="up_dist_col")
            col_data = df[col_sel].dropna()

            fig_dist = make_subplots(rows=1, cols=2,
                subplot_titles=["Distribution (Histogram + KDE)", "Box Plot"])

            # Histogram
            fig_dist.add_trace(go.Histogram(
                x=col_data, nbinsx=50, name="Distribution",
                marker_color=BLUE, opacity=0.7,
            ), row=1, col=1)

            # Box plot
            fig_dist.add_trace(go.Box(
                y=col_data, name=col_sel,
                marker_color=CYAN, line_color=CYAN,
                fillcolor="rgba(0,255,212,0.1)",
            ), row=1, col=2)

            fig_dist.update_layout(
                paper_bgcolor=NAVY, plot_bgcolor=PANEL,
                font=dict(color=TEXT, family="monospace"),
                showlegend=False, height=380,
                margin=dict(l=40, r=20, t=60, b=40),
            )
            fig_dist.update_xaxes(gridcolor=GRID)
            fig_dist.update_yaxes(gridcolor=GRID)
            st.plotly_chart(fig_dist, use_container_width=True)

            # Basic stats for selected column
            st.markdown(f"""
            <div style='background:{PANEL};border:1px solid {GRID};border-radius:6px;padding:14px;display:grid;grid-template-columns:repeat(5,1fr);gap:12px;font-size:12px;'>
                <div><div style='color:#6B8CAE;'>Mean</div><div style='color:{TEXT};font-family:JetBrains Mono,monospace;'>{col_data.mean():.4f}</div></div>
                <div><div style='color:#6B8CAE;'>Median</div><div style='color:{TEXT};font-family:JetBrains Mono,monospace;'>{col_data.median():.4f}</div></div>
                <div><div style='color:#6B8CAE;'>Std Dev</div><div style='color:{TEXT};font-family:JetBrains Mono,monospace;'>{col_data.std():.4f}</div></div>
                <div><div style='color:#6B8CAE;'>Skewness</div><div style='color:{TEXT};font-family:JetBrains Mono,monospace;'>{float(col_data.skew()):.4f}</div></div>
                <div><div style='color:#6B8CAE;'>Kurtosis</div><div style='color:{TEXT};font-family:JetBrains Mono,monospace;'>{float(col_data.kurtosis()):.4f}</div></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No numeric columns available for distribution plots.")

    with tab4:
        missing_data = df.isnull().sum()
        missing_data = missing_data[missing_data > 0]

        if missing_data.empty:
            st.success("✅ No missing values detected. Dataset is complete.")
        else:
            st.warning(f"⚠ {len(missing_data)} column(s) have missing values.")

            miss_df = pd.DataFrame({
                "Column":     missing_data.index,
                "Missing Count": missing_data.values,
                "Missing %":  (missing_data / len(df) * 100).round(2).values,
                "Data Type":  [str(df[c].dtype) for c in missing_data.index],
            }).sort_values("Missing %", ascending=False)

            st.dataframe(miss_df, use_container_width=True, hide_index=True)

            # Bar chart of missing %
            fig_miss = go.Figure(go.Bar(
                x=miss_df["Column"],
                y=miss_df["Missing %"],
                marker_color=[RED if p > 20 else GOLD if p > 5 else BLUE
                              for p in miss_df["Missing %"]],
                text=[f"{p:.1f}%" for p in miss_df["Missing %"]],
                textposition="outside",
            ))
            fig_miss.update_layout(
                paper_bgcolor=NAVY, plot_bgcolor=PANEL,
                font=dict(color=TEXT, family="monospace"),
                yaxis=dict(title="Missing %", gridcolor=GRID),
                xaxis=dict(title="Column", gridcolor=GRID),
                title=dict(text="Missing Value Rate by Column", font=dict(color=BLUE, size=14)),
                height=360, margin=dict(l=40, r=20, t=50, b=60),
                showlegend=False,
            )
            st.plotly_chart(fig_miss, use_container_width=True)

    with tab5:
        st.markdown(f"""
        <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;margin-bottom:16px;'>
        AI ANALYSIS RECOMMENDATIONS
        </div>
        """, unsafe_allow_html=True)

        recommendations = []
        has_date = df.index.dtype == "datetime64[ns]" or pd.api.types.is_datetime64_any_dtype(df.index)

        if len(numeric_cols) >= 2:
            recommendations.append({
                "module":  "Regression Lab",
                "icon":    "📈",
                "title":   "Run Regression Analysis",
                "reason":  f"Dataset has {len(numeric_cols)} numeric columns. You can test relationships between variables using OLS regression.",
                "action":  f"Use '{numeric_cols[0]}' as dependent variable and one or more of {numeric_cols[1:3]} as predictors.",
                "urgency": BLUE,
            })
            recommendations.append({
                "module":  "Correlation Explorer",
                "icon":    "🔗",
                "title":   "Explore Correlations",
                "reason":  f"Multiple numeric columns detected. Correlation analysis can reveal co-movement and redundancy.",
                "action":  f"Analyze Pearson or Spearman correlation across {', '.join(numeric_cols[:5])}.",
                "urgency": CYAN,
            })

        if len(numeric_cols) >= 1:
            recommendations.append({
                "module":  "Statistical Inference Lab",
                "icon":    "🔬",
                "title":   "Run Hypothesis Tests",
                "reason":  "Numeric columns available for t-tests and confidence interval estimation.",
                "action":  f"Test whether the mean of '{numeric_cols[0]}' is significantly different from zero or some benchmark.",
                "urgency": GOLD,
            })
            recommendations.append({
                "module":  "Probability Lab",
                "icon":    "🎲",
                "title":   "Model Return Distribution",
                "reason":  "If numeric columns represent returns or price changes, AlphaLab can estimate tail probabilities and VaR.",
                "action":  f"Use '{numeric_cols[0]}' as a return series to compute VaR, CVaR, and drawdown probabilities.",
                "urgency": GOLD,
            })

        if total_missing > 0:
            recommendations.append({
                "module":  "Data Cleaning Required",
                "icon":    "⚠",
                "title":   "Address Missing Values Before Analysis",
                "reason":  f"{total_missing} missing cells ({missing_pct:.1f}% of data). Most analyses require complete data.",
                "action":  "Consider: forward-fill for time series, mean/median imputation, or dropping incomplete rows.",
                "urgency": RED,
            })

        for rec in recommendations:
            st.markdown(f"""
            <div style='background:{PANEL};border:1px solid {GRID};border-left:4px solid {rec["urgency"]};
                        border-radius:8px;padding:18px;margin-bottom:12px;'>
                <div style='display:flex;align-items:center;gap:12px;margin-bottom:8px;'>
                    <span style='font-size:20px;'>{rec["icon"]}</span>
                    <div>
                        <div style='color:{rec["urgency"]};font-weight:700;font-size:14px;'>{rec["title"]}</div>
                        <div style='color:#6B8CAE;font-size:11px;font-family:JetBrains Mono,monospace;margin-top:2px;'>→ {rec["module"]}</div>
                    </div>
                </div>
                <div style='color:{TEXT};font-size:13px;margin-bottom:6px;'>{rec["reason"]}</div>
                <div style='color:#6B8CAE;font-size:12px;font-style:italic;'>{rec["action"]}</div>
            </div>
            """, unsafe_allow_html=True)

        if not recommendations:
            st.info("No specific recommendations generated. Ensure your dataset has numeric columns for quantitative analysis.")

    # ─── Export cleaned data ─────────────────────────────────────────────────

    st.markdown("---")
    st.markdown("**Export**")
    csv_export = df.to_csv().encode("utf-8")
    st.download_button(
        "⬇ Download Dataset as CSV",
        data=csv_export,
        file_name="alphalab_dataset.csv",
        mime="text/csv",
    )

else:
    st.markdown("""
    <div style='text-align:center;padding:80px 0;'>
        <div style='font-size:52px;'>📂</div>
        <div style='color:#6B8CAE;font-size:14px;margin-top:16px;'>Upload a CSV file above to begin exploration.</div>
        <div style='color:#1E2D4A;font-size:12px;margin-top:8px;'>
            Supports price data, returns, financial metrics, or any tabular dataset.
        </div>
    </div>
    """, unsafe_allow_html=True)
