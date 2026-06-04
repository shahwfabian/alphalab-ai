"""
AlphaLab AI — Global Design System
Clean, minimal, professional dark mode.
"""

import streamlit as st


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* ── Base ─────────────────────────────── */
    html, body, .stApp {
        background-color: #0d0d0d !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        color: #e5e5e5 !important;
    }

    /* ── Sidebar ──────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #1f1f1f !important;
    }
    [data-testid="stSidebar"] * { font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebarNav"] a {
        color: #888 !important;
        font-size: 13px !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        transition: all 0.15s !important;
    }
    [data-testid="stSidebarNav"] a:hover { background: #1a1a1a !important; color: #e5e5e5 !important; }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: #1e1e2e !important;
        color: #818cf8 !important;
    }

    /* ── Main content ─────────────────────── */
    .main .block-container {
        padding: 2rem 2.5rem !important;
        max-width: 1100px !important;
    }

    /* ── Typography ───────────────────────── */
    h1 { font-size: 1.6rem !important; font-weight: 600 !important; color: #f0f0f0 !important; letter-spacing: -0.02em !important; margin-bottom: 0.25rem !important; }
    h2 { font-size: 1.1rem !important; font-weight: 500 !important; color: #d0d0d0 !important; letter-spacing: -0.01em !important; }
    h3 { font-size: 0.95rem !important; font-weight: 500 !important; color: #c0c0c0 !important; }
    p, li { font-size: 0.875rem !important; line-height: 1.7 !important; color: #a0a0a0 !important; }

    /* ── Divider ──────────────────────────── */
    hr { border: none !important; border-top: 1px solid #1f1f1f !important; margin: 1.5rem 0 !important; }

    /* ── Inputs ───────────────────────────── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea {
        background: #161616 !important;
        border: 1px solid #262626 !important;
        border-radius: 8px !important;
        color: #e5e5e5 !important;
        font-size: 0.875rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.15s !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: #5865f2 !important;
        box-shadow: 0 0 0 3px rgba(88,101,242,0.1) !important;
        outline: none !important;
    }
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: #161616 !important;
        border: 1px solid #262626 !important;
        border-radius: 8px !important;
        color: #e5e5e5 !important;
    }
    label { font-size: 0.8rem !important; color: #666 !important; font-weight: 500 !important; letter-spacing: 0.02em !important; text-transform: uppercase !important; }

    /* ── Buttons ──────────────────────────── */
    .stButton > button {
        background: #5865f2 !important;
        border: none !important;
        color: #fff !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.25rem !important;
        transition: all 0.15s !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stButton > button:hover {
        background: #4752c4 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(88,101,242,0.3) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── Metrics ──────────────────────────── */
    [data-testid="metric-container"] {
        background: #161616 !important;
        border: 1px solid #1f1f1f !important;
        border-radius: 10px !important;
        padding: 1rem 1.25rem !important;
    }
    [data-testid="metric-container"] label {
        color: #555 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f0f0f0 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.75rem !important; }

    /* ── Tabs ─────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid #1f1f1f !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #555 !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        padding: 0.6rem 1rem !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #e5e5e5 !important;
        border-bottom: 2px solid #5865f2 !important;
    }

    /* ── Dataframes ───────────────────────── */
    [data-testid="stDataFrame"] {
        background: #161616 !important;
        border: 1px solid #1f1f1f !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* ── Expanders ────────────────────────── */
    details {
        background: #161616 !important;
        border: 1px solid #1f1f1f !important;
        border-radius: 8px !important;
    }
    summary { font-size: 0.875rem !important; color: #aaa !important; }

    /* ── Alerts / Info boxes ──────────────── */
    .stAlert {
        background: #161616 !important;
        border: 1px solid #1f1f1f !important;
        border-radius: 8px !important;
        font-size: 0.85rem !important;
    }

    /* ── File uploader ────────────────────── */
    [data-testid="stFileUploader"] {
        background: #161616 !important;
        border: 1px dashed #262626 !important;
        border-radius: 10px !important;
    }

    /* ── Scrollbar ────────────────────────── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: #3a3a3a; }

    /* ── Hide Streamlit branding ──────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Render a clean, consistent page header."""
    st.markdown(f"""
    <div style="padding: 0.5rem 0 1.5rem 0;">
        <h1 style="margin:0; font-size:1.5rem; font-weight:600; color:#f0f0f0; letter-spacing:-0.02em;">{title}</h1>
        {f'<p style="margin:0.35rem 0 0 0; font-size:0.875rem; color:#555;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)
    st.divider()


def stat_card(label: str, value: str, sub: str = "", accent: str = "#5865f2"):
    """Render a single clean stat card."""
    return f"""
    <div style="background:#161616; border:1px solid #1f1f1f; border-radius:10px; padding:1rem 1.25rem;">
        <div style="font-size:0.7rem; color:#555; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.4rem;">{label}</div>
        <div style="font-size:1.4rem; font-weight:600; color:{accent}; font-family:'Inter',sans-serif;">{value}</div>
        {f'<div style="font-size:0.75rem; color:#444; margin-top:0.25rem;">{sub}</div>' if sub else ''}
    </div>
    """


def info_box(text: str, kind: str = "info"):
    """Render a clean inline info/warning box."""
    colors = {
        "info":    ("#1e1e2e", "#5865f2"),
        "warning": ("#1f1a10", "#f59e0b"),
        "success": ("#0f1f15", "#22c55e"),
        "error":   ("#1f1010", "#ef4444"),
    }
    bg, accent = colors.get(kind, colors["info"])
    st.markdown(f"""
    <div style="background:{bg}; border-left:3px solid {accent};
                border-radius:0 8px 8px 0; padding:0.75rem 1rem;
                font-size:0.825rem; color:#aaa; line-height:1.6; margin:0.75rem 0;">
        {text}
    </div>
    """, unsafe_allow_html=True)
