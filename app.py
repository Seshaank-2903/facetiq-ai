"""FacetIQ — AI Conversation Facet Evaluation Platform.

High-Contrast Enterprise UI with Compact Theme Toggle Positioned Top-Right Next to Deploy Button.
"""

import os
import json
import time
import re
import pandas as pd
import streamlit as st

# pyrefly: ignore [missing-import]
from src.pipeline import FacetScoringPipeline
# pyrefly: ignore [missing-import]
from src.retrieval import FacetRetriever
# pyrefly: ignore [missing-import]
from src.evaluate import run_benchmark_evaluation
# pyrefly: ignore [missing-import]
from src.config import settings
try:
    # pyrefly: ignore [missing-import]
    from a2wsgi import ASGIMiddleware
    # pyrefly: ignore [missing-import]
    from server import app as _asgi_app
    app = ASGIMiddleware(_asgi_app)
except Exception:
    # pyrefly: ignore [missing-import]
    from server import app as app

# --- Page Configuration ---
st.set_page_config(
    page_title="FacetIQ — AI Conversation Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if "history" not in st.session_state:
    st.session_state["history"] = []
if "current_analysis" not in st.session_state:
    st.session_state["current_analysis"] = None
if "selected_facet_detail" not in st.session_state:
    st.session_state["selected_facet_detail"] = None
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

# --- Theme Design System (Dark / Light Mode Tokens) ---
theme_mode = st.session_state.get("theme", "dark")
is_dark = theme_mode == "dark"

# Dynamic Theme Tokens
BG_COLOR = "#09090b" if is_dark else "#ffffff"
SIDEBAR_BG = "#121215" if is_dark else "#ffffff"
CARD_BG = "#18181c" if is_dark else "#f8fafc"
CARD_BORDER = "#27272a" if is_dark else "#cbd5e1"
INPUT_BG = "#18181c" if is_dark else "#ffffff"
INPUT_BORDER = "#3f3f46" if is_dark else "#cbd5e1"
TEXT_PRIMARY = "#fafafa" if is_dark else "#0f172a"
TEXT_MUTED = "#a1a1aa" if is_dark else "#475569"
HEADING_COLOR = "#fafafa" if is_dark else "#0f172a"
CODE_BG = "#27272a" if is_dark else "#e2e8f0"
CODE_TEXT = "#38bdf8" if is_dark else "#1d4ed8"

BTN_SEC_BG = "#27272a" if is_dark else "#f1f5f9"
BTN_SEC_TEXT = "#fafafa" if is_dark else "#0f172a"
BTN_SEC_BORDER = "#3f3f46" if is_dark else "#cbd5e1"

ACCENT_BLUE = "#3b82f6" if is_dark else "#2563eb"
ACCENT_BG = "rgba(59, 130, 246, 0.12)" if is_dark else "#eff6ff"
QUOTE_BG = "rgba(59, 130, 246, 0.06)" if is_dark else "#f1f5f9"

SCORED_COLOR = "#4ade80" if is_dark else "#15803d"
SCORED_BG = "rgba(34, 197, 94, 0.12)" if is_dark else "#f0fdf4"
SCORED_BORDER = "rgba(34, 197, 94, 0.3)" if is_dark else "#bbf7d0"

ABSTAIN_COLOR = "#fbbf24" if is_dark else "#b45309"
ABSTAIN_BG = "rgba(245, 158, 11, 0.12)" if is_dark else "#fffbeb"
ABSTAIN_BORDER = "rgba(245, 158, 11, 0.3)" if is_dark else "#fef3c7"

UNOBS_COLOR = "#94a3b8" if is_dark else "#64748b"
UNOBS_BG = "rgba(148, 163, 184, 0.12)" if is_dark else "#f1f5f9"
UNOBS_BORDER = "rgba(148, 163, 184, 0.3)" if is_dark else "#e2e8f0"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: {TEXT_PRIMARY} !important;
}}

.stApp {{
    background-color: {BG_COLOR} !important;
}}

/* Streamlit Sidebar Background & Borders */
section[data-testid="stSidebar"] {{
    background-color: {SIDEBAR_BG} !important;
    border-right: 1px solid {CARD_BORDER} !important;
}}

