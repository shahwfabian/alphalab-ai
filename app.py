"""
AlphaLab AI
AI-Powered Statistical Research Copilot
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.styles import inject_css
from utils.modules import MODULES, MODULE_MAP, detect_intent, run_analysis_from_chat
from utils.ai_explainer import get_best_response

st.set_page_config(
    page_title="AlphaLab AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()

# ── Session defaults ──────────────────────────────────────────────────────────
for k, v in {
    "view":              "home",
    "active_module":     None,
    "chat_messages":     {},
    "anthropic_api_key": "",
    "openai_api_key":    "",
    "risk_free_rate":    0.05,
    "default_start":     "2020-01-01",
    "default_end":       "2024-12-31",
    "uploaded_df":       None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── AI response dispatcher ────────────────────────────────────────────────────

def get_ai_response(module: dict, user_message: str) -> str:
    """Route to the best available AI: Claude → OpenAI → intelligent fallback."""
    history = st.session_state.chat_messages.get(module["id"], [])
    return get_best_response(module["id"], history, user_message)


# ── Navigation helpers ────────────────────────────────────────────────────────

def open_module(module_id: str):
    mod = MODULE_MAP[module_id]
    st.session_state.view          = "chat"
    st.session_state.active_module = module_id
    # Seed welcome message if first time opening
    if module_id not in st.session_state.chat_messages:
        st.session_state.chat_messages[module_id] = [
            {"role": "assistant", "content": mod["welcome"]}
        ]

def go_home():
    st.session_state.view = "home"


# ══════════════════════════════════════════════════════════════════════════════
# HOME VIEW
# ══════════════════════════════════════════════════════════════════════════════

def render_home():
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding: 3rem 0 2.25rem 0;">
        <div style="font-size: 0.65rem; color: #3a3a3a; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 0.75rem; font-weight: 500;">Statistical Research Copilot</div>
        <h1 style="font-size: 2.1rem; font-weight: 600; color: #ebebeb; letter-spacing: -0.04em; line-height: 1.1; margin: 0 0 0.75rem 0;">
            AlphaLab AI
        </h1>
        <p style="font-size: 0.9rem; color: #3d3d3d; max-width: 460px; line-height: 1.75; margin: 0;">
            Turn research questions into statistical analysis, visualizations, and professional reports.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Module grid ───────────────────────────────────────────────────────────
    st.markdown('<p style="font-size:0.65rem; color:#2e2e2e; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.75rem; font-weight:500;">Modules</p>', unsafe_allow_html=True)

    cols = st.columns(2, gap="medium")
    for i, mod in enumerate(MODULES):
        with cols[i % 2]:
            if st.button(
                f"**{mod['name']}**\n\n{mod['desc']}",
                key=f"mod_{mod['id']}",
                use_container_width=True,
            ):
                open_module(mod["id"])
                st.rerun()

    st.divider()

    # ── Example questions ─────────────────────────────────────────────────────
    st.markdown('<p style="font-size:0.65rem; color:#2e2e2e; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.75rem; font-weight:500;">Try a question</p>', unsafe_allow_html=True)

    example_qs = [
        ("Does QQQ explain NVDA returns better than SPY?",            "regression"),
        ("What is the probability of SPY dropping 5% in 30 days?",    "probability"),
        ("Build the highest Sharpe portfolio from SPY, QQQ, GLD, TLT","portfolio"),
        ("Show correlation matrix for SPY, QQQ, GLD, BTC-USD",        "correlation"),
        ("Test whether SPY mean daily return differs from zero",       "inference"),
        ("Explain the difference between R² and Adjusted R²",         "research"),
    ]

    for question, module_id in example_qs:
        if st.button(f"↗  {question}", key=f"q_{question[:25]}", use_container_width=False):
            open_module(module_id)
            mod  = MODULE_MAP[module_id]
            msgs = st.session_state.chat_messages[module_id]
            msgs.append({"role": "user", "content": question})
            result   = {"ran": False}
            fig_data = None
            df_data  = None
            with st.spinner("Thinking…"):
                intent = detect_intent(question, module_id)
                if intent != "conversational":
                    result = run_analysis_from_chat(intent, question)
                    if result.get("ran"):
                        ai_text  = result["summary"]
                        fig_data = result.get("fig")
                        df_data  = result.get("df")
                    else:
                        ai_text = get_ai_response(mod, question)
                else:
                    ai_text = get_ai_response(mod, question)
            msgs.append({"role": "assistant", "content": ai_text,
                         "fig": fig_data, "df": df_data})
            st.rerun()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <p style="font-size:0.72rem; color:#1e1e1e; margin-top:3rem; line-height:1.7;">
    For research and educational use only — not financial advice.
    &nbsp;·&nbsp;
    <a href="https://github.com/shahwfabian/alphalab-ai" style="color:#2e2e2e; text-decoration:none;">GitHub</a>
    </p>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CHAT VIEW
# ══════════════════════════════════════════════════════════════════════════════

def render_chat():
    mod_id = st.session_state.active_module
    mod    = MODULE_MAP.get(mod_id)
    if not mod:
        go_home(); st.rerun(); return

    messages = st.session_state.chat_messages.get(mod_id, [])

    # ── Top bar ───────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    /* Nav buttons — ghost style, no background */
    [data-testid="stButton"][data-key="btn_home"] > button,
    [data-testid="stButton"][data-key="btn_settings"] > button {
        background: transparent !important;
        border: none !important;
        color: #444 !important;
        font-size: 0.8rem !important;
        padding: 0.25rem 0.5rem !important;
        min-height: unset !important;
    }
    [data-testid="stButton"][data-key="btn_home"] > button:hover,
    [data-testid="stButton"][data-key="btn_settings"] > button:hover {
        color: #aaa !important;
        background: transparent !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col_back, col_title, col_settings = st.columns([1, 6, 1])
    with col_back:
        if st.button("← Home", key="btn_home"):
            go_home(); st.rerun()
    with col_title:
        st.markdown(f"""
        <div style="padding:0.4rem 0;">
            <span style="font-size:0.95rem; font-weight:600; color:#e5e5e5;">{mod['name']}</span>
            <span style="font-size:0.78rem; color:#383838; margin-left:0.75rem;">{mod['desc']}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_settings:
        if st.button("⚙", key="btn_settings", help="Settings"):
            st.session_state["show_settings"] = not st.session_state.get("show_settings", False)

    # Inline settings panel
    if st.session_state.get("show_settings", False):
        with st.expander("Settings", expanded=True):
            # Detect which provider is active
            has_anthropic = bool(st.session_state.get("anthropic_api_key", "").strip()
                                 or __import__("os").environ.get("ANTHROPIC_API_KEY", ""))
            has_openai    = bool(st.session_state.get("openai_api_key", "").strip()
                                 or __import__("os").environ.get("OPENAI_API_KEY", ""))
            status = "● Claude connected" if has_anthropic else ("● OpenAI connected" if has_openai else "● No AI key — using built-in answers")
            color  = "#22c55e" if (has_anthropic or has_openai) else "#f59e0b"
            st.markdown(f'<p style="font-size:0.8rem; color:{color}; margin-bottom:0.5rem;">{status}</p>', unsafe_allow_html=True)

            ant_in = st.text_input("Anthropic API key (Claude) — recommended",
                                   value=st.session_state.anthropic_api_key,
                                   type="password", placeholder="sk-ant-...")
            oai_in = st.text_input("OpenAI API key (GPT-4o-mini) — fallback",
                                   value=st.session_state.openai_api_key,
                                   type="password", placeholder="sk-...")
            c1, c2, _ = st.columns([1, 1, 4])
            with c1:
                if st.button("Save keys"):
                    st.session_state.anthropic_api_key = ant_in.strip()
                    st.session_state.openai_api_key    = oai_in.strip()
                    st.success("Saved.")
                    st.rerun()
            with c2:
                if st.button("Clear keys"):
                    st.session_state.anthropic_api_key = ""
                    st.session_state.openai_api_key    = ""
                    st.rerun()
            rf = st.number_input("Risk-free rate (%)", value=st.session_state.risk_free_rate * 100,
                                 min_value=0.0, max_value=20.0, step=0.1)
            if st.button("Save rate"):
                st.session_state.risk_free_rate = rf / 100.0
                st.success("Saved.")

    st.divider()

    # ── Starter prompts (shown only if only welcome message) ─────────────────
    if len(messages) == 1:
        st.markdown('<p style="font-size:0.75rem; color:#333; margin-bottom:0.5rem;">Try asking:</p>', unsafe_allow_html=True)
        starter_cols = st.columns(2)
        for i, starter in enumerate(mod.get("starters", [])):
            with starter_cols[i % 2]:
                if st.button(starter, key=f"start_{i}", use_container_width=True):
                    messages.append({"role": "user", "content": starter})
                    with st.spinner("Thinking..."):
                        intent = detect_intent(starter, mod_id)
                        if intent != "conversational":
                            result = run_analysis_from_chat(intent, starter)
                            if result.get("ran"):
                                ai_text = result["summary"]
                                fig_data = result.get("fig")
                                df_data  = result.get("df")
                            else:
                                ai_text  = get_ai_response(mod, starter)
                                fig_data = None; df_data = None
                        else:
                            ai_text  = get_ai_response(mod, starter)
                            fig_data = None; df_data = None
                    messages.append({"role": "assistant", "content": ai_text,
                                     "fig": fig_data, "df": df_data})
                    st.session_state.chat_messages[mod_id] = messages
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Message history ───────────────────────────────────────────────────────
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("fig"):
                st.plotly_chart(msg["fig"], use_container_width=True)
            if msg.get("df") is not None:
                st.dataframe(msg["df"], use_container_width=True, hide_index=True)

    # ── Chat input ────────────────────────────────────────────────────────────
    user_input = st.chat_input(f"Ask {mod['name']}...")

    if user_input:
        messages.append({"role": "user", "content": user_input})
        st.session_state.chat_messages[mod_id] = messages

        with st.spinner(""):
            intent = detect_intent(user_input, mod_id)
            fig_data = None
            df_data  = None

            if intent != "conversational":
                result = run_analysis_from_chat(intent, user_input)
                if result.get("ran"):
                    ai_text  = result["summary"]
                    fig_data = result.get("fig")
                    df_data  = result.get("df")
                else:
                    # Analysis failed — fall back to AI explanation
                    ai_text = get_ai_response(mod, user_input)
                    if result.get("summary"):
                        ai_text = result["summary"] + "\n\n" + ai_text
            else:
                ai_text = get_ai_response(mod, user_input)

        messages.append({"role": "assistant", "content": ai_text,
                         "fig": fig_data, "df": df_data})
        st.session_state.chat_messages[mod_id] = messages
        st.rerun()

    # ── Clear chat button ─────────────────────────────────────────────────────
    if len(messages) > 1:
        if st.button("Clear conversation", key="clear_chat"):
            st.session_state.chat_messages[mod_id] = [
                {"role": "assistant", "content": mod["welcome"]}
            ]
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.view == "home":
    render_home()
else:
    render_chat()
