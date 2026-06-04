"""
AlphaLab AI — Research Assistant
Natural-language statistical research interface powered by OpenAI (with mock fallback).
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ai_explainer import get_research_response, MODULE_MAP

st.set_page_config(page_title="Research Assistant — AlphaLab AI", page_icon="🤖", layout="wide")

# Inject shared style
st.markdown("""
<style>
.stApp { background: #0A0E1A; }
[data-testid="stSidebar"] { background: #070B16 !important; border-right: 1px solid #1E2D4A; }
.stButton > button { background: linear-gradient(135deg,#00D4FF18,#00D4FF0A); border:1px solid #00D4FF; color:#00D4FF; font-weight:600; border-radius:6px; }
.stTextInput > div > div > input { background:#0F1628 !important; border:1px solid #1E2D4A !important; color:#E8F4FD !important; }
.stTextArea textarea { background:#0F1628 !important; border:1px solid #1E2D4A !important; color:#E8F4FD !important; border-radius:6px !important; }
::-webkit-scrollbar { width:6px; } ::-webkit-scrollbar-thumb { background:#1E2D4A; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown("""
<div style='padding:30px 0 10px 0;'>
    <div style='font-family:JetBrains Mono,monospace; font-size:11px; color:#6B8CAE; letter-spacing:3px;'>MODULE 01</div>
    <div style='font-size:32px; font-weight:700; color:#00D4FF; font-family:JetBrains Mono,monospace; margin-top:6px;'>🤖 Research Assistant</div>
    <div style='color:#6B8CAE; font-size:14px; margin-top:8px;'>Ask any statistical or quantitative research question. AlphaLab will identify the right method and structure your analysis.</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ─── AI Status ───────────────────────────────────────────────────────────────

api_key = st.session_state.get("openai_api_key", "")
if api_key:
    st.success("🟢 AI Engine connected — responses powered by OpenAI GPT-4o Mini")
else:
    st.info("🔵 Running in demo mode with structured mock responses. Add your OpenAI API key in **Settings** for live AI responses.")

st.markdown("<br>", unsafe_allow_html=True)

# ─── Suggested Questions ─────────────────────────────────────────────────────

st.markdown("**Try one of these questions:**")
example_questions = [
    "Does QQQ explain NVDA returns better than SPY?",
    "Is momentum statistically significant?",
    "What is the probability of a 10% drawdown in 30 days?",
    "Build the highest Sharpe portfolio from these assets.",
    "Test whether the mean return of SPY is significantly different from zero.",
    "Which correlation method is best for financial returns?",
]

cols = st.columns(3)
for i, q in enumerate(example_questions):
    with cols[i % 3]:
        if st.button(q, key=f"eg_{i}", use_container_width=True):
            st.session_state["prefill_question"] = q

# ─── Input Area ──────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
prefill = st.session_state.pop("prefill_question", "")

question = st.text_area(
    "Enter your research question",
    value=prefill,
    height=100,
    placeholder="Example: Does the Fama-French momentum factor explain NVDA excess returns after controlling for market beta?",
)

col_send, col_clear = st.columns([1, 5])
with col_send:
    run_analysis = st.button("Analyze", use_container_width=True)
with col_clear:
    if st.button("Clear History", use_container_width=False):
        st.session_state["chat_history"] = []
        st.rerun()

# ─── Analysis ────────────────────────────────────────────────────────────────

if run_analysis and question.strip():
    with st.spinner("Analyzing your research question..."):
        response = get_research_response(question.strip(), api_key or None)
        st.session_state["chat_history"].append({"question": question.strip(), "response": response})

# ─── Display History ─────────────────────────────────────────────────────────

history = st.session_state.get("chat_history", [])

if history:
    st.markdown("---")
    for i, entry in enumerate(reversed(history)):
        q = entry["question"]
        r = entry["response"]

        st.markdown(f"""
        <div style='background:#0F1628; border:1px solid #1E2D4A; border-radius:8px; padding:18px; margin-bottom:24px;'>
            <div style='color:#6B8CAE; font-size:11px; font-family:JetBrains Mono,monospace; letter-spacing:2px; margin-bottom:8px;'>RESEARCH QUESTION</div>
            <div style='color:#E8F4FD; font-size:15px; font-style:italic; font-weight:500;'>"{q}"</div>
        </div>
        """, unsafe_allow_html=True)

        if r.get("source") == "mock":
            st.markdown("""
            <div style='background:rgba(255,215,0,0.05); border:1px solid #FFD70044; border-radius:5px; padding:8px 14px; color:#FFD700; font-size:12px; margin-bottom:16px;'>
                📋 Demo mode response — Add OpenAI API key in Settings for live AI analysis
            </div>
            """, unsafe_allow_html=True)

        cols = st.columns([3, 2])

        with cols[0]:
            # Method card
            st.markdown(f"""
            <div style='background:rgba(0,212,255,0.05); border:1px solid #00D4FF33; border-radius:8px; padding:18px; margin-bottom:14px;'>
                <div style='color:#00D4FF; font-family:JetBrains Mono,monospace; font-size:11px; letter-spacing:2px; margin-bottom:6px;'>METHOD SELECTED</div>
                <div style='color:#E8F4FD; font-size:16px; font-weight:700;'>{r.get('method', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Why This Method Fits", expanded=True):
                st.markdown(r.get("why", "N/A"))

            with st.expander("Inputs Needed"):
                st.markdown(r.get("inputs", "N/A"))

            with st.expander("Assumptions"):
                st.markdown(r.get("assumptions", "N/A"))

        with cols[1]:
            with st.expander("Expected Output", expanded=True):
                st.markdown(r.get("output", "N/A"))

            with st.expander("Limitations"):
                st.markdown(r.get("limitations", "N/A"))

            module = r.get("suggested_module", "")
            if module:
                st.markdown(f"""
                <div style='background:rgba(0,255,212,0.06); border:1px solid #00FFD444; border-radius:6px; padding:14px; margin-top:10px;'>
                    <div style='color:#00FFD4; font-size:11px; font-family:JetBrains Mono,monospace; letter-spacing:1px; margin-bottom:4px;'>SUGGESTED MODULE</div>
                    <div style='color:#E8F4FD; font-size:14px; font-weight:600;'>{module}</div>
                    <div style='color:#6B8CAE; font-size:12px; margin-top:4px;'>Navigate to this module in the sidebar to run the analysis.</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='text-align:center; padding:60px 0; color:#1E2D4A;'>
        <div style='font-size:48px;'>🤖</div>
        <div style='font-size:14px; margin-top:14px; color:#6B8CAE;'>No analysis yet. Enter a research question above to begin.</div>
    </div>
    """, unsafe_allow_html=True)

# ─── Disclaimer ──────────────────────────────────────────────────────────────

st.markdown("<br>")
st.markdown("""
<div style='background:rgba(255,215,0,0.04); border:1px solid #FFD70033; border-radius:6px; padding:12px 16px; color:#FFD70099; font-size:11px;'>
⚠ Research tool only. Not financial advice. Statistical methods have assumptions and limitations. Always validate results with appropriate domain expertise.
</div>
""", unsafe_allow_html=True)