section[data-testid="stSidebar"] * {{
    color: {TEXT_PRIMARY} !important;
}}

/* Streamlit Top Header Bar */
header[data-testid="stHeader"] {{
    background-color: {BG_COLOR} !important;
}}

/* Headings Contrast Fix */
h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
    color: {HEADING_COLOR} !important;
    font-weight: 700 !important;
}}

p, span, label, div, .tooltip-text {{
    color: {TEXT_PRIMARY} !important;
}}

/* Inline Code Badges */
code {{
    background-color: {CODE_BG} !important;
    color: {CODE_TEXT} !important;
    border: 1px solid {CARD_BORDER} !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
}}

/* Compact Buttons Styling */
div.stButton > button {{
    background-color: {BTN_SEC_BG} !important;
    color: {BTN_SEC_TEXT} !important;
    border: 1px solid {BTN_SEC_BORDER} !important;
    border-radius: 5px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 4px 12px !important;
    min-height: 30px !important;
    line-height: 1.2 !important;
    transition: all 0.15s ease !important;
}}

div.stButton > button:hover {{
    background-color: {ACCENT_BG} !important;
    color: {ACCENT_BLUE} !important;
    border-color: {ACCENT_BLUE} !important;
}}

/* Primary CTA Button Override */
div.stButton > button[kind="primary"] {{
    background-color: {ACCENT_BLUE} !important;
    color: #ffffff !important;
    border: none !important;
    font-size: 0.86rem !important;
    padding: 6px 16px !important;
    min-height: 36px !important;
    box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25) !important;
}}

div.stButton > button[kind="primary"]:hover {{
    background-color: #1d4ed8 !important;
    color: #ffffff !important;
}}

/* Deploy-Style Compact Theme Button Styling */
.deploy-style-theme-btn div.stButton > button {{
    background-color: {BTN_SEC_BG} !important;
    color: {BTN_SEC_TEXT} !important;
    border: 1px solid {BTN_SEC_BORDER} !important;
    font-size: 0.82rem !important;
    padding: 4px 12px !important;
    min-height: 30px !important;
    border-radius: 5px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
}}

.deploy-style-theme-btn div.stButton > button:hover {{
    background-color: {ACCENT_BG} !important;
    color: {ACCENT_BLUE} !important;
    border-color: {ACCENT_BLUE} !important;
}}

/* Streamlit Selectboxes / Dropdowns */
.stSelectbox > div > div, div[data-baseweb="select"] > div {{
    background-color: {INPUT_BG} !important;
    border: 1px solid {INPUT_BORDER} !important;
    color: {TEXT_PRIMARY} !important;
    border-radius: 5px !important;
    min-height: 34px !important;
    font-size: 0.85rem !important;
}}

.stSelectbox * , div[data-baseweb="select"] * {{
    color: {TEXT_PRIMARY} !important;
    background-color: transparent !important;
}}

div[role="listbox"], ul[role="listbox"], div[data-baseweb="menu"] {{
    background-color: {CARD_BG} !important;
    border: 1px solid {CARD_BORDER} !important;
    border-radius: 5px !important;
}}

div[role="option"] {{
    color: {TEXT_PRIMARY} !important;
    background-color: {CARD_BG} !important;
    font-size: 0.85rem !important;
}}

div[role="option"]:hover, div[role="option"][aria-selected="true"] {{
    background-color: {ACCENT_BG} !important;
    color: {ACCENT_BLUE} !important;
}}

/* File Uploader Container */
div[data-testid="stFileUploader"], div[data-testid="stFileUploader"] > section {{
    background-color: {INPUT_BG} !important;
    border: 1px dashed {INPUT_BORDER} !important;
    color: {TEXT_PRIMARY} !important;
    border-radius: 6px !important;
    padding: 8px !important;
}}

div[data-testid="stFileUploader"] * {{
    color: {TEXT_PRIMARY} !important;
}}

div[data-testid="stFileUploader"] button {{
    background-color: {BTN_SEC_BG} !important;
    color: {BTN_SEC_TEXT} !important;
    border: 1px solid {INPUT_BORDER} !important;
    font-size: 0.78rem !important;
    padding: 3px 10px !important;
}}

