"""AlphaLab AI — Settings"""

import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.styles import inject_css, page_header, info_box
from utils.data_loader import DEFAULT_START, DEFAULT_END

st.set_page_config(page_title="Settings — AlphaLab AI", page_icon="⬡", layout="wide")
inject_css()

page_header("Settings", "Configure API keys, risk parameters, and data defaults.")

tab1, tab2, tab3, tab4 = st.tabs(["AI Engine", "Risk Parameters", "Data Defaults", "About"])

# ── AI ENGINE ─────────────────────────────────────────────────────────────────
with tab1:
    current_key = st.session_state.get("openai_api_key", "")
    st.markdown(f"""
    <p style="font-size:0.8rem; color:{'#22c55e' if current_key else '#444'}; margin-bottom:1rem;">
    {'● Connected' if current_key else '● Not configured — running in demo mode'}
    </p>
    """, unsafe_allow_html=True)

    new_key = st.text_input("OpenAI API key", value=current_key, type="password",
                            placeholder="sk-...", help="Stored in session state only. Never logged or persisted.")
    c1, c2, _ = st.columns([1, 1, 4])
    with c1:
        if st.button("Save", key="save_key"):
            st.session_state["openai_api_key"] = new_key.strip()
            st.success("Saved." if new_key.strip() else "Cleared — demo mode active.")
    with c2:
        if current_key and st.button("Clear", key="clear_key"):
            st.session_state["openai_api_key"] = ""
            st.rerun()

    st.divider()
    st.selectbox("Model", ["gpt-4o-mini (Recommended)", "gpt-4o", "gpt-3.5-turbo"],
                 key="settings_model", help="Model used in Research Assistant and AI explanations.")
    info_box("Your API key is stored only in Streamlit session state and cleared when the browser tab closes.", "info")

# ── RISK PARAMETERS ───────────────────────────────────────────────────────────
with tab2:
    rf_pct = st.number_input("Annual risk-free rate (%)",
                             value=float(st.session_state.get("risk_free_rate", 0.05)) * 100,
                             min_value=0.0, max_value=20.0, step=0.1,
                             help="Used in Sharpe ratio calculations. Typically the 3-month T-Bill rate.")
    var_conf = st.selectbox("Default VaR confidence level", [0.90, 0.95, 0.99], index=1)
    trading_days = st.number_input("Trading days per year", value=252, min_value=200, max_value=365,
                                   help="Used to annualize daily statistics.")

    if st.button("Save Risk Parameters", type="primary"):
        st.session_state["risk_free_rate"]   = rf_pct / 100.0
        st.session_state["var_conf_default"] = var_conf
        st.session_state["trading_days"]     = trading_days
        st.success(f"Saved — RF {rf_pct:.2f}% · VaR {var_conf:.0%} · {trading_days} trading days")

# ── DATA DEFAULTS ─────────────────────────────────────────────────────────────
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        def_start = st.date_input("Default start date",
                                  value=pd.to_datetime(st.session_state.get("default_start", DEFAULT_START)))
    with c2:
        def_end = st.date_input("Default end date",
                                value=pd.to_datetime(st.session_state.get("default_end", DEFAULT_END)))
    ret_type = st.selectbox("Default return type", ["Simple (Arithmetic)", "Log"])

    if st.button("Save Data Defaults", type="primary"):
        st.session_state["default_start"]       = str(def_start)
        st.session_state["default_end"]         = str(def_end)
        st.session_state["default_return_type"] = ret_type
        st.success(f"Saved — {def_start} to {def_end} · {ret_type}")

    st.divider()
    st.markdown(f"""
    <div style="font-size:0.8rem; color:#555; line-height:2;">
    Chat history: {len(st.session_state.get('chat_history', []))} messages<br>
    Uploaded dataset: {'Loaded (' + str(len(st.session_state['uploaded_df'])) + ' rows)' if st.session_state.get('uploaded_df') is not None else 'None'}<br>
    Regression results: {'Available' if st.session_state.get('last_regression_results') else 'None'}<br>
    Portfolio results: {'Available' if st.session_state.get('last_portfolio_results') else 'None'}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear Session Data"):
        for k in ["chat_history", "uploaded_df", "last_regression_results", "last_portfolio_results", "generated_report_html"]:
            st.session_state[k] = [] if k == "chat_history" else None
        st.success("Session data cleared.")
        st.rerun()

# ── ABOUT ─────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("""
    <div style="padding:1.5rem 0;">
        <div style="font-size:1.1rem; font-weight:600; color:#f0f0f0; margin-bottom:0.25rem;">⬡ AlphaLab AI</div>
        <div style="font-size:0.8rem; color:#444; margin-bottom:1.5rem;">AI-Powered Statistical Research Copilot · v1.0.0</div>
    </div>
    """, unsafe_allow_html=True)

    modules = [
        ("Home",                  "Landing page with module overview"),
        ("Research Assistant",    "NL question → method identification (OpenAI / mock)"),
        ("Regression Lab",        "OLS regression via statsmodels with full diagnostics"),
        ("Statistical Inference", "t-tests and confidence intervals"),
        ("Probability Lab",       "Distribution, VaR, CVaR, drawdown probability"),
        ("Portfolio Optimization","Mean-Variance Optimization via scipy"),
        ("Correlation Explorer",  "Heatmaps, rolling correlation, diversification"),
        ("Data Upload",           "CSV auto-exploration and recommendations"),
        ("Research Reports",      "HTML report generation and export"),
        ("Settings",              "Configuration (this page)"),
    ]

    for i, (name, desc) in enumerate(modules):
        st.markdown(f"""
        <div style="display:flex; padding:0.6rem 0; border-bottom:1px solid #1a1a1a;">
            <span style="font-size:0.75rem; color:#333; font-family:monospace; width:2rem;">{str(i).zfill(2)}</span>
            <span style="font-size:0.825rem; color:#818cf8; width:200px;">{name}</span>
            <span style="font-size:0.825rem; color:#555;">{desc}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    info_box("AlphaLab AI is a research and educational tool. It does not provide financial advice, investment recommendations, or performance guarantees. All statistical outputs carry uncertainty.", "warning")
