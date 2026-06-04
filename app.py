"""
AlphaLab AI — Main Application Entry Point
AI-Powered Statistical Research Copilot
"""

import streamlit as st

st.set_page_config(
    page_title="AlphaLab AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "AlphaLab AI — AI-Powered Statistical Research Copilot",
    },
)

# ─── Global CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

/* Sidebar */
[data-testid="stSidebar"] {
    background: #070B16 !important;
    border-right: 1px solid #1E2D4A;
}
[data-testid="stSidebar"] .stMarkdown { color: #6B8CAE; }

/* Main background */
.stApp { background: #0A0E1A; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #0F1628 !important;
    border: 1px solid #1E2D4A !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
[data-testid="metric-container"] label { color: #6B8CAE !important; font-size: 11px !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00D4FF !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #0F1628; border-radius: 8px; gap: 4px; }
.stTabs [data-baseweb="tab"] { color: #6B8CAE; padding: 8px 20px; border-radius: 6px; }
.stTabs [aria-selected="true"] { background: rgba(0,212,255,0.12) !important; color: #00D4FF !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00D4FF18, #00D4FF0A);
    border: 1px solid #00D4FF;
    color: #00D4FF;
    font-weight: 600;
    border-radius: 6px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #00D4FF22;
    box-shadow: 0 0 12px #00D4FF40;
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #0F1628 !important;
    border: 1px solid #1E2D4A !important;
    color: #E8F4FD !important;
    border-radius: 6px !important;
}

/* DataFrames */
[data-testid="stDataFrame"] { background: #0F1628; border-radius: 8px; }

/* Expanders */
details { border: 1px solid #1E2D4A !important; border-radius: 6px !important; background: #0F1628 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0A0E1A; }
::-webkit-scrollbar-thumb { background: #1E2D4A; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00D4FF44; }
</style>
""", unsafe_allow_html=True)

# ─── Session State Defaults ───────────────────────────────────────────────────

def init_session_state():
    defaults = {
        "openai_api_key": "",
        "risk_free_rate": 0.05,
        "default_start": "2020-01-01",
        "default_end": "2024-12-31",
        "chat_history": [],
        "uploaded_df": None,
        "last_regression_results": None,
        "last_portfolio_results": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <div style='font-family: JetBrains Mono, monospace; font-size: 22px; color: #00D4FF; letter-spacing: 3px; font-weight: 600;'>⬡ ALPHALAB</div>
        <div style='font-size: 10px; color: #6B8CAE; letter-spacing: 2px; margin-top: 4px;'>STATISTICAL RESEARCH COPILOT</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("**NAVIGATION**", help="Select a module to begin analysis")
    st.page_link("app.py", label="Home", icon="⬡")
    st.page_link("pages/1_Research_Assistant.py",        label="Research Assistant",       icon="🤖")
    st.page_link("pages/2_Regression_Lab.py",             label="Regression Lab",            icon="📈")
    st.page_link("pages/3_Statistical_Inference_Lab.py",  label="Statistical Inference",     icon="🔬")
    st.page_link("pages/4_Probability_Lab.py",            label="Probability Lab",           icon="🎲")
    st.page_link("pages/5_Portfolio_Optimization_Lab.py", label="Portfolio Optimization",    icon="💼")
    st.page_link("pages/6_Correlation_Explorer.py",       label="Correlation Explorer",      icon="🔗")
    st.page_link("pages/7_Data_Upload_Lab.py",            label="Data Upload Lab",           icon="📂")
    st.page_link("pages/8_Research_Reports.py",           label="Research Reports",          icon="📄")
    st.page_link("pages/9_Settings.py",                   label="Settings",                  icon="⚙️")

    st.divider()

    api_status = "🟢 Connected" if st.session_state.openai_api_key else "🔴 Not set"
    st.markdown(f"**AI Engine:** {api_status}")
    rf_pct = st.session_state.risk_free_rate * 100
    st.markdown(f"**Risk-Free Rate:** {rf_pct:.2f}%")
    st.markdown("<div style='color:#6B8CAE; font-size:11px; margin-top:16px;'>For research & educational use only. Not financial advice.</div>", unsafe_allow_html=True)

# ─── Home Page ────────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding: 50px 0 30px 0; text-align: center;'>
    <div style='font-family: JetBrains Mono, monospace; font-size: 13px; color: #6B8CAE; letter-spacing: 4px; margin-bottom: 14px;'>INTRODUCING</div>
    <div style='font-family: JetBrains Mono, monospace; font-size: 52px; font-weight: 700; color: #00D4FF; letter-spacing: 4px; line-height: 1.1;'>
        ⬡ ALPHALAB AI
    </div>
    <div style='font-size: 20px; color: #E8F4FD; margin-top: 16px; font-weight: 300; letter-spacing: 1px;'>
        AI-Powered Statistical Research Copilot
    </div>
    <div style='font-size: 14px; color: #6B8CAE; margin-top: 10px; max-width: 600px; margin-left: auto; margin-right: auto;'>
        Convert natural-language research questions into quantitative analysis,
        visualizations, and professional research reports.
    </div>
</div>
""", unsafe_allow_html=True)

# ─── What AlphaLab Does ───────────────────────────────────────────────────────

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background:#0F1628; border:1px solid #1E2D4A; border-top:3px solid #00D4FF; border-radius:8px; padding:24px; height:220px;'>
        <div style='font-size:28px; margin-bottom:12px;'>📐</div>
        <div style='color:#00D4FF; font-family:JetBrains Mono,monospace; font-size:13px; font-weight:600; letter-spacing:1px;'>QUANTITATIVE RIGOR</div>
        <div style='color:#6B8CAE; font-size:13px; margin-top:10px; line-height:1.6;'>
        Regression analysis, hypothesis testing, probability modeling, and portfolio optimization — all in one platform.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background:#0F1628; border:1px solid #1E2D4A; border-top:3px solid #00FFD4; border-radius:8px; padding:24px; height:220px;'>
        <div style='font-size:28px; margin-bottom:12px;'>🤖</div>
        <div style='color:#00FFD4; font-family:JetBrains Mono,monospace; font-size:13px; font-weight:600; letter-spacing:1px;'>AI INTERPRETATION</div>
        <div style='color:#6B8CAE; font-size:13px; margin-top:10px; line-height:1.6;'>
        Ask research questions in plain English. AlphaLab identifies the right method, runs the analysis, and explains results.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background:#0F1628; border:1px solid #1E2D4A; border-top:3px solid #FFD700; border-radius:8px; padding:24px; height:220px;'>
        <div style='font-size:28px; margin-bottom:12px;'>📄</div>
        <div style='color:#FFD700; font-family:JetBrains Mono,monospace; font-size:13px; font-weight:600; letter-spacing:1px;'>RESEARCH REPORTS</div>
        <div style='color:#6B8CAE; font-size:13px; margin-top:10px; line-height:1.6;'>
        Export professional HTML research reports with methodology, results, visualizations, and interpretations.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Modules Grid ─────────────────────────────────────────────────────────────

st.markdown("""
<div style='font-family:JetBrains Mono,monospace; font-size:12px; color:#6B8CAE; letter-spacing:3px; margin-bottom:18px;'>
CORE MODULES
</div>
""", unsafe_allow_html=True)

modules = [
    ("🤖", "Research Assistant",      "Ask any statistical or finance question in plain English."),
    ("📈", "Regression Lab",           "OLS regression with full diagnostics and interpretation."),
    ("🔬", "Statistical Inference",    "T-tests, confidence intervals, hypothesis testing."),
    ("🎲", "Probability Lab",          "Distribution analysis, VaR, drawdown probabilities."),
    ("💼", "Portfolio Optimization",   "Mean-Variance Optimization, Sharpe, Efficient Frontier."),
    ("🔗", "Correlation Explorer",     "Correlation matrices, heatmaps, diversification analysis."),
    ("📂", "Data Upload Lab",          "Import any CSV dataset and explore it automatically."),
    ("📄", "Research Reports",         "Generate and export professional research reports."),
]

cols = st.columns(4)
for i, (icon, name, desc) in enumerate(modules):
    with cols[i % 4]:
        st.markdown(f"""
        <div style='background:#0F1628; border:1px solid #1E2D4A; border-radius:8px; padding:18px; margin-bottom:14px; min-height:130px;'>
            <div style='font-size:22px; margin-bottom:8px;'>{icon}</div>
            <div style='color:#E8F4FD; font-size:13px; font-weight:600;'>{name}</div>
            <div style='color:#6B8CAE; font-size:12px; margin-top:6px; line-height:1.5;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Example Questions ────────────────────────────────────────────────────────

st.markdown("""
<div style='font-family:JetBrains Mono,monospace; font-size:12px; color:#6B8CAE; letter-spacing:3px; margin-bottom:18px;'>
EXAMPLE QUESTIONS YOU CAN ASK
</div>
""", unsafe_allow_html=True)

questions = [
    ("📈", "Does QQQ explain NVDA returns better than SPY?",         "Regression Lab"),
    ("🔬", "Is momentum statistically significant in this dataset?", "Statistical Inference"),
    ("🎲", "What is the probability of a 10% drawdown in 30 days?",  "Probability Lab"),
    ("💼", "Build the highest Sharpe portfolio from these 5 assets.", "Portfolio Optimization"),
    ("🔗", "Which factor contributes most to portfolio risk?",        "Correlation Explorer"),
    ("🤖", "Explain the difference between R² and Adjusted R².",      "Research Assistant"),
]

q_cols = st.columns(2)
for i, (icon, question, module) in enumerate(questions):
    with q_cols[i % 2]:
        st.markdown(f"""
        <div style='background:#0F1628; border:1px solid #1E2D4A; border-radius:6px; padding:14px 16px; margin-bottom:10px; display:flex; align-items:flex-start; gap:12px;'>
            <span style='font-size:18px;'>{icon}</span>
            <div>
                <div style='color:#E8F4FD; font-size:13px; font-style:italic;'>"{question}"</div>
                <div style='color:#00D4FF; font-size:11px; margin-top:5px; font-family:JetBrains Mono,monospace;'>→ {module}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Who It's For ─────────────────────────────────────────────────────────────

st.markdown("""
<div style='font-family:JetBrains Mono,monospace; font-size:12px; color:#6B8CAE; letter-spacing:3px; margin-bottom:18px;'>
WHO ALPHALAB IS FOR
</div>
""", unsafe_allow_html=True)

personas = [
    ("Quantitative Researchers", "Validate hypotheses, run regressions, and generate structured reports with full statistical rigor."),
    ("Portfolio Managers",       "Optimize allocations, analyze correlations, and model tail risk using modern portfolio theory."),
    ("Students & Educators",     "Learn statistical methods hands-on with real market data and plain-English explanations."),
    ("Data Analysts",            "Upload any dataset, explore distributions, run inference tests, and export findings."),
]

p_cols = st.columns(4)
for i, (role, desc) in enumerate(personas):
    with p_cols[i]:
        st.markdown(f"""
        <div style='background:#0F1628; border:1px solid #1E2D4A; border-radius:8px; padding:18px;'>
            <div style='color:#00FFD4; font-size:13px; font-weight:600; font-family:JetBrains Mono,monospace;'>{role}</div>
            <div style='color:#6B8CAE; font-size:12px; margin-top:8px; line-height:1.6;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Disclaimer ───────────────────────────────────────────────────────────────

st.markdown("""
<div style='background:rgba(255,215,0,0.05); border:1px solid #FFD700; border-radius:6px; padding:14px 18px; color:#FFD700; font-size:12px;'>
    ⚠ <strong>Disclaimer:</strong> AlphaLab AI is a research and educational tool. It does not provide financial advice,
    investment recommendations, or guarantees of future performance. All statistical outputs carry uncertainty.
    Results should be interpreted by qualified professionals in appropriate context.
</div>
""", unsafe_allow_html=True)