/* Inputs & Textareas */
input, textarea {{
    background-color: {INPUT_BG} !important;
    color: {TEXT_PRIMARY} !important;
    border: 1px solid {INPUT_BORDER} !important;
    border-radius: 6px !important;
    font-size: 0.88rem !important;
}}

/* Summary Metric Cards */
.summary-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 8px;
    padding: 14px 16px;
}}

.summary-value {{
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.2;
    color: {TEXT_PRIMARY};
}}

.summary-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {TEXT_MUTED} !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 3px;
}}

/* Trust Banner */
.trust-banner {{
    background: {ACCENT_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: {TEXT_PRIMARY};
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
}}

/* Facet Result Cards */
.facet-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
}}

/* Status Badges */
.badge-status-scored {{
    background: {SCORED_BG};
    color: {SCORED_COLOR} !important;
    border: 1px solid {SCORED_BORDER};
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.75rem;
}}

.badge-status-insufficient {{
    background: {ABSTAIN_BG};
    color: {ABSTAIN_COLOR} !important;
    border: 1px solid {ABSTAIN_BORDER};
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.75rem;
}}

.badge-status-unobservable {{
    background: {UNOBS_BG};
    color: {UNOBS_COLOR} !important;
    border: 1px solid {UNOBS_BORDER};
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.75rem;
}}

/* 5-Segment Score Rating Dots */
.score-dots-wrapper {{
    display: flex;
    gap: 4px;
    align-items: center;
    margin-top: 4px;
}}

.score-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: {CARD_BORDER};
}}

.score-dot-active {{
    background: {ACCENT_BLUE};
}}

/* Evidence Highlight Quote Box */
.evidence-quote {{
    background: {QUOTE_BG};
    border-left: 3px solid {ACCENT_BLUE};
    padding: 6px 10px;
    border-radius: 0 4px 4px 0;
    font-style: italic;
    font-size: 0.85rem;
    color: {TEXT_PRIMARY};
    margin-top: 8px;
}}

.tooltip-text {{
    font-size: 0.82rem;
    color: {TEXT_MUTED} !important;
}}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --- Pipeline Lazy Loader ---
@st.cache_resource
def get_pipeline():
    return FacetScoringPipeline()

pipeline = get_pipeline()


# --- Helper Functions ---
def get_score_label(score: int) -> str:
    labels = {
        1: "Very Weak Evidence",
        2: "Weak Evidence",
        3: "Moderate Evidence",
        4: "Strong Evidence",
        5: "Very Strong Evidence"
    }
    return labels.get(score, "Unscored")


def render_score_dots(score: int) -> str:
    """Renders 5-segment rating indicator dots in HTML."""
    if not score or score < 1:
        return ""
    dots = []
    for i in range(1, 6):
        cls = "score-dot-active" if i <= score else ""
        dots.append(f"<div class='score-dot {cls}'></div>")
    return f"<div class='score-dots-wrapper'>{''.join(dots)}</div>"


def highlight_evidence_in_text(text: str, snippet: str) -> str:
    """Highlights snippet phrase in original text with HTML mark tags."""
    if not snippet or not text:
        return text
    clean_snippet = snippet.strip("\"' ")
    if len(clean_snippet) < 3:
        return text
    pattern = re.escape(clean_snippet[:40])
    return re.sub(f"({pattern})", r"<mark style='background: rgba(59, 130, 246, 0.3); color: inherit; padding: 2px 4px; border-radius: 4px;'>\1</mark>", text, flags=re.IGNORECASE)


# --- TOP HEADER BAR WITH COMPACT DEPLOY-SIZED THEME TOGGLE BUTTON ---
col_hdr_left, col_hdr_right = st.columns([5, 1])

