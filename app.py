"""
AlphaLab AI — Home
"""

import streamlit as st

st.set_page_config(
    page_title="AlphaLab AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session defaults ──────────────────────────────────────────────────────────
for k, v in {
    "openai_api_key": "",
    "risk_free_rate": 0.05,
    "default_start":  "2020-01-01",
    "default_end":    "2024-12-31",
    "chat_history":   [],
    "uploaded_df":    None,
    "last_regression_results": None,
    "last_portfolio_results":  None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Global CSS ────────────────────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.styles import inject_css
inject_css()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.25rem 0 1rem 0;">
        <div style="font-size:1rem; font-weight:600; color:#e5e5e5; letter-spacing:-0.01em;">⬡ AlphaLab AI</div>
        <div style="font-size:0.7rem; color:#444; margin-top:3px;">Statistical Research Copilot</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.page_link("app.py",                                        label="Home")
    st.page_link("pages/1_Research_Assistant.py",                 label="Research Assistant")
    st.page_link("pages/2_Regression_Lab.py",                     label="Regression Lab")
    st.page_link("pages/3_Statistical_Inference_Lab.py",          label="Statistical Inference")
    st.page_link("pages/4_Probability_Lab.py",                    label="Probability Lab")
    st.page_link("pages/5_Portfolio_Optimization_Lab.py",         label="Portfolio Optimization")
    st.page_link("pages/6_Correlation_Explorer.py",               label="Correlation Explorer")
    st.page_link("pages/7_Data_Upload_Lab.py",                    label="Data Upload")
    st.page_link("pages/8_Research_Reports.py",                   label="Research Reports")
    st.page_link("pages/9_Settings.py",                           label="Settings")

    st.divider()
    st.markdown(f"""
    <div style="font-size:0.75rem; color:#444; line-height:1.8;">
        AI &nbsp;{'<span style="color:#22c55e">●</span> Connected' if st.session_state.openai_api_key else '<span style="color:#333">● Not set</span>'}<br>
        Risk-free rate &nbsp;<span style="color:#666">{st.session_state.risk_free_rate*100:.2f}%</span>
    </div>
    """, unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 3rem 0 2.5rem 0;">
    <div style="font-size:0.7rem; color:#444; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.75rem;">Statistical Research Copilot</div>
    <h1 style="font-size:2.25rem; font-weight:600; color:#f0f0f0; letter-spacing:-0.03em; line-height:1.2; margin:0 0 0.75rem 0;">
        AlphaLab AI
    </h1>
    <p style="font-size:1rem; color:#555; max-width:520px; line-height:1.7; margin:0;">
        Convert research questions into quantitative analysis, statistical interpretation, and professional reports. No prediction claims. Just evidence.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Modules ───────────────────────────────────────────────────────────────────
st.markdown('<p style="font-size:0.7rem; color:#444; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:1rem;">Modules</p>', unsafe_allow_html=True)

modules = [
    ("Research Assistant",    "Ask any statistical question in plain English. AlphaLab identifies the method and guides your analysis."),
    ("Regression Lab",        "OLS regression with full diagnostics — coefficients, R², residuals, Q-Q plot, and interpretation."),
    ("Statistical Inference", "Hypothesis testing, t-tests, and confidence intervals with visualized rejection regions."),
    ("Probability Lab",       "Return distributions, Value at Risk, CVaR, drawdown probability modeling."),
    ("Portfolio Optimization","Mean-Variance Optimization — Max Sharpe, Min Variance, Efficient Frontier."),
    ("Correlation Explorer",  "Heatmaps, rolling correlation, pairwise analysis, and diversification ratios."),
    ("Data Upload",           "Upload any CSV. Auto-detect columns, summarize distributions, flag missing values."),
    ("Research Reports",      "Generate and export professional HTML reports with methodology and visualizations."),
]

cols = st.columns(2)
for i, (name, desc) in enumerate(modules):
    with cols[i % 2]:
        st.markdown(f"""
        <div style="padding: 1rem 0; border-bottom: 1px solid #1a1a1a;">
            <div style="font-size:0.875rem; font-weight:500; color:#d0d0d0; margin-bottom:0.3rem;">{name}</div>
            <div style="font-size:0.8rem; color:#555; line-height:1.6;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── Example questions ─────────────────────────────────────────────────────────
st.markdown('<p style="font-size:0.7rem; color:#444; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:1rem;">Example questions</p>', unsafe_allow_html=True)

questions = [
    ("Does QQQ explain NVDA returns better than SPY?",         "Regression Lab"),
    ("Is momentum statistically significant?",                 "Statistical Inference"),
    ("What is the probability of a 10% drawdown in 30 days?", "Probability Lab"),
    ("Build the highest Sharpe portfolio from these 5 assets.","Portfolio Optimization"),
    ("Which assets are most correlated in my portfolio?",      "Correlation Explorer"),
    ("Explain the difference between R² and Adjusted R².",     "Research Assistant"),
]

for question, module in questions:
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between;
                padding:0.75rem 0; border-bottom:1px solid #161616;">
        <span style="font-size:0.875rem; color:#888; font-style:italic;">"{question}"</span>
        <span style="font-size:0.7rem; color:#5865f2; white-space:nowrap; margin-left:1.5rem;">{module}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<p style="font-size:0.75rem; color:#333; line-height:1.7;">
For research and educational use only. AlphaLab does not provide financial advice or predict future performance.
</p>
""", unsafe_allow_html=True)
