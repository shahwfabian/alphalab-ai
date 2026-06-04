"""
AlphaLab AI — Settings
API keys, risk parameters, default configurations, and system information.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Settings — AlphaLab AI", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
.stApp{background:#0A0E1A}
[data-testid="stSidebar"]{background:#070B16!important;border-right:1px solid #1E2D4A}
.stButton>button{background:linear-gradient(135deg,#00D4FF18,#00D4FF0A);border:1px solid #00D4FF;color:#00D4FF;font-weight:600;border-radius:6px}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stSelectbox>div>div{background:#0F1628!important;border:1px solid #1E2D4A!important;color:#E8F4FD!important;border-radius:6px!important}
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
    <div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#6B8CAE;letter-spacing:3px;'>MODULE 09</div>
    <div style='font-size:32px;font-weight:700;color:#00D4FF;font-family:JetBrains Mono,monospace;margin-top:6px;'>⚙️ Settings</div>
    <div style='color:#6B8CAE;font-size:14px;margin-top:8px;'>
        Configure API keys, risk parameters, default date ranges, and platform preferences.
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["AI Engine", "Risk Parameters", "Data Defaults", "About AlphaLab"])

# ─── TAB 1: AI ENGINE ─────────────────────────────────────────────────────────

with tab1:
    st.markdown(f"""
    <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:22px;margin-bottom:20px;'>
        <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:14px;'>
        OPENAI API CONFIGURATION
        </div>
    """, unsafe_allow_html=True)

    current_key = st.session_state.get("openai_api_key", "")
    status_color = CYAN if current_key else RED
    status_text  = "✓ Key configured" if current_key else "✗ Not configured (mock mode active)"

    st.markdown(f"""
    <div style='color:{status_color};font-size:13px;margin-bottom:16px;font-family:JetBrains Mono,monospace;'>
    Status: {status_text}
    </div>
    """, unsafe_allow_html=True)

    new_key = st.text_input(
        "OpenAI API Key",
        value=current_key,
        type="password",
        placeholder="sk-...",
        key="settings_api_key",
        help="Your OpenAI API key. Used for Research Assistant and AI explanations. Never shared or logged.",
    )

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("Save API Key", key="save_api_key"):
            st.session_state["openai_api_key"] = new_key.strip()
            if new_key.strip():
                st.success("✅ API key saved for this session.")
            else:
                st.info("API key cleared. Running in mock/demo mode.")
    with c2:
        if current_key and st.button("Clear API Key", key="clear_api_key"):
            st.session_state["openai_api_key"] = ""
            st.success("API key cleared.")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Model provider info
    st.markdown(f"""
    <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:22px;'>
        <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:14px;'>
        AI MODEL CONFIGURATION
        </div>
        <div style='color:{TEXT};font-size:13px;line-height:1.9;'>
            <strong>Current Model:</strong> <span style='color:{CYAN};font-family:JetBrains Mono,monospace;'>GPT-4o Mini</span><br>
            <strong>Provider:</strong> OpenAI<br>
            <strong>Use Case:</strong> Research question analysis, result interpretation, report generation
        </div>
        <div style='margin-top:16px;'>
    """, unsafe_allow_html=True)

    model_option = st.selectbox(
        "AI Model",
        ["gpt-4o-mini (Recommended — Fast & Affordable)", "gpt-4o (Advanced)", "gpt-3.5-turbo (Legacy)"],
        key="settings_model",
        help="Model used for the Research Assistant and AI explanations."
    )

    st.markdown("""
    <div style='color:#6B8CAE;font-size:12px;margin-top:10px;'>
    Model selection is saved for this session. Future versions will support Anthropic Claude and local models (Ollama).
    </div>
    </div></div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:rgba(255,215,0,0.05);border:1px solid {GOLD}44;border-radius:6px;padding:14px;margin-top:16px;color:{GOLD};font-size:12px;'>
    🔒 <strong>Privacy:</strong> Your API key is stored only in Streamlit session state and is never logged, transmitted,
    or stored to disk. It is cleared when you close the browser tab.
    </div>
    """, unsafe_allow_html=True)

# ─── TAB 2: RISK PARAMETERS ───────────────────────────────────────────────────

with tab2:
    st.markdown(f"""
    <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:22px;margin-bottom:20px;'>
        <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:16px;'>
        RISK MODEL PARAMETERS
        </div>
    """, unsafe_allow_html=True)

    current_rf = st.session_state.get("risk_free_rate", 0.05)

    rf_pct = st.number_input(
        "Annual Risk-Free Rate (%)",
        value=float(current_rf * 100),
        min_value=0.0, max_value=20.0, step=0.1,
        key="settings_rf",
        help="Used in Sharpe ratio calculations across Portfolio Optimization and Probability Lab. "
             "Typically set to the current 3-month T-Bill rate.",
    )

    st.markdown(f"""
    <div style='color:#6B8CAE;font-size:12px;margin-top:-8px;margin-bottom:16px;'>
    Current value: <span style='color:{CYAN};font-family:JetBrains Mono,monospace;'>{current_rf*100:.2f}%</span>
    &nbsp;·&nbsp; Common reference rates: US 3M T-Bill (~5.0%), Fed Funds Rate, SOFR
    </div>
    """, unsafe_allow_html=True)

    var_default = st.selectbox(
        "Default VaR Confidence Level",
        [0.90, 0.95, 0.99],
        index=1,
        key="settings_var_conf",
        help="Default confidence level used in Probability Lab VaR calculations.",
    )

    trading_days = st.number_input(
        "Trading Days per Year",
        value=252,
        min_value=200, max_value=365,
        key="settings_trading_days",
        help="Used for annualizing daily statistics. Standard is 252 for US equities.",
    )

    if st.button("Save Risk Parameters", key="save_risk"):
        st.session_state["risk_free_rate"]  = rf_pct / 100.0
        st.session_state["var_conf_default"] = var_default
        st.session_state["trading_days"]    = trading_days
        st.success(f"✅ Saved — Risk-Free Rate: {rf_pct:.2f}% · VaR Confidence: {var_default:.0%} · Trading Days: {trading_days}")

    st.markdown("</div>", unsafe_allow_html=True)

# ─── TAB 3: DATA DEFAULTS ─────────────────────────────────────────────────────

with tab3:
    st.markdown(f"""
    <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:22px;'>
        <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:16px;'>
        DEFAULT DATE RANGE
        </div>
    """, unsafe_allow_html=True)

    import pandas as pd
    from utils.data_loader import DEFAULT_START, DEFAULT_END

    col1, col2 = st.columns(2)
    with col1:
        def_start = st.date_input(
            "Default Start Date",
            value=pd.to_datetime(st.session_state.get("default_start", DEFAULT_START)),
            key="settings_start",
        )
    with col2:
        def_end = st.date_input(
            "Default End Date",
            value=pd.to_datetime(st.session_state.get("default_end", DEFAULT_END)),
            key="settings_end",
        )

    return_type_default = st.selectbox(
        "Default Return Type",
        ["Simple (Arithmetic)", "Log"],
        key="settings_ret_type",
        help="Simple returns are standard for portfolio analysis. Log returns are preferred for statistical modeling.",
    )

    data_source_info = st.selectbox(
        "Data Source",
        ["Yahoo Finance (yfinance) — Default", "Uploaded CSV"],
        key="settings_data_source",
        disabled=True,
        help="Yahoo Finance is the default data source. Upload via Data Upload Lab for custom datasets.",
    )

    if st.button("Save Data Defaults", key="save_data"):
        st.session_state["default_start"]       = str(def_start)
        st.session_state["default_end"]         = str(def_end)
        st.session_state["default_return_type"] = return_type_default
        st.success(f"✅ Defaults saved — {def_start} to {def_end} · {return_type_default} returns")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:22px;margin-top:16px;'>
        <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:14px;'>
        SESSION DATA
        </div>
        <div style='color:{TEXT};font-size:13px;line-height:1.9;'>
            <span style='color:#6B8CAE;'>Chat History:</span> {len(st.session_state.get("chat_history", []))} messages<br>
            <span style='color:#6B8CAE;'>Uploaded Dataset:</span> {"Loaded (" + str(len(st.session_state["uploaded_df"])) + " rows)" if st.session_state.get("uploaded_df") is not None else "None"}<br>
            <span style='color:#6B8CAE;'>Regression Results:</span> {"Available" if st.session_state.get("last_regression_results") else "None"}<br>
            <span style='color:#6B8CAE;'>Portfolio Results:</span> {"Available" if st.session_state.get("last_portfolio_results") else "None"}
        </div>
    """, unsafe_allow_html=True)

    if st.button("🗑 Clear Session Data", key="clear_session"):
        for k in ["chat_history", "uploaded_df", "last_regression_results",
                  "last_portfolio_results", "generated_report_html"]:
            st.session_state[k] = None if "df" in k or "results" in k or "html" in k else []
        st.success("Session data cleared.")
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ─── TAB 4: ABOUT ─────────────────────────────────────────────────────────────