with col_hdr_left:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 2px;">
        <h2 style="margin: 0; font-size: 1.4rem; font-weight: 800; color: {TEXT_PRIMARY};">FacetIQ</h2>
        <span style="font-size: 0.7rem; font-weight: 600; padding: 2px 6px; border-radius: 4px; background: {ACCENT_BG}; color: {ACCENT_BLUE}; border: 1px solid {CARD_BORDER};">ENTERPRISE</span>
    </div>
    <p style="font-size: 0.82rem; color: {TEXT_MUTED}; margin: 0;">AI Conversation Intelligence & Facet Evaluation Platform</p>
    """, unsafe_allow_html=True)

with col_hdr_right:
    st.markdown("<div class='deploy-style-theme-btn'>", unsafe_allow_html=True)
    toggle_text = "Light" if is_dark else "Dark"
    if st.button(toggle_text, key="top_right_theme_toggle_btn"):
        st.session_state["theme"] = "light" if is_dark else "dark"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='margin: 8px 0 16px 0; opacity: 0.2;'>", unsafe_allow_html=True)


# --- Sidebar Navigation Shell ---
with st.sidebar:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
        <span style="font-size: 1.4rem;">🎯</span>
        <div>
            <div style="font-weight: 800; font-size: 1.1rem; color: {TEXT_PRIMARY};">FacetIQ</div>
            <div style="font-size: 0.72rem; color: {TEXT_MUTED};">AI Conversation Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    navigation = st.radio(
        "Navigation",
        options=[
            "Analyze Conversation",
            "Facet Catalog",
            "Safety & Abstention",
            "Benchmark Evaluation",
            "History Log",
            "System Settings"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Active Infrastructure Metadata
    st.caption("Active Infrastructure")
    st.markdown(f"**Provider**: `{settings.MODEL_PROVIDER.upper()}`")
    st.markdown(f"**Model**: `{settings.MODEL_NAME}`")
    st.markdown(f"**Embeddings**: `{settings.EMBEDDING_MODEL}`")


# ==============================================================================
# PAGE 1: ANALYZE CONVERSATION (PRIMARY DEFAULT LANDING PAGE)
# ==============================================================================
if navigation == "Analyze Conversation":
    st.markdown("### Conversation Analysis")
    st.markdown("<p class='tooltip-text'>Evaluate conversational evidence against relevant facets.</p>", unsafe_allow_html=True)
    
    # Sample Presets Selector
    preset_options = {
        "Custom Input": "",
        "Scenario 1: Executive Presentation (High Confidence)": "I gave a presentation yesterday to the executive board and answered all questions calmly and confidently.",
        "Scenario 2: Sarcasm & Panic Trap": "I absolutely LOVE presenting to 500 people... my heart was racing and I felt like I was going to throw up.",
        "Scenario 3: Medical Measurement Trap": "I've been feeling dizzy lately when I wake up. My doctor checked my blood pressure yesterday.",
        "Scenario 4: Third-Person Manager Quote Trap": "My manager told me yesterday that I handled the client presentation effectively and demonstrated strong leadership.",
        "Scenario 5: Code-Switching Fluency": "Presentation start hone ke baad I became very comfortable and explained the entire architecture smoothly."
    }
    
    col_preset, col_file = st.columns([3, 1])
    with col_preset:
        selected_preset_key = st.selectbox("Load Sample Conversation:", list(preset_options.keys()))
        default_val = preset_options[selected_preset_key] if selected_preset_key != "Custom Input" else "I gave a presentation yesterday to the executive board and answered all questions calmly and confidently."
    with col_file:
        uploaded_file = st.file_uploader("Upload Text File (.txt)", type=["txt"])
        if uploaded_file is not None:
            default_val = uploaded_file.read().decode("utf-8")

    # Conversation Text Input Area
    conv_text = st.text_area(
        "Paste a conversation:",
        value=default_val,
        height=120,
        placeholder="Paste a conversation here...",
        help="The system evaluates only evidence supported by the conversation."
    )

    char_count = len(conv_text.strip())
    st.markdown(f"<div style='text-align: right; font-size: 0.78rem; color: {TEXT_MUTED};'>Character Count: <strong>{char_count}</strong></div>", unsafe_allow_html=True)

    col_btn, col_hint = st.columns([1, 3])
    with col_btn:
        analyze_disabled = char_count == 0
        btn_click = st.button("Analyze Conversation", type="primary", disabled=analyze_disabled, use_container_width=True)

    with col_hint:
        st.markdown(f"<div style='margin-top: 6px; font-size: 0.8rem; color: {TEXT_MUTED};'>The system evaluates only evidence supported by the conversation.</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- EXECUTION & PROGRESS STATE ---
    if btn_click:
        progress_placeholder = st.empty()
        
        with progress_placeholder.container():
            st.markdown(f"""
            <div class="summary-card" style="margin-bottom: 16px;">
                <h4 style="margin: 0 0 8px 0; color: {ACCENT_BLUE}; font-size: 0.95rem;">Analyzing Conversation</h4>
                <div style="font-size: 0.82rem; color: {TEXT_PRIMARY}; line-height: 1.6;">
                    <div>○ Reading conversation context</div>
                    <div>○ Retrieving candidate facets</div>
                    <div>○ Evaluating evidence & applying safety filters</div>
                    <div style="color: {TEXT_MUTED};">○ Validating results</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        start_time = time.time()
        result = pipeline.process_conversation(conv_text, top_k=settings.TOP_K_RETRIEVAL, batch_size=settings.SCORING_BATCH_SIZE)
        latency = round(time.time() - start_time, 2)
        result["latency_sec"] = latency
        
        # Save analysis to session state and history
        st.session_state["current_analysis"] = result
        st.session_state["history"].insert(0, {
            "timestamp": time.strftime("%H:%M:%S (%b %d)"),
            "snippet": conv_text[:60] + "...",
            "full_text": conv_text,
            "result": result
        })
        progress_placeholder.empty()

    # --- RESULTS DISPLAY ---
    analysis = st.session_state.get("current_analysis")
    if analysis:
        res_list = analysis["results"]
        scored_count = sum(1 for r in res_list if r["status"] == "scored")
        abstained_count = sum(1 for r in res_list if r["status"] != "scored")
        
        confidences = [r["confidence"] for r in res_list if r["status"] == "scored"]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        st.markdown("### Analysis Results")
        st.markdown("<p class='tooltip-text'>Evidence-based facet evaluation</p>", unsafe_allow_html=True)

        # SUMMARY METRIC CARDS
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value">{analysis['retrieved_candidates_count']}</div>
                <div class="summary-label">Retrieved</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value" style="color: {SCORED_COLOR};">{scored_count}</div>
                <div class="summary-label">Scored</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value" style="color: {ABSTAIN_COLOR};">{abstained_count}</div>
                <div class="summary-label">Abstained</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value">{avg_conf * 100:.0f}%</div>
                <div class="summary-label">Average Confidence</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ABSTENTION SUMMARY BANNER
        st.markdown(f"""
        <div class="trust-banner">
            <span>🛡️</span>
            <div>
                <strong>{abstained_count} facets not scored</strong> — Withheld because conversational evidence was insufficient.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # FILTERS, SEARCH & SORT CONTROLS
        c_search, c_filter, c_sort = st.columns([2, 2, 1.5])
        with c_search:
            search_query = st.text_input("Search facets...", placeholder="Search facets...", label_visibility="collapsed")
        with c_filter:
            status_filter = st.radio("Filter Status:", ["All", "Scored", "Abstained"], horizontal=True, label_visibility="collapsed")
        with c_sort:
            sort_by = st.selectbox("Sort By:", ["Score", "Confidence", "Facet Name", "Default Order"], label_visibility="collapsed")

        # FILTER & SORT LOGIC
        filtered_results = res_list.copy()
        
        if search_query.strip():
            sq = search_query.lower().strip()
            filtered_results = [r for r in filtered_results if sq in r["facet"].lower()]

        if status_filter == "Scored":
            filtered_results = [r for r in filtered_results if r["status"] == "scored"]
        elif status_filter == "Abstained":
            filtered_results = [r for r in filtered_results if r["status"] != "scored"]

        if sort_by == "Score":
            filtered_results.sort(key=lambda x: (x["score"] if x["score"] is not None else -1), reverse=True)
        elif sort_by == "Confidence":
            filtered_results.sort(key=lambda x: x["confidence"], reverse=True)
        elif sort_by == "Facet Name":
            filtered_results.sort(key=lambda x: x["facet"])

        st.markdown("<br>", unsafe_allow_html=True)

        # FACET RESULT CARDS GRID
        if not filtered_results:
            st.info("No facet results match the selected filter query.")
        else:
            for item in filtered_results:
                fname = item["facet"]
                status = item["status"]
                score = item.get("score")
                conf = item["confidence"]
                evidence = item.get("evidence")
                reason = item.get("reason")

                card_border_style = f"border-left: 3px solid {SCORED_COLOR};" if status == "scored" else (f"border-left: 3px solid {ABSTAIN_COLOR};" if status == "insufficient_evidence" else f"border-left: 3px solid {UNOBS_COLOR};")

                with st.container():
                    col_main, col_action = st.columns([4.2, 0.8])
                    
                    with col_main:
                        if status == "scored":
                            badge_html = f"<span class='badge-status-scored'>Scored</span>"
                            score_dots = render_score_dots(score)
                            score_html = f"<div><span style='font-weight: 700; font-size: 1rem; color: {TEXT_PRIMARY};'>{score} / 5</span> <span style='font-size: 0.78rem; color: {TEXT_MUTED};'>• {get_score_label(score)}</span>{score_dots}</div>"
                        elif status == "insufficient_evidence":
                            badge_html = f"<span class='badge-status-insufficient'>Insufficient Evidence</span>"
                            score_html = f"<span style='font-weight: 600; font-size: 0.85rem; color: {ABSTAIN_COLOR};'>Score: Null (Abstained)</span>"
                        else:
                            badge_html = f"<span class='badge-status-unobservable'>Not Observable</span>"
                            score_html = f"<span style='font-weight: 600; font-size: 0.85rem; color: {UNOBS_COLOR};'>Score: Null (Unobservable)</span>"

                        st.markdown(f"""
                        <div class="facet-card" style="{card_border_style}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h4 style="margin: 0; font-size: 0.98rem; font-weight: 700;">{fname.title()}</h4>
                                <div>{badge_html}</div>
                            </div>
                            <div style="margin-top: 4px; display: flex; gap: 20px; align-items: center;">
                                {score_html}
                                <div style="font-size: 0.8rem; color: {TEXT_MUTED};">Confidence: <strong>{conf * 100:.0f}%</strong></div>
                            </div>
                            <div class="evidence-quote">
                                <strong>{'Evidence' if status == 'scored' else 'Reason'}:</strong> "{evidence if evidence else reason}"
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col_action:
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                        if st.button("View Details", key=f"btn_detail_{fname}"):
                            st.session_state["selected_facet_detail"] = item

        # --- FACET DETAILS MODAL / DRAWER ---
        selected_detail = st.session_state.get("selected_facet_detail")
        if selected_detail:
            st.markdown("---")
            with st.expander(f"Details: {selected_detail['facet'].title()}", expanded=True):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.markdown(f"**Facet Name**: `{selected_detail['facet']}`")
                    st.markdown(f"**Status**: `{selected_detail['status']}`")
                    st.markdown(f"**Score**: `{selected_detail['score'] if selected_detail['score'] is not None else 'Null (Abstained)'}`")
                    st.markdown(f"**Confidence**: `{selected_detail['confidence'] * 100:.0f}%`")
                with col_d2:
                    st.markdown(f"**Evidence**: *\"{selected_detail.get('evidence')}\"*")
                    st.markdown(f"**Reasoning**: *\"{selected_detail.get('reason')}\"*")
                
                st.markdown("#### Highlighted Evidence Context:")
                highlighted_context = highlight_evidence_in_text(analysis["conversation"], selected_detail.get("evidence") or "")
                st.markdown(f"<div style='background: {CARD_BG}; border: 1px solid {CARD_BORDER}; padding: 10px; border-radius: 5px;'>{highlighted_context}</div>", unsafe_allow_html=True)

                with st.expander("Advanced Details"):
                    st.json(selected_detail)

                if st.button("Close Details", key="close_detail"):
                    st.session_state["selected_facet_detail"] = None
                    st.rerun()

        # EXPORT OPTIONS
        st.markdown("<br>", unsafe_allow_html=True)
        col_ex1, col_ex2 = st.columns([1, 1])
        with col_ex1:
            st.download_button(
                "Download JSON",
                data=json.dumps(analysis, indent=2),
                file_name="facet_analysis_result.json",
                mime="application/json"
            )
        with col_ex2:
            df_export = pd.DataFrame(analysis["results"])
            st.download_button(
                "Export CSV",
                data=df_export.to_csv(index=False),
                file_name="facet_analysis_result.csv",
                mime="text/csv"
            )


# ==============================================================================
# PAGE 2: FACET CATALOG
# ==============================================================================
elif navigation == "Facet Catalog":
    st.markdown("### Facet Catalog")
    st.markdown("<p class='tooltip-text'>Browse and understand the available evaluation facets.</p>", unsafe_allow_html=True)

    try:
        retriever = FacetRetriever()
        retriever.build_or_load_index()
        df_catalog = retriever.df_facets
    except Exception as e:
        df_catalog = pd.DataFrame()

    if df_catalog.empty:
        st.warning("Facet catalog data is empty or processed file not found.")
    else:
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value">{len(df_catalog)}</div>
                <div class="summary-label">Total Facets</div>
            </div>
            """, unsafe_allow_html=True)
        with fc2:
            obs_cnt = sum(1 for v in df_catalog.get("conversation_observable", []) if v is True or str(v).lower() == "true")
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value" style="color: {SCORED_COLOR};">{obs_cnt}</div>
                <div class="summary-label">Observable</div>
            </div>
            """, unsafe_allow_html=True)
        with fc3:
            unobs_cnt = len(df_catalog) - obs_cnt
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value" style="color: {UNOBS_COLOR};">{unobs_cnt}</div>
                <div class="summary-label">Not Observable</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Search & Filter
        col_cs, col_cf = st.columns([2, 1])
        with col_cs:
            cat_search = st.text_input("Search facets...", placeholder="Search facets...")
        with col_cf:
            types_list = ["All"] + list(df_catalog.get("facet_type", pd.Series()).dropna().unique())
            sel_type = st.selectbox("Type Filter:", types_list)

        df_show = df_catalog.copy()
        if cat_search.strip():
            df_show = df_show[df_show["facet_normalized"].str.contains(cat_search.lower(), na=False)]
        if sel_type != "All":
            df_show = df_show[df_show["facet_type"] == sel_type]

        st.dataframe(
            df_show[["facet_normalized", "facet_type", "conversation_observable", "sensitivity", "scoring_definition"]],
            use_container_width=True,
            column_config={
                "facet_normalized": "Facet",
                "facet_type": "Type",
                "conversation_observable": "Observable",
                "sensitivity": "Sensitivity",
                "scoring_definition": "Definition"
            }
        )


