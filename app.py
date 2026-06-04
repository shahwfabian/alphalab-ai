"""
AlphaLab AI
AI-Powered Statistical Research Copilot
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.styles import inject_css
from utils.modules import MODULES, MODULE_MAP, detect_intent, run_analysis_from_chat
from utils.ai_explainer import get_openai_response, get_mock_response

st.set_page_config(
    page_title="AlphaLab AI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_css()

# ── Session defaults ──────────────────────────────────────────────────────────
for k, v in {
    "view":           "home",
    "active_module":  None,
    "chat_messages":  {},
    "openai_api_key": "",
    "risk_free_rate": 0.05,
    "default_start":  "2020-01-01",
    "default_end":    "2024-12-31",
    "uploaded_df":    None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── AI response dispatcher ────────────────────────────────────────────────────

def get_ai_response(module: dict, user_message: str) -> str:
    """Get a contextual AI response for a module chat."""
    api_key = st.session_state.get("openai_api_key", "")

    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            history = st.session_state.chat_messages.get(module["id"], [])
            messages = [{"role": "system", "content": module["prompt"]}]
            for m in history[-10:]:           # last 10 turns for context
                messages.append({"role": m["role"], "content": m["content"]})
            messages.append({"role": "user", "content": user_message})
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
                max_tokens=700,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"AI error: {e}. Falling back to demo mode.\n\n" + _mock_response(module, user_message)
    else:
        return _mock_response(module, user_message)


def _mock_response(module: dict, user_message: str) -> str:
    """Contextual mock response when no API key is set."""
    from utils.ai_explainer import classify_question, MOCK_RESPONSES
    cat  = classify_question(user_message)
    data = MOCK_RESPONSES.get(cat, MOCK_RESPONSES["regression"])
    return (
        f"**Method:** {data['method']}\n\n"
        f"**Why this fits:** {data['why']}\n\n"
        f"**Inputs needed:** {data['inputs']}\n\n"
        f"**Assumptions:** {data['assumptions']}\n\n"
        f"**Limitations:** {data['limitations']}\n\n"
        f"*Add an OpenAI API key in Settings for full conversational AI.*"
    )


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
    # Header
    st.markdown("""
    <div style="padding: 2.5rem 0 2rem 0;">
        <div style="font-size: 0.7rem; color: #333; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.6rem;">Statistical Research Copilot</div>
        <h1 style="font-size: 2rem; font-weight: 600; color: #f0f0f0; letter-spacing: -0.03em; line-height: 1.15; margin: 0 0 0.65rem 0;">
            AlphaLab AI
        </h1>
        <p style="font-size: 0.95rem; color: #4a4a4a; max-width: 480px; line-height: 1.65; margin: 0;">
            Convert research questions into quantitative analysis, statistical interpretation, and professional reports.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Modules grid
    st.markdown('<p style="font-size:0.7rem; color:#333; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.5rem;">Choose a module</p>', unsafe_allow_html=True)

    # Render 2-column grid of clickable module cards
    cols = st.columns(2, gap="medium")
    for i, mod in enumerate(MODULES):
        with cols[i % 2]:
            # Use a button for the card — clicking opens the chat
            clicked = st.button(
                f"**{mod['name']}**\n\n{mod['desc']}",
                key=f"mod_{mod['id']}",
                use_container_width=True,
            )
            if clicked:
                open_module(mod["id"])
                st.rerun()

    st.divider()

    # Example questions
    st.markdown('<p style="font-size:0.7rem; color:#333; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.75rem;">Or try a question</p>', unsafe_allow_html=True)

    example_qs = [
        ("Does QQQ explain NVDA returns better than SPY?",         "regression"),
        ("What is the probability of SPY dropping 5% in 30 days?", "probability"),
        ("Build the highest Sharpe portfolio from SPY, QQQ, GLD, TLT", "portfolio"),
        ("Show me the correlation matrix for SPY, QQQ, GLD, BTC-USD", "correlation"),
        ("Test whether SPY mean daily return is different from zero",   "inference"),
        ("Explain the difference between R² and Adjusted R²",          "research"),
    ]

    for question, module_id in example_qs:
        if st.button(f"↗  {question}", key=f"q_{question[:20]}", use_container_width=False):
            open_module(module_id)
            # Pre-seed the question as first user message
            mod = MODULE_MAP[module_id]
            msgs = st.session_state.chat_messages[module_id]
            msgs.append({"role": "user", "content": question})
            with st.spinner("Thinking..."):
                intent = detect_intent(question, module_id)
                if intent != "conversational":
                    result = run_analysis_from_chat(intent, question)
                    if result.get("ran"):
                        ai_text = result["summary"]
                    else:
                        ai_text = get_ai_response(mod, question)
                else:
                    ai_text = get_ai_response(mod, question)
            msgs.append({"role": "assistant", "content": ai_text,
                         "fig": result.get("fig") if intent != "conversational" and result.get("ran") else None,
                         "df":  result.get("df")  if intent != "conversational" and result.get("ran") else None})
            st.rerun()

    # Footer
    st.markdown("""
    <p style="font-size:0.75rem; color:#252525; margin-top:2.5rem; line-height:1.7;">
    For research and educational use only. Not financial advice.
    &nbsp;·&nbsp;
    <a href="https://github.com/shahwfabian/alphalab-ai" style="color:#333; text-decoration:none;">GitHub</a>
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
    col_back, col_title, col_settings = st.columns([1, 6, 1])
    with col_back:
        if st.button("← Home"):
            go_home(); st.rerun()
    with col_title:
        st.markdown(f"""
        <div style="padding:0.4rem 0;">
            <span style="font-size:1rem; font-weight:600; color:#f0f0f0;">{mod['name']}</span>
            <span style="font-size:0.8rem; color:#333; margin-left:0.75rem;">{mod['desc']}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_settings:
        if st.button("⚙", help="Settings"):
            st.session_state["show_settings"] = not st.session_state.get("show_settings", False)

    # Inline settings panel
    if st.session_state.get("show_settings", False):
        with st.expander("Settings", expanded=True):
            key_in = st.text_input("OpenAI API key", value=st.session_state.openai_api_key,
                                   type="password", placeholder="sk-...")
            c1, c2, _ = st.columns([1, 1, 4])
            with c1:
                if st.button("Save key"):
                    st.session_state.openai_api_key = key_in.strip()
                    st.success("Saved.")
            with c2:
                if st.button("Clear key"):
                    st.session_state.openai_api_key = ""
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
        with st.chat_message(msg["role"], avatar="⬡" if msg["role"] == "assistant" else None):
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