with tab4:
    st.markdown(f"""
    <div style='background:{PANEL};border:1px solid {GRID};border-top:3px solid {BLUE};border-radius:8px;padding:28px;'>
        <div style='font-family:JetBrains Mono,monospace;font-size:24px;color:{BLUE};letter-spacing:3px;margin-bottom:6px;'>
        ⬡ ALPHALAB AI
        </div>
        <div style='color:#6B8CAE;font-size:12px;letter-spacing:2px;margin-bottom:20px;'>
        AI-POWERED STATISTICAL RESEARCH COPILOT
        </div>
        <div style='color:{TEXT};font-size:13px;line-height:2.1;'>
            <strong style='color:{BLUE};'>Version:</strong> 1.0.0 MVP<br>
            <strong style='color:{BLUE};'>Stack:</strong> Python · Streamlit · statsmodels · scipy · plotly · yfinance · OpenAI<br>
            <strong style='color:{BLUE};'>Design:</strong> Bloomberg Terminal meets AI Research Workstation<br>
            <strong style='color:{BLUE};'>License:</strong> MIT
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Module index
    st.markdown(f"""
    <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:22px;'>
        <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:16px;'>
        MODULE REGISTRY
        </div>
    """, unsafe_allow_html=True)

    modules = [
        ("Home",                     "Landing page with module overview and example questions"),
        ("Research Assistant",       "Natural-language question → statistical method mapping (OpenAI / mock)"),
        ("Regression Lab",           "OLS regression via statsmodels with full diagnostics and interpretation"),
        ("Statistical Inference Lab","One-sample & two-sample t-tests, confidence intervals"),
        ("Probability Lab",          "Return distribution, VaR, CVaR, drawdown probability modeling"),
        ("Portfolio Optimization",   "Mean-Variance Optimization, Efficient Frontier via scipy"),
        ("Correlation Explorer",     "Pearson/Spearman/Kendall heatmaps, rolling correlation, diversification"),
        ("Data Upload Lab",          "CSV upload, auto-exploration, missing value analysis, recommendations"),
        ("Research Reports",         "One-click professional HTML report generation and export"),
        ("Settings",                 "API keys, risk parameters, data defaults (this page)"),
    ]

    for i, (name, desc) in enumerate(modules):
        st.markdown(f"""
        <div style='display:flex;padding:10px 0;border-bottom:1px solid {GRID};'>
            <div style='color:#6B8CAE;font-family:JetBrains Mono,monospace;font-size:12px;width:40px;'>
            {str(i).zfill(2)}
            </div>
            <div style='color:{CYAN};font-family:JetBrains Mono,monospace;font-size:12px;width:220px;'>
            {name}
            </div>
            <div style='color:{TEXT};font-size:12px;'>
            {desc}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Theme explanation
    st.markdown(f"""
    <div style='background:{PANEL};border:1px solid {GRID};border-radius:8px;padding:22px;'>
        <div style='color:{BLUE};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:14px;'>
        DESIGN SYSTEM
        </div>
        <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:12px;'>
            <div style='background:#0A0E1A;border:1px solid #1E2D4A;border-radius:6px;padding:12px;text-align:center;'>
                <div style='color:#6B8CAE;font-size:10px;letter-spacing:1px;'>NAVY BG</div>
                <div style='color:#00D4FF;font-family:JetBrains Mono,monospace;font-size:11px;margin-top:6px;'>#0A0E1A</div>
            </div>
            <div style='background:#0F1628;border:1px solid #1E2D4A;border-radius:6px;padding:12px;text-align:center;'>
                <div style='color:#6B8CAE;font-size:10px;letter-spacing:1px;'>PANEL</div>
                <div style='color:#00D4FF;font-family:JetBrains Mono,monospace;font-size:11px;margin-top:6px;'>#0F1628</div>
            </div>
            <div style='background:#00D4FF22;border:1px solid #00D4FF;border-radius:6px;padding:12px;text-align:center;'>
                <div style='color:#6B8CAE;font-size:10px;letter-spacing:1px;'>ELECTRIC BLUE</div>
                <div style='color:#00D4FF;font-family:JetBrains Mono,monospace;font-size:11px;margin-top:6px;'>#00D4FF</div>
            </div>
            <div style='background:#FFD70022;border:1px solid #FFD700;border-radius:6px;padding:12px;text-align:center;'>
                <div style='color:#6B8CAE;font-size:10px;letter-spacing:1px;'>SIGNAL GOLD</div>
                <div style='color:#FFD700;font-family:JetBrains Mono,monospace;font-size:11px;margin-top:6px;'>#FFD700</div>
            </div>
        </div>
        <div style='color:#6B8CAE;font-size:12px;margin-top:14px;line-height:1.7;'>
        AlphaLab AI uses a Bloomberg Terminal-inspired dark palette. Deep navy backgrounds minimize eye strain
        for long research sessions. Electric blue accents draw attention to key metrics and interactive elements.
        Gold signals statistical significance and alerts. Red marks risk thresholds and rejection regions.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Disclaimer
    st.markdown(f"""
    <div style='background:rgba(255,215,0,0.04);border:1px solid {GOLD}44;border-radius:8px;padding:20px;'>
        <div style='color:{GOLD};font-family:JetBrains Mono,monospace;font-size:11px;letter-spacing:2px;margin-bottom:12px;'>
        LEGAL DISCLAIMER
        </div>
        <div style='color:#6B8CAE;font-size:12px;line-height:1.9;'>
        AlphaLab AI is an <strong style='color:{TEXT};'>educational and research tool only</strong>.
        It does not constitute financial advice, investment recommendations, trading signals, or
        guarantees of any kind regarding future performance.<br><br>
        All statistical outputs are estimates with inherent uncertainty. Past performance of any
        financial instrument analyzed by AlphaLab does not imply future results. Models make
        simplifying assumptions that may not hold in real markets.<br><br>
        Users are solely responsible for their own investment decisions. Consult a qualified
        financial professional before making any investment.
        </div>
    </div>
    """, unsafe_allow_html=True)