# ==============================================================================
# PAGE 3: SAFETY & ABSTENTION
# ==============================================================================
elif navigation == "Safety & Abstention":
    st.markdown("### Safety & Abstention")
    st.markdown("<p class='tooltip-text'>Understand when the system chooses not to make an unsupported conclusion.</p>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-card" style="margin-bottom: 16px;">
        <h4 style="margin: 0 0 6px 0; color: {ACCENT_BLUE}; font-size: 0.95rem;">Evidence-First Evaluation</h4>
        <p style="color: {TEXT_MUTED}; font-size: 0.88rem; line-height: 1.5; margin: 0;">
            The system is designed to avoid making unsupported conclusions. When the conversation does not provide sufficient evidence, the system can abstain.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Examples of Responsible Abstention")

    st.markdown("""
    | Category | Conversation Input | Result | Reason |
    | :--- | :--- | :--- | :--- |
    | **Medical Inference** | *"I've been feeling dizzy when I wake up."* | `not_observable` | Blood pressure or lab metrics require explicit numerical measurements. |
    | **Third-Party Statement** | *"My father has diabetes."* | `insufficient_evidence` | Statement refers to another person, not direct evidence of the speaker. |
    | **Unobservable Trait** | *"I enjoy programming in Python."* | `not_observable` | Attributes like salary expectations or political affiliation cannot be observed. |
    | **Quoted Speech** | *"My boss said I did a great presentation."* | `insufficient_evidence` | Quoted statement is distinguished from speaker's own behavioral evidence. |
    """)


# ==============================================================================
# PAGE 4: BENCHMARK EVALUATION
# ==============================================================================
elif navigation == "Benchmark Evaluation":
    st.markdown("### Benchmark Evaluation")
    st.markdown("<p class='tooltip-text'>Measure how the system performs across representative conversations.</p>", unsafe_allow_html=True)

    if st.button("Run Benchmark Evaluation", type="primary"):
        with st.spinner("Running benchmark evaluation..."):
            report = run_benchmark_evaluation()
            st.session_state["benchmark_report"] = report
            st.success("Benchmark completed.")

    report = st.session_state.get("benchmark_report")
    if not report:
        report_path = os.path.join(settings.BASE_DIR, "outputs", "benchmark_results.json")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)

    if report:
        summ = report["summary"]
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value">{summ['total_reference_labels']}</div>
                <div class="summary-label">Test Cases</div>
            </div>
            """, unsafe_allow_html=True)
        with b2:
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value" style="color: {SCORED_COLOR};">{summ['correct_score_agreements']}</div>
                <div class="summary-label">Score Agreement</div>
            </div>
            """, unsafe_allow_html=True)
        with b3:
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value" style="color: {UNOBS_COLOR};">{summ['correct_abstentions']}</div>
                <div class="summary-label">Correct Abstentions</div>
            </div>
            """, unsafe_allow_html=True)
        with b4:
            st.markdown(f"""
            <div class="summary-card">
                <div class="summary-value" style="color: {ABSTAIN_COLOR};">{summ['incorrect_scores'] + summ['incorrect_abstentions']}</div>
                <div class="summary-label">Incorrect Scores</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Detailed Test Results")
        df_bench = pd.DataFrame(report["detailed_comparisons"])
        st.dataframe(df_bench, use_container_width=True)


