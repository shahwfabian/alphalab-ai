"""AlphaLab AI — Research Assistant"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.styles import inject_css, page_header, info_box
from utils.ai_explainer import get_research_response

st.set_page_config(page_title="Research Assistant — AlphaLab AI", page_icon="⬡", layout="wide")
inject_css()

page_header("Research Assistant", "Ask a research question. AlphaLab identifies the right method and structures your analysis.")

api_key = st.session_state.get("openai_api_key", "")
if not api_key:
    info_box("Running in demo mode — add your OpenAI API key in <b>Settings</b> to enable live AI responses.", "info")

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick starters ────────────────────────────────────────────────────────────
st.markdown('<p style="font-size:0.7rem; color:#444; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.75rem;">Quick start</p>', unsafe_allow_html=True)

examples = [
    "Does QQQ explain NVDA returns better than SPY?",
    "Is momentum statistically significant?",
    "What is the probability of a 10% drawdown in 30 days?",
    "Build the highest Sharpe portfolio from these assets.",
    "Test whether mean SPY return differs from zero.",
    "Which correlation method is best for financial returns?",
]

cols = st.columns(3)
for i, q in enumerate(examples):
    with cols[i % 3]:
        if st.button(q, key=f"eg_{i}", use_container_width=True):
            st.session_state["prefill_question"] = q

st.markdown("<br>", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill_question", "")
question = st.text_area(
    "Your research question",
    value=prefill,
    height=90,
    placeholder="e.g. Does the momentum factor explain NVDA excess returns after controlling for market beta?",
)

c1, c2, _ = st.columns([1, 1, 5])
with c1:
    run = st.button("Analyze", use_container_width=True)
with c2:
    if st.button("Clear", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()

# ── Run ───────────────────────────────────────────────────────────────────────
if run and question.strip():
    with st.spinner("Analyzing..."):
        resp = get_research_response(question.strip(), api_key or None)
        st.session_state["chat_history"].append({"question": question.strip(), "response": resp})

# ── History ───────────────────────────────────────────────────────────────────
history = st.session_state.get("chat_history", [])

if history:
    st.divider()
    for entry in reversed(history):
        q = entry["question"]
        r = entry["response"]

        st.markdown(f"""
        <div style="margin-bottom:0.5rem;">
            <span style="font-size:0.7rem; color:#444; text-transform:uppercase; letter-spacing:0.08em;">Question</span>
            <p style="font-size:0.95rem; color:#c0c0c0; font-style:italic; margin:0.3rem 0 1.25rem 0;">"{q}"</p>
        </div>
        """, unsafe_allow_html=True)

        if r.get("source") == "mock":
            info_box("Demo response — add an OpenAI API key in Settings for live analysis.", "info")

        col1, col2 = st.columns([3, 2])

        with col1:
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
                <div style="font-size:0.7rem; color:#444; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.4rem;">Method</div>
                <div style="font-size:1rem; font-weight:500; color:#818cf8;">{r.get('method', '—')}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Why this method fits"):
                st.markdown(r.get("why", "—"))
            with st.expander("Inputs needed"):
                st.markdown(r.get("inputs", "—"))
            with st.expander("Assumptions"):
                st.markdown(r.get("assumptions", "—"))

        with col2:
            with st.expander("Expected output", expanded=True):
                st.markdown(r.get("output", "—"))
            with st.expander("Limitations"):
                st.markdown(r.get("limitations", "—"))

            module = r.get("suggested_module", "")
            if module:
                st.markdown(f"""
                <div style="background:#161616; border:1px solid #1f1f1f; border-radius:8px; padding:0.875rem 1rem; margin-top:0.75rem;">
                    <div style="font-size:0.7rem; color:#444; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.3rem;">Suggested module</div>
                    <div style="font-size:0.875rem; color:#818cf8; font-weight:500;">{module}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
else:
    st.markdown("""
    <div style="text-align:center; padding:4rem 0; color:#2a2a2a;">
        <div style="font-size:2rem; margin-bottom:0.75rem;">⬡</div>
        <div style="font-size:0.875rem;">Enter a question above to begin.</div>
    </div>
    """, unsafe_allow_html=True)