# ==============================================================================
# PAGE 5: HISTORY LOG
# ==============================================================================
elif navigation == "History Log":
    st.markdown("### Analysis History")
    st.markdown("<p class='tooltip-text'>Review previous evaluation sessions performed during this session.</p>", unsafe_allow_html=True)

    history = st.session_state.get("history", [])
    if not history:
        st.info("No analyses yet. Paste a conversation on the 'Analyze' page to begin your first evaluation.")
    else:
        for idx, h in enumerate(history):
            res = h["result"]
            scored = sum(1 for r in res["results"] if r["status"] == "scored")
            abstained = len(res["results"]) - scored

            with st.container():
                st.markdown(f"""
                <div class="facet-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: {ACCENT_BLUE}; font-size: 0.95rem;">Analysis #{len(history) - idx} — {h['timestamp']}</h4>
                        <div>
                            <span class="badge-status-scored">{scored} Scored</span>
                            <span class="badge-status-insufficient">{abstained} Abstained</span>
                        </div>
                    </div>
                    <p style="margin-top: 6px; color: {TEXT_MUTED}; font-size: 0.85rem;">
                        <strong>Preview:</strong> "{h['snippet']}"
                    </p>
                </div>
                """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 6: SYSTEM SETTINGS
# ==============================================================================
elif navigation == "System Settings":
    st.markdown("### Settings")
    st.markdown("<p class='tooltip-text'>System configuration settings loaded from environment variables (.env).</p>", unsafe_allow_html=True)

    st.markdown(f"""
    | Setting Parameter | Active Value | Description |
    | :--- | :--- | :--- |
    | **MODEL_PROVIDER** | `{settings.MODEL_PROVIDER}` | Configured LLM backend. |
    | **MODEL_NAME** | `{settings.MODEL_NAME}` | Model identifier. |
    | **API_BASE_URL** | `{settings.API_BASE_URL}` | Endpoint API base URL. |
    | **EMBEDDING_MODEL** | `{settings.EMBEDDING_MODEL}` | Dense vector embedding model. |
    | **TOP_K_RETRIEVAL** | `{settings.TOP_K_RETRIEVAL}` | Retrieval count. |
    | **SCORING_BATCH_SIZE** | `{settings.SCORING_BATCH_SIZE}` | Scoring batch size. |
    """)
