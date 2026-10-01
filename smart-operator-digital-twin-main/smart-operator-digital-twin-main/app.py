import time
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from digital_twin.twin_engine import DigitalTwinEngine
from digital_twin.state_comparator import compare_states
from digital_twin.trend_analyzer import analyze_trends
from digital_twin.decision_engine import generate_decisions
from digital_twin.recommendation_engine import RecommendationEngine
from digital_twin.twin_snapshot import DigitalTwinSnapshot


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="VisionLink — Smart Operator Twin",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# UI THEME — VisionLink Industrial OS (Complete Redesign)
# Dark sidebar + light workspace + CAT amber accent
# ============================================================


# ============================================================
# GLOBAL THEME CSS
# ============================================================

st.markdown(

    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@600&display=swap');

    :root {
        --ink: #0f172a;
        --muted: #64748b;
        --line: #e2e8f0;
        --amber: #f5a800;
        --amber-dark: #b45309;
        --green: #16a34a;
        --red: #dc2626;
        --navy: #0f172a;
        --card-shadow: 0 10px 30px rgba(15,23,42,0.08);
        --card-shadow-sm: 0 4px 14px rgba(15,23,42,0.06);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* ---------- App background ---------- */
    .main {
        background:
            radial-gradient(900px 320px at 15% -5%, rgba(245,168,0,0.10), transparent 60%),
            radial-gradient(800px 300px at 95% 0%, rgba(2,132,199,0.10), transparent 60%),
            #eef2f6;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* ---------- Sidebar : dark control deck ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 55%, #0f172a 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {
        color: #94a3b8 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.12) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        min-height: 48px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
        background: var(--amber) !important;
        color: #0f172a !important;
        border-color: var(--amber) !important;
    }

    /* ---------- Hero : command header ---------- */
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 22px;
        background:
            linear-gradient(90deg, rgba(245,168,0,0.18), transparent 45%),
            linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #334155 100%);
        border: 1px solid rgba(245,168,0,0.35);
        color: white;
        margin-bottom: 1.2rem;
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
    }
    .hero h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        color: white !important;
    }
    .hero h1::after {
        content: "  LIVE";
        font-size: 0.7rem;
        font-weight: 800;
        background: #22c55e;
        color: white;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        vertical-align: middle;
        margin-left: 0.6rem;
        letter-spacing: 0.08em;
    }
    .hero p {
        margin: 0.4rem 0 0 0;
        color: #cbd5e1 !important;
        font-size: 1.02rem;
        font-weight: 500;
    }

    /* ---------- Generic cards / metrics ---------- */
    .machine-card {
        padding: 1rem 1.25rem;
        border-radius: 16px;
        background: white;
        border: 1px solid var(--line);
        border-left: 6px solid var(--amber);
        box-shadow: var(--card-shadow-sm);
        margin-bottom: 1rem;
    }
    div[data-testid="stMetric"] {
        background: white !important;
        padding: 0.9rem 1rem !important;
        border-radius: 16px !important;
        border: 1px solid var(--line) !important;
        box-shadow: var(--card-shadow-sm);
        border-top: 4px solid var(--amber) !important;
    }
    div[data-testid="stMetric"] label {
        font-weight: 700 !important;
        color: var(--muted) !important;
        font-size: 0.82rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-weight: 900 !important;
        color: var(--ink) !important;
    }
    div[data-testid="stContainer"] {
        border-radius: 18px !important;
    }

    /* ---------- Status pills ---------- */
    .status-normal, .status-warning, .status-critical {
        padding: 0.65rem 1rem;
        border-radius: 999px;
        font-weight: 800;
        text-align: center;
        font-size: 0.95rem;
        border: 1px solid transparent;
    }
    .status-normal { background: #dcfce7; color: #166534; border-color: #86efac; }
    .status-warning { background: #fef3c7; color: #92400e; border-color: #fcd34d; }
    .status-critical { background: #fee2e2; color: #991b1b; border-color: #fca5a5; }

    .section-space { margin-top: 1rem; margin-bottom: 0.5rem; }

    /* ---------- Buttons : glove friendly ---------- */
    div[data-testid="stButton"] button {
        border-radius: 14px !important;
        min-height: 54px !important;
        font-weight: 800 !important;
        font-size: 0.98rem !important;
        letter-spacing: 0.01em;
        border: 2px solid #cbd5e1 !important;
        transition: all .15s ease;
    }
    div[data-testid="stButton"] button:hover {
        border-color: var(--amber) !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(245,168,0,0.25);
    }
    div[data-testid="stFormSubmitButton"] button {
        background: var(--amber) !important;
        color: #0f172a !important;
        border-color: var(--amber) !important;
    }

    /* ---------- Tabs : pill workspace ---------- */
    div[data-testid="stTabs"] div[role="tablist"] {
        gap: 0.6rem;
        background: white;
        padding: 0.6rem;
        border-radius: 16px;
        border: 1px solid var(--line);
        box-shadow: var(--card-shadow-sm);
    }
    div[data-testid="stTabs"] button[role="tab"] {
        border-radius: 12px !important;
        font-weight: 800 !important;
        padding: 0.7rem 1.1rem !important;
        border: 1px solid transparent !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #0f172a !important;
        color: white !important;
        border-color: var(--amber) !important;
    }

    /* ---------- Expanders / progress ---------- */
    div[data-testid="stExpander"] {
        border-radius: 16px !important;
        border: 1px solid var(--line) !important;
        background: white !important;
        box-shadow: var(--card-shadow-sm);
        overflow: hidden;
    }
    div[data-testid="stProgress"] > div > div > div {
        background: linear-gradient(90deg, var(--amber), #f97316) !important;
    }

    /* ---------- Video library ---------- */
    .video-library-hero {
        background: linear-gradient(135deg, #0f172a, #1e3a5f);
        color: white;
        border-radius: 20px;
        padding: 1.4rem 1.6rem;
        border: 1px solid rgba(245,168,0,0.4);
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
    }
    .video-library-hero h3 { margin: 0; color: white !important; font-weight: 900; font-size: 1.45rem; }
    .video-library-hero p { margin: 0.35rem 0 0 0; color: #cbd5e1; font-weight: 500; }
    .video-stat {
        background: white;
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 0.9rem 1rem;
        text-align: center;
        box-shadow: var(--card-shadow-sm);
    }
    .video-stat b { display:block; font-size: 1.5rem; color: var(--ink); }
    .video-stat span { font-size: 0.8rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }
    .video-card {
        background: white;
        border: 1px solid var(--line);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: var(--card-shadow-sm);
        margin-bottom: 1rem;
    }
    .video-card-top {
        padding: 0.9rem 1.1rem 0.2rem 1.1rem;
    }
    .video-badge {
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 800;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        letter-spacing: .04em;
    }
    .video-badge.safety { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
    .video-badge.efficiency { background: #e0f2fe; color: #075985; border: 1px solid #7dd3fc; }
    .video-badge.maintenance { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
    .video-badge.default { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

    /* ========================================================
       VISUAL DIGITAL TWIN — redesigned stage
       ======================================================== */
    .twin-panel {
        background: white;
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1.25rem;
        margin: 0.5rem 0 1.4rem 0;
        box-shadow: var(--card-shadow);
        border-top: 6px solid var(--amber);
    }
    .twin-header { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 0.75rem; }
    .twin-title { font-size: 1.35rem; font-weight: 900; color: var(--ink); margin: 0; letter-spacing: -0.01em; }
    .twin-subtitle { color: var(--muted); font-size: 0.9rem; margin-top: 0.2rem; font-weight: 500; }
    .twin-live-badge {
        padding: 0.5rem 0.9rem; border-radius: 999px; font-weight: 800; font-size: 0.8rem;
        white-space: nowrap; border: 1px solid #bbf7d0; background: #f0fdf4; color: #166534;
    }
    .twin-live-badge.warning { border-color: #fde68a; background: #fffbeb; color: #92400e; }
    .twin-live-badge.critical { border-color: #fecaca; background: #fef2f2; color: #991b1b; animation: twinPulse 1.4s infinite; }
    .twin-body { display: grid; grid-template-columns: minmax(0, 2.1fr) minmax(230px, 0.9fr); gap: 1rem; align-items: stretch; }
    .twin-machine {
        min-height: 390px; border-radius: 18px; border: 1px solid #e2e8f0;
        background:
            radial-gradient(circle at 50% 38%, rgba(245,168,0,0.14), transparent 46%),
            linear-gradient(180deg, #0f172a 0%, #1e293b 55%, #334155 100%);
        overflow: hidden; position: relative;
    }
    .twin-machine svg { width: 100%; height: 100%; min-height: 390px; display: block; }
    .excavator-stage {
        position: relative; width: 100%; height: 390px; overflow: hidden;
        background:
            radial-gradient(circle at 48% 42%, rgba(245,168,0,0.20), transparent 42%),
            linear-gradient(180deg, #1e293b 0%, #0f172a 70%, #020617 100%);
    }
    .excavator-ground { position: absolute; left: 6%; right: 6%; bottom: 44px; height: 4px; border-radius: 99px; background: #f5a800; opacity: 0.8; }
    .excavator { position: absolute; left: 7%; right: 5%; bottom: 48px; height: 285px; }
    .exc-track { position: absolute; bottom: 0; width: 37%; height: 58px; border-radius: 30px; background: #0b1220; border: 4px solid #f5a800; box-sizing: border-box; }
    .exc-track.left { left: 5%; } .exc-track.right { left: 22%; }
    .exc-track::after { content: "●  ●  ●  ●  ●"; position: absolute; left: 10%; top: 12px; color: #f5a800; letter-spacing: 8px; font-size: 14px; }
    .exc-base { position: absolute; left: 10%; bottom: 48px; width: 43%; height: 72px; background: linear-gradient(135deg, #fbbf24, #f59e0b); border: 4px solid #78350f; border-radius: 24px 32px 12px 12px; transform: skewX(-6deg); box-sizing: border-box; }
    .exc-engine { position: absolute; left: 34%; bottom: 91px; width: 16%; height: 105px; border-radius: 18px 24px 8px 8px; background: linear-gradient(135deg, #fde68a, #f59e0b); border: 4px solid #78350f; box-sizing: border-box; z-index: 5; }
    .exc-engine::before { content: "ENGINE"; position: absolute; left: 10%; right: 10%; bottom: -25px; text-align: center; font-size: 10px; font-weight: 800; color: #fde68a; }
    .exc-engine-core { position: absolute; left: 50%; top: 35%; transform: translate(-50%, -50%); width: 34px; height: 34px; border-radius: 50%; background: white; border: 3px solid #78350f; }
    .exc-engine-core::after { content: "↻"; position: absolute; inset: 3px; text-align: center; line-height: 27px; color: #92400e; font-weight: 900; font-size: 18px; }
    .exc-cabin { position: absolute; left: 8%; bottom: 139px; width: 25%; height: 100px; background: #fffbeb; border: 4px solid #78350f; border-radius: 22px 18px 6px 6px; z-index: 7; box-sizing: border-box; }
    .exc-window { position: absolute; left: 12%; right: 10%; top: 13%; height: 48%; background: linear-gradient(135deg, #e0f2fe, #7dd3fc); border: 3px solid #0c4a6e; border-radius: 9px; }
    .exc-window::after { content: "●"; position: absolute; left: 48%; top: 25%; color: #475569; font-size: 18px; }
    .exc-cabin::after { content: "OPERATOR"; position: absolute; left: 0; right: 0; bottom: -20px; text-align: center; color: #fde68a; font-size: 10px; font-weight: 800; }
    .exc-pivot { position: absolute; left: 31%; bottom: 155px; width: 34px; height: 34px; border-radius: 50%; background: #fef3c7; border: 4px solid #f59e0b; z-index: 10; box-sizing: border-box; }
    .exc-pivot::after { content: ""; position: absolute; left: 8px; top: 8px; width: 10px; height: 10px; border-radius: 50%; background: #92400e; }
    .exc-boom { position: absolute; left: 30%; bottom: 184px; width: 31%; height: 30px; border-radius: 18px; background: linear-gradient(90deg, #fde68a, #f59e0b); border: 4px solid #78350f; transform: rotate(-28deg); transform-origin: left center; z-index: 8; box-sizing: border-box; }
    .exc-boom::after { content: "HYDRAULICS"; position: absolute; left: 36%; top: -24px; font-size: 10px; font-weight: 800; color: #fde68a; white-space: nowrap; transform: rotate(28deg); }
    .exc-arm { position: absolute; left: 57%; bottom: 238px; width: 28%; height: 25px; border-radius: 15px; background: linear-gradient(90deg, #fde68a, #f59e0b); border: 4px solid #78350f; transform: rotate(57deg); transform-origin: left center; z-index: 6; box-sizing: border-box; }
    .exc-bucket { position: absolute; left: 76%; bottom: 70px; width: 19%; height: 68px; background: #f59e0b; border: 4px solid #78350f; border-radius: 8px 10px 28px 5px; transform: rotate(12deg) skewX(-8deg); z-index: 4; box-sizing: border-box; }
    .exc-bucket::after { content: "⌄  ⌄  ⌄"; position: absolute; left: 15%; bottom: -20px; color: #fde68a; font-weight: 900; letter-spacing: 5px; }
    .exc-cylinder { position: absolute; left: 39%; bottom: 197px; width: 21%; height: 9px; border-radius: 9px; background: #e2e8f0; transform: rotate(-34deg); z-index: 9; }
    .exc-cylinder::after { content: ""; position: absolute; right: -22px; top: 1px; width: 45%; height: 7px; border-radius: 7px; background: #f5a800; }
    .twin-alert-dot { position: absolute; width: 14px; height: 14px; border-radius: 50%; z-index: 20; }
    .twin-alert-dot.engine { left: 47%; bottom: 175px; } .twin-alert-dot.hydraulic { left: 55%; bottom: 245px; }
    .twin-alert-dot.fuel { left: 42%; bottom: 110px; } .twin-alert-dot.safety { left: 19%; bottom: 225px; }
    .twin-alert-dot.warning { background: #f59e0b; box-shadow: 0 0 0 5px rgba(245,158,11,0.25), 0 0 12px rgba(245,158,11,0.7); animation: componentWarning 1.8s infinite; }
    .twin-alert-dot.critical { background: #dc2626; box-shadow: 0 0 0 6px rgba(220,38,38,0.25), 0 0 16px rgba(220,38,38,0.8); animation: componentCritical 1.1s infinite; }
    .twin-alert-dot.normal { background: #10b981; box-shadow: 0 0 0 4px rgba(16,185,129,0.18); }
    .twin-callout { position: absolute; z-index: 30; max-width: 180px; padding: 0.48rem 0.65rem; border-radius: 10px; background: rgba(255,255,255,0.97); border: 1px solid #dbe4ea; box-shadow: 0 5px 18px rgba(15,23,42,0.18); font-family: Arial, sans-serif; font-size: 11px; line-height: 1.3; }
    .twin-callout strong { display: block; font-size: 11px; margin-bottom: 2px; }
    .twin-callout.warning { border-color: #fcd34d; } .twin-callout.critical { border-color: #fca5a5; }
    .twin-callout.engine { left: 47%; bottom: 210px; } .twin-callout.hydraulic { left: 54%; bottom: 285px; }
    .twin-callout.fuel { left: 39%; bottom: 112px; } .twin-callout.safety { left: 12%; bottom: 246px; }
    .twin-callout.operation { left: 64%; bottom: 30px; }
    .twin-interpretation { margin-top: 0.75rem; padding: 0.8rem 0.9rem; border-radius: 14px; background: #f8fafc; border: 1px solid #e2e8f0; }
    .twin-interpretation-title { font-size: 0.84rem; font-weight: 800; color: #0f172a; margin-bottom: 0.25rem; }
    .twin-interpretation-main { font-size: 0.92rem; font-weight: 800; color: #334155; margin-bottom: 0.22rem; }
    .twin-interpretation-detail { font-size: 0.78rem; color: #64748b; line-height: 1.45; }
    .twin-action { margin-top: 0.55rem; padding: 0.5rem 0.65rem; border-radius: 9px; background: #fffbeb; color: #92400e; border: 1px solid #fde68a; font-size: 0.76rem; line-height: 1.4; }
    .twin-component { transition: opacity 0.2s ease, filter 0.2s ease; }
    .twin-component.normal { filter: drop-shadow(0 0 2px rgba(245,168,0,0.25)); }
    .twin-component.warning { filter: drop-shadow(0 0 7px rgba(245, 158, 11, 0.65)); animation: componentWarning 1.8s infinite; }
    .twin-component.critical { filter: drop-shadow(0 0 10px rgba(220, 38, 38, 0.8)); animation: componentCritical 1.1s infinite; }
    .twin-machine-label { font-size: 13px; font-weight: 800; letter-spacing: 0.02em; }
    .twin-side { display: flex; flex-direction: column; gap: 0.65rem; }
    .twin-state-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 0.72rem 0.8rem; }
    .twin-state-row { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; }
    .twin-state-name { font-size: 0.82rem; color: #475569; font-weight: 650; }
    .twin-state-value { font-size: 0.75rem; font-weight: 800; padding: 0.25rem 0.5rem; border-radius: 999px; }
    .twin-state-value.normal { color: #166534; background: #dcfce7; }
    .twin-state-value.warning { color: #92400e; background: #fef3c7; }
    .twin-state-value.critical { color: #991b1b; background: #fee2e2; }
    .twin-gauge { margin-top: 0.5rem; height: 8px; border-radius: 999px; background: #e2e8f0; overflow: hidden; }
    .twin-gauge-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #f5a800, #f97316); }
    .twin-explanation { margin-top: 0.75rem; padding: 0.65rem 0.8rem; border-radius: 12px; background: #f8fafc; border: 1px dashed #cbd5e1; color: #475569; font-size: 0.78rem; line-height: 1.45; }
    @keyframes componentWarning { 0%, 100% { opacity: 1; } 50% { opacity: 0.62; } }
    @keyframes componentCritical { 0%, 100% { opacity: 1; } 50% { opacity: 0.45; } }
    @keyframes twinPulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.55; } }
    @media (max-width: 900px) { .twin-body { grid-template-columns: 1fr; } }

    /* ---------- In-cab nav : redesigned ---------- */
    div.cab-nav-inactive div[data-testid="stButton"] button,
    div.cab-nav-inactive button {
        background: white !important; color: #0f172a !important;
        border: 1.5px solid #e2e8f0 !important; border-left: 6px solid #cbd5e1 !important;
        border-radius: 16px !important; height: 68px !important; min-height: 68px !important;
        padding: 12px 16px !important; font-size: 1.02rem !important; font-weight: 700 !important;
        text-align: left !important; width: 100% !important;
        box-shadow: 0 2px 8px rgba(15,23,42,0.05) !important;
    }
    div.cab-nav-inactive div[data-testid="stButton"] button:hover,
    div.cab-nav-inactive button:hover {
        background: #fffbeb !important; border-color: var(--amber) !important;
        border-left: 6px solid var(--amber) !important; color: #92400e !important;
        transform: translateX(4px) !important;
    }
    div.cab-nav-active div[data-testid="stButton"] button,
    div.cab-nav-active button {
        background: #0f172a !important; color: white !important;
        border: 2px solid var(--amber) !important; border-left: 10px solid var(--amber) !important;
        border-radius: 16px !important; height: 68px !important; min-height: 68px !important;
        padding: 12px 16px !important; font-size: 1.05rem !important; font-weight: 800 !important;
        width: 100% !important; box-shadow: 0 8px 22px rgba(245,168,0,0.28) !important;
    }

    /* ---------- Sticky cab status bar : stays visible while scrolling ---------- */
    .cab-sticky-bar {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        z-index: 999;
    }

    .footer { text-align: center; color: #94a3b8; padding: 1rem; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True
)



# ============================================================
# LOAD DATA
# ============================================================

DATA_PATH = Path(__file__).parent / "data" / "raw" / "machine_telemetry.csv"


@st.cache_data
def load_data():

    candidates = [
        Path(__file__).parent / "data" / "raw" / "machine_telemetry.csv",
        Path.cwd() / "data" / "raw" / "machine_telemetry.csv",
        Path.cwd() / "smart-operator-digital-twin-main" / "data" / "raw" / "machine_telemetry.csv",
        DATA_PATH,
    ]
    seen = set()
    for cand in candidates:
        key = str(cand.resolve()) if hasattr(cand, "resolve") else str(cand)
        if key in seen:
            continue
        seen.add(key)
        try:
            if cand.exists():
                data = pd.read_csv(cand)
                data["timestamp"] = pd.to_datetime(data["timestamp"])
                return data
        except Exception:
            continue

    return None


df = load_data()


if df is None:

    st.error(
        "Telemetry dataset not found. Looked in:\n"
        f"- `{Path(__file__).parent / 'data' / 'raw' / 'machine_telemetry.csv'}`\n"
        f"- `{Path.cwd() / 'data' / 'raw' / 'machine_telemetry.csv'}`\n"
        f"- `{Path.cwd() / 'smart-operator-digital-twin-main' / 'data' / 'raw' / 'machine_telemetry.csv'}`\n"
        "Generate it with: `python simulator/generate_dataset.py` run from the folder containing `app.py`."
    )

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "👷 Operator Assistant"

if "record_number" not in st.session_state:

    st.session_state.record_number = min(
        99,
        len(df) - 1
    )


if "playing" not in st.session_state:

    st.session_state.playing = False


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("### 🔀 View Mode")
st.sidebar.radio(
    "Select View Mode",
    [
        "🌐 Digital Twin Monitor",
        "👷 Operator Assistant"
    ],
    key="view_mode"
)

st.sidebar.divider()

st.sidebar.title(
    "🚜 VisionLink Command Deck"
)


st.sidebar.markdown(
    "### Machine"
)

st.sidebar.write(
    "**CAT-SIM-EXC-001**"
)

st.sidebar.caption(
    "Synthetic excavator telemetry"
)


st.sidebar.divider()


# ============================================================
# SIMULATION CONTROLS
# ============================================================

st.sidebar.markdown(
    "### 🎮 Simulation Controls"
)


col_play, col_pause = st.sidebar.columns(2)


with col_play:

    if st.button(
        "▶ Start",
        use_container_width=True
    ):

        st.session_state.playing = True


with col_pause:

    if st.button(
        "⏸ Pause",
        use_container_width=True
    ):

        st.session_state.playing = False


if st.sidebar.button(
    "↻ Reset Simulation",
    use_container_width=True
):

    st.session_state.record_number = 0
    st.session_state.playing = False
    st.rerun()


# ============================================================
# SPEED CONTROL
# ============================================================

simulation_speed = st.sidebar.selectbox(
    "Simulation Speed",
    [
        "Slow",
        "Normal",
        "Fast"
    ],
    index=1
)


speed_settings = {
    "Slow": 1.0,
    "Normal": 0.5,
    "Fast": 0.15
}


# ============================================================
# TELEMETRY SLIDER
# ============================================================

selected_record = st.sidebar.slider(
    "Telemetry Time Point",
    min_value=0,
    max_value=len(df) - 1,
    value=st.session_state.record_number,
    step=1,
    key="telemetry_slider"
)


# Only allow manual slider movement
# when simulation is paused.

if not st.session_state.playing:

    st.session_state.record_number = (
        selected_record
    )


st.sidebar.caption(
    f"{st.session_state.record_number + 1:,} / "
    f"{len(df):,} telemetry records"
)


# ============================================================
# SIMULATION STATUS
# ============================================================

if st.session_state.playing:

    st.sidebar.success(
        "🟢 Simulation running"
    )

else:

    st.sidebar.info(
        "⏸ Simulation paused"
    )


st.sidebar.divider()


# ============================================================
# PIPELINE
# ============================================================

st.sidebar.markdown(
    "### 🔄 Digital Twin Pipeline"
)

st.sidebar.markdown(
    """
    🛰️ **Telemetry**

    ↓

    🧠 **Digital Twin**

    ↓

    📊 **State Analysis**

    ↓

    📈 **Trend Analysis**

    ↓

    🤖 **Decision Engine**

    ↓

    👷 **Operator Recommendation**
    """
)


# ============================================================
# CURRENT RECORD
# ============================================================

record_number = st.session_state.record_number

current_record = df.iloc[
    record_number
]


# ============================================================
# DIGITAL TWIN ENGINE
# ============================================================

engine = DigitalTwinEngine(
    max_history=100
)


selected_records = df.iloc[
    :record_number + 1
]


for _, row in selected_records.iterrows():

    engine.update(
        row.to_dict()
    )


# ============================================================
# MACHINE STATES
# ============================================================

current_state = (
    engine.get_current_state()
)

previous_state = (
    engine.get_previous_state()
)

history = (
    engine.get_history()
)


if current_state is None:

    st.error(
        "Unable to create Digital Twin state."
    )

    st.stop()


# ============================================================
# STATE COMPARISON
# ============================================================

changes = compare_states(
    previous_state,
    current_state
)


# ============================================================
# TREND ANALYSIS
# ============================================================

trend_result = analyze_trends(
    history
)


if (
    isinstance(trend_result, dict)
    and "trends" in trend_result
):

    trends = trend_result["trends"]

else:

    trends = trend_result


# ============================================================
# DECISION ENGINE
# ============================================================

decisions = generate_decisions(
    current_state,
    trends,
    changes
)


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

recommendation_engine = (
    RecommendationEngine()
)


recommendations = (
    recommendation_engine
    .get_recommendations(
        decisions
    )
)


# ============================================================
# SNAPSHOT
# ============================================================

snapshot = DigitalTwinSnapshot(
    current_state=current_state,
    previous_state=previous_state,
    trends=trend_result,
    changes=changes,
    decisions=decisions,
    recommendations=recommendations
)

highest_priority_recommendation = snapshot.get_highest_priority_recommendation()

if highest_priority_recommendation is None:
    highest_priority_recommendation = {
        "priority": "NORMAL",
        "title": "Machine Operating Normally",
        "issue": "NO_ACTIVE_ISSUES",
        "action": "Continue operation while monitoring machine telemetry.",
        "reason": "Machine parameters are within expected limits."
    }


# ============================================================
# GLOBAL TWIN ALERTS — Digital Twin warnings surfaced on EVERY page
# ============================================================

if "dismissed_twin_alerts" not in st.session_state:
    st.session_state.dismissed_twin_alerts = set()

_twin_alert_items = []

if recommendations:

    _prio_rank = {"CRITICAL": 0, "WARNING": 1}

    for _i, _rec in enumerate(recommendations):

        _p = str(_rec.get("priority", "NORMAL")).upper()

        if _p in ("CRITICAL", "WARNING"):

            _twin_alert_items.append(
                {
                    "id": f"tw_{record_number}_{_i}",
                    "priority": _p,
                    "title": str(_rec.get("title", "Machine condition")),
                    "message": str(_rec.get("message", "")),
                }
            )

    _twin_alert_items.sort(
        key=lambda _a: _prio_rank.get(_a["priority"], 9)
    )

    _twin_alert_items = _twin_alert_items[:3]

st.session_state.twin_alert_items = _twin_alert_items


def _active_twin_alerts():

    dismissed = st.session_state.dismissed_twin_alerts

    return [
        a for a in st.session_state.twin_alert_items
        if a["id"] not in dismissed
    ]


def _twin_alert_banner_html(alert):

    bg = "#fee2e2" if alert["priority"] == "CRITICAL" else "#fef3c7"
    fg = "#991b1b" if alert["priority"] == "CRITICAL" else "#92400e"
    icon = "🚨" if alert["priority"] == "CRITICAL" else "⚠️"
    tag = "TWIN CRITICAL" if alert["priority"] == "CRITICAL" else "TWIN WARNING"

    return (
        f"<div style='margin-top:0.6rem;background-color:{bg};color:{fg};"
        f"padding:0.65rem 0.9rem;border-radius:12px;font-weight:700;font-size:0.98rem;'>"
        f"<span style='background:#0f172a;color:white;font-size:0.72rem;font-weight:800;"
        f"padding:0.2rem 0.55rem;border-radius:6px;margin-right:0.55rem;'>🤖 {tag}</span>"
        f"{icon} <strong>{alert['title']}</strong> — {alert['message']}</div>"
    )


def render_global_twin_alert_bar():
    """Sticky twin-warning bar for the Digital Twin Monitor view.

    (The Operator Assistant view merges the same alerts into its own
    sticky cab bar, so each page renders exactly one sticky bar.)
    """

    alerts = _active_twin_alerts()

    if not alerts:
        return

    html = "".join(
        _twin_alert_banner_html(a) for a in alerts
    )

    st.markdown(
        f"""<div class="cab-sticky-bar" style="background:#eef2f6;padding:0.4rem 0.1rem 0.6rem 0.1rem;">
<div style="background:linear-gradient(135deg,#0f172a,#1e293b);padding:0.7rem 1.1rem;border-radius:14px;color:white;font-weight:800;display:flex;justify-content:space-between;align-items:center;border:1px solid rgba(245,168,0,0.35);">
<span>🤖 DIGITAL TWIN ALERTS · record {record_number + 1}</span><span style="color:#fbbf24;">{len(alerts)} ACTIVE</span>
</div>{html}</div>""",
        unsafe_allow_html=True,
    )

    cols = st.columns(len(alerts))

    for c, a in zip(cols, alerts):

        with c:

            if st.button(
                f"✖ DISMISS: {a['title'][:28]}",
                key=f"tw_dis_{a['id']}",
                use_container_width=True
            ):

                st.session_state.dismissed_twin_alerts.add(a["id"])
                st.rerun()


# ============================================================

def render_operator_assistant_view(current_record, current_state, highest_priority_recommendation, decisions):
    """
    Renders the In-Cab, Glove-Friendly Operator Assistant interface.
    Features:
    - Composite Operator Safety Score (0-100) & Trends.
    - 3-Zone Proximity Safety System.
    - Automated Escalation Workflow to Supervisor Dashboard.
    - Complete Training & 15-Item Pre-Op Checklist Hub.
    - In-Cab Conversational Copilot (Voice + Text using Web Speech API STT/TTS).
    - Composite Fatigue & Attention-Drift Scoring Module.
    """

    # ------------------------------------------------------------
    # CENTRALIZED AUTOMATED ESCALATION CONFIGURATION
    # ------------------------------------------------------------
    ESCALATION_CONFIG = {
        "SAFETY_SCORE_MIN_THRESHOLD": 70,       # Escalates if composite safety score < 70
        "RED_PROXIMITY_ENABLED": True,          # Escalates on Red-zone proximity breach (< 3.0m)
        "REPEATED_AMBER_COUNT": 2,              # Escalates if >= 2 Amber proximity events in shift
        "SEATBELT_ACTIVE_OP_ENABLED": True,    # Escalates if seatbelt unfastened during active operation
        "FATIGUE_TAKE_BREAK_ENABLED": True      # Escalates if fatigue status == "TAKE A BREAK" (< 65 score)
    }

    # ------------------------------------------------------------
    # GLOBAL CONVERSION & SAFETY CONSTANTS
    # ------------------------------------------------------------
    DIESEL_CO2_PER_LITER = 2.68   # kg CO2 per liter of diesel fuel
    CAR_KM_PER_KG_CO2 = 6.0       # km driven in standard passenger car per kg CO2
    
    STANDARD_SPEED_LIMIT = 5.0    # km/h safe machine travel limit
    HAZARD_SPEED_LIMIT = 2.0      # km/h safe speed near active hazard zone

    idle_mins = float(current_state.operation.idle_time_minutes)
    wasted_fuel_l = idle_mins * (current_state.fuel.consumption_lph / 60.0)
    co2_kg = wasted_fuel_l * DIESEL_CO2_PER_LITER
    km_equivalent = co2_kg * CAR_KM_PER_KG_CO2

    # ------------------------------------------------------------
    # SESSION STATE INITIALIZATION
    # ------------------------------------------------------------
    if "op_assistant_nav" not in st.session_state:
        st.session_state.op_assistant_nav = "📋 Shift Tasks"

    if "active_task_idx" not in st.session_state:
        st.session_state.active_task_idx = 0

    if "active_preop_idx" not in st.session_state:
        st.session_state.active_preop_idx = 0

    if "active_train_idx" not in st.session_state:
        st.session_state.active_train_idx = 0

    if "dismissed_nudges" not in st.session_state:
        st.session_state.dismissed_nudges = set()

    if "incident_cooldowns" not in st.session_state:
        st.session_state.incident_cooldowns = {}

    if "safety_score_history" not in st.session_state:
        st.session_state.safety_score_history = [95, 94, 92]

    if "shift_tasks" not in st.session_state:
        st.session_state.shift_tasks = [
            {"id": 1, "name": "Trenching Zone B-4 (Section 12)", "zone": "Zone B-4", "est_min": 90, "elapsed_min": 58, "status": "In-Progress"},
            {"id": 2, "name": "Foundation Earthmoving - North Block", "zone": "North Block", "est_min": 120, "elapsed_min": 0, "status": "Pending"},
            {"id": 3, "name": "Stockpile Loading - Truck Fleet #4", "zone": "Stockpile A", "est_min": 45, "elapsed_min": 45, "status": "Completed"},
            {"id": 4, "name": "Access Road Leveling & Grading", "zone": "Access Sector 2", "est_min": 60, "elapsed_min": 0, "status": "Pending"},
        ]

    if "incident_log" not in st.session_state:
        st.session_state.incident_log = [
            {"time": "08:15 AM", "type": "Seatbelt Reminder", "severity": "WARNING", "category": "HEALTH & SAFETY", "impact": "-10 pts", "details": "Operator seatbelt unfastened for 12 seconds during start."},
            {"time": "07:30 AM", "type": "Pre-Start Inspection", "severity": "INFO", "category": "HEALTH & SAFETY", "impact": "0 pts", "details": "Daily fluid level and hydraulic hose inspection completed."},
        ]

    if "escalations" not in st.session_state:
        st.session_state.escalations = [
            {
                "id": "esc_init_1",
                "time": "08:15 AM",
                "step": 0,
                "operator": "Alex M.",
                "machine_id": current_state.machine_id,
                "trigger": "Seatbelt Unfastened During Active Operation",
                "severity": "CRITICAL",
                "status": "Acknowledged",
                "ack_time": "08:17 AM",
                "res_time": None
            }
        ]

    if "escalation_cooldowns" not in st.session_state:
        st.session_state.escalation_cooldowns = {}

    if "amber_event_count" not in st.session_state:
        st.session_state.amber_event_count = 0

    if "copilot_history" not in st.session_state:
        st.session_state.copilot_history = [
            {
                "time": "08:00 AM",
                "sender": "Copilot",
                "text": "Hello Alex! I am your In-Cab Digital Twin Copilot. Ask me about your active tasks, safety score, machine health, or fuel usage using voice or text."
            }
        ]

    if "copilot_audio_enabled" not in st.session_state:
        st.session_state.copilot_audio_enabled = True

    if "voice_query_input" not in st.session_state:
        st.session_state.voice_query_input = ""

    # 15-Item Pre-Operation Cab Checklist Definition
    PRE_OP_CHECKLIST_ITEMS = [
        {"id": "fluid_levels", "name": "Engine Oil & Coolant Fluid Levels", "cat": "Fluids & Engine", "desc": "Check engine dipstick, coolant level, and radiator overflow reservoir."},
        {"id": "undercarriage", "name": "Tracks / Tires / Undercarriage Condition", "cat": "Mechanical", "desc": "Inspect track tension, shoes, rollers, sprockets, or tire tread inflation."},
        {"id": "seatbelt_mirrors", "name": "Seatbelt Buckle & Rearview Mirrors", "cat": "Cab & Safety", "desc": "Ensure seatbelt latch locks securely and mirrors are aligned for clear rear view."},
        {"id": "lights_alarms", "name": "Dashboard Warning Lights & Alarms", "cat": "Electrical", "desc": "Verify bulb self-test pass and audible travel warning chime sounds."},
        {"id": "fire_ext", "name": "Fire Extinguisher Charge & Mounting", "cat": "Safety Equipment", "desc": "Gauge in green zone, quick-release pin intact."},
        {"id": "guards_shields", "name": "Safety Guards & Structural Shields", "cat": "Mechanical", "desc": "Confirm engine side compartment panels and hydraulic pump shields are locked."},
        {"id": "hydraulic_hoses", "name": "Hydraulic Hoses & Cylinder Integrity", "cat": "Hydraulics", "desc": "Inspect boom, arm, and bucket cylinder hoses for weeping oil, bulges, or chafing."},
        {"id": "visible_leaks", "name": "Ground Leak Check under Machine", "cat": "Fluids & Engine", "desc": "Look under machine belly pan for fresh oil, fuel, or coolant drips."},
        {"id": "glass_visibility", "name": "Cab Glass Cleanliness & Wipers", "cat": "Cab & Safety", "desc": "Wipe front windshield glass clean and confirm washer fluid reservoir filled."},
        {"id": "horn_function", "name": "Horn & Travel Warning Signal", "cat": "Electrical", "desc": "Test cab steering wheel horn button and 2-tone travel warning alarm."},
        {"id": "backup_camera", "name": "Backup Camera & Perimeter Display", "cat": "Safety Equipment", "desc": "Verify rear camera feed image clarity on the main cab tablet display screen."},
        {"id": "work_lights", "name": "LED Work Lights & Hazard Flashers", "cat": "Electrical", "desc": "Turn on boom floodlights, cab roof lights, and orange strobe beacon."},
        {"id": "cab_controls", "name": "Joystick & Hydraulic Lock Lever", "cat": "Cab & Controls", "desc": "Confirm red hydraulic lockout lever smoothly engages and disengages pilot controls."},
        {"id": "parking_brake", "name": "Parking Brake & Swing Lock Pin", "cat": "Cab & Controls", "desc": "Engage house swing lock pin and verify parking brake holds machine steady."},
        {"id": "walk_check", "name": "360° Walk-Around Perimeter Clearance", "cat": "Site Safety", "desc": "Perform 360-degree walk around machine to clear ground workers, tools, and obstacles."}
    ]

    if "pre_op_status" not in st.session_state:
        st.session_state.pre_op_status = {item["id"]: "PASSED" for item in PRE_OP_CHECKLIST_ITEMS}

    if "pre_op_notes" not in st.session_state:
        st.session_state.pre_op_notes = {}

    if "training_modules" not in st.session_state:
        st.session_state.training_modules = [
            {
                "id": "mod_1",
                "title": "Module 1: Proximity Hazard Mitigation",
                "category": "HEALTH & SAFETY",
                "scenario": "You are trenching near Zone B-4 when your perimeter display flags a site pickup truck 6.2m on your right side.",
                "options": [
                    "A) Continue digging at full speed since it's outside the 3m red zone.",
                    "B) Reduce speed (< 2 km/h), sound horn, and confirm truck position via radio before moving.",
                    "C) Swing boom right immediately to signal the truck to leave."
                ],
                "correct_idx": 1,
                "explanation": "Reducing machine speed to the hazard limit (2.0 km/h) and establishing positive radio contact prevents swing-radius collisions.",
                "user_answer": 1,
                "status": "Passed"
            },
            {
                "id": "mod_2",
                "title": "Module 2: Inclined Ramp Overspeed Control",
                "category": "HEALTH & SAFETY",
                "scenario": "While traveling down a 12% grade access ramp, machine speed hits 6.8 km/h (speed limit: 5.0 km/h) and an overspeed alert sounds.",
                "options": [
                    "A) Apply service brake smoothly, lower engine RPM, and maintain speed under 5 km/h.",
                    "B) Shift travel control into neutral and let gravity coast the machine down.",
                    "C) Lower the excavator bucket onto the gravel ramp surface to drag brake."
                ],
                "correct_idx": 0,
                "explanation": "Controlled service braking combined with lower engine RPM maintains traction without overheating hydraulic brakes or chattering tracks.",
                "user_answer": 0,
                "status": "Passed"
            },
            {
                "id": "mod_3",
                "title": "Module 3: Idle Fuel & Emission Reduction",
                "category": "OPERATING EFFICIENCY",
                "scenario": "You arrive at stockpile loader zone and are informed of a 30-minute truck queue delay. Engine fuel level is at 22%.",
                "options": [
                    "A) Keep engine idling at 1900 RPM to keep cab air conditioning cold.",
                    "B) Leave engine idling at low idle (800 RPM) for the entire 30 minutes.",
                    "C) Shut off engine after 3 minutes of waiting to eliminate wasted fuel and emissions, notifying dispatch."
                ],
                "correct_idx": 2,
                "explanation": "Shutting down during waits > 5 mins saves ~4.5L of diesel per hour, prevents ~12 kg of CO₂ emissions, and extends engine component life.",
                "user_answer": 2,
                "status": "Passed"
            },
            {
                "id": "mod_4",
                "title": "Module 4: Hydraulic Over-Pressure Relief",
                "category": "OPERATING EFFICIENCY",
                "scenario": "While digging in rocky clay, hydraulic pressure spikes above 300 bar and machine health drops by 2%.",
                "options": [
                    "A) Pull joystick harder to force the bucket through the rock seam.",
                    "B) Ease joystick pressure, adjust bucket entry angle, and use hydraulic hammer attachment if needed.",
                    "C) Turn off engine immediately while bucket is stuck in the trench."
                ],
                "correct_idx": 1,
                "explanation": "Adjusting bucket entry angle prevents continuous hydraulic relief valve bypass venting, lowering oil temperature and preserving pump life.",
                "user_answer": None,
                "status": "Not Started"
            }
        ]


    if "training_videos" not in st.session_state:
        st.session_state.training_videos = [
            {
                "id": "vid_1",
                "title": "Pre-Start Walkaround Masterclass",
                "category": "HEALTH & SAFETY",
                "level": "Beginner",
                "duration": "0:15",
                "description": "Full 360-degree walkaround: fluid levels, undercarriage, guards, lights and perimeter clearance before engine start.",
                "url": "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                "watched": True,
                "is_sample": True,
            },
            {
                "id": "vid_2",
                "title": "Proximity & Swing-Radius Awareness",
                "category": "HEALTH & SAFETY",
                "level": "Intermediate",
                "duration": "0:15",
                "description": "How to read the 3-zone radar, horn signals, radio confirmation and safe swing near ground workers.",
                "url": "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                "watched": False,
                "is_sample": True,
            },
            {
                "id": "vid_3",
                "title": "Idle Reduction & Fuel-Smart Operation",
                "category": "OPERATING EFFICIENCY",
                "level": "Beginner",
                "duration": "1:00",
                "description": "When to shut down vs low-idle, reading idle CO2 waste, and dispatch coordination during truck queues.",
                "url": "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
                "watched": False,
                "is_sample": True,
            },
            {
                "id": "vid_4",
                "title": "Hydraulic Control & Over-Pressure Prevention",
                "category": "MAINTENANCE",
                "level": "Advanced",
                "duration": "1:00",
                "description": "Bucket entry angles, relief-valve symptoms, oil temperature control and attachment selection in rock.",
                "url": "https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
                "watched": False,
                "is_sample": True,
            },
        ]

    if "video_filter" not in st.session_state:
        st.session_state.video_filter = "All"

    if "training_videos" not in st.session_state:
        pass

    # ------------------------------------------------------------
    # THREE-ZONE PROXIMITY SAFETY SYSTEM
    # Thresholds: GREEN (>10.0m), AMBER (3.0m - 10.0m), RED (<3.0m)
    # ------------------------------------------------------------
    has_hazard = current_state.anomaly_detected or current_state.scenario == "SAFETY_VIOLATION"
    has_warning = current_state.overall_status == "WARNING"

    if has_hazard:
        hazard_dir = "REAR"
        hazard_dist = 2.4
        hazard_zone = "RED"
        hazard_label = "RED DANGER: Ground worker detected 2.4m behind rear counterweight swing zone!"
    elif has_warning:
        hazard_dir = "RIGHT"
        hazard_dist = 6.2
        hazard_zone = "AMBER"
        hazard_label = "AMBER CAUTION: Site pickup truck parked 6.2m near right track."
    else:
        hazard_dir = "NONE"
        hazard_dist = 12.5
        hazard_zone = "GREEN"
        hazard_label = "GREEN SAFE: All 4 perimeter zones clear (> 10.0m)."

    # ------------------------------------------------------------
    # COMPOSITE FATIGUE & ATTENTION-DRIFT SCORING MODULE (FEATURE 2)
    # Inputs: Shift duration, idle-to-active trend, time-of-day risk, reaction consistency proxy
    # ------------------------------------------------------------
    rec_num = st.session_state.record_number
    shift_hours = ((rec_num % 480) / 60.0) + 1.5

    # 1. Shift duration penalty
    duration_penalty = min(25.0, shift_hours * 4.0)

    # 2. Idle-to-active trend penalty
    shift_history_df = df.iloc[:rec_num + 1] if not df.empty else None
    recent_idle_avg = shift_history_df['idle_time_minutes'].tail(10).mean() if shift_history_df is not None and not shift_history_df.empty else idle_mins
    idle_trend_penalty = min(20.0, (recent_idle_avg / 15.0) * 15.0)

    # 3. Time of day risk (late shift circadian factor)
    time_of_day_risk = 8.0 if (shift_hours >= 5.5 or (rec_num % 1440) > 1000) else 2.0

    # 4. Synthetic Reaction Consistency Proxy (task pace ratio variance)
    active_task_for_fatigue = st.session_state.shift_tasks[st.session_state.active_task_idx % len(st.session_state.shift_tasks)]
    task_pace_ratio = active_task_for_fatigue["elapsed_min"] / max(1, active_task_for_fatigue["est_min"])
    reaction_variance_penalty = min(12.0, max(0.0, (task_pace_ratio - 1.0) * 10.0))

    base_fatigue = 100.0 - (duration_penalty + idle_trend_penalty + time_of_day_risk + reaction_variance_penalty)
    if current_state.anomaly_detected:
        base_fatigue -= 5.0

    alertness_score = max(40.0, min(99.0, base_fatigue))

    if alertness_score >= 82:
        fatigue_status = "ALERT & FOCUSED"
        fatigue_color = "#166534"
        fatigue_bg = "#dcfce7"
        fatigue_icon = "🟢"
        fatigue_reason = f"{shift_hours:.1f} hrs into shift · Steady operational pace & low idle trend."
    elif alertness_score >= 65:
        fatigue_status = "GETTING TIRED"
        fatigue_color = "#92400e"
        fatigue_bg = "#fef3c7"
        fatigue_icon = "🟡"
        fatigue_reason = f"{shift_hours:.1f} hrs into shift · Elevated idle trend & attention variance. Consider a 5-min stretch break."
    else:
        fatigue_status = "TAKE A BREAK"
        fatigue_color = "#991b1b"
        fatigue_bg = "#fee2e2"
        fatigue_icon = "🔴"
        fatigue_reason = f"{shift_hours:.1f} hrs into shift · High fatigue & attention drift detected. Mandatory 15-min break recommended."

    # Hysteresis logging of fatigue state transitions
    current_sim_step = st.session_state.record_number
    if "last_fatigue_status" not in st.session_state:
        st.session_state.last_fatigue_status = fatigue_status
    elif st.session_state.last_fatigue_status != fatigue_status:
        last_fatigue_step = st.session_state.incident_cooldowns.get("Fatigue State Change", -999)
        if (current_sim_step - last_fatigue_step) >= 10:
            st.session_state.incident_log.insert(0, {
                "time": current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current",
                "type": f"Fatigue Transition: {fatigue_status}",
                "severity": "CRITICAL" if fatigue_status == "TAKE A BREAK" else ("WARNING" if fatigue_status == "GETTING TIRED" else "INFO"),
                "category": "HEALTH & SAFETY",
                "impact": "-10 pts" if fatigue_status == "TAKE A BREAK" else ("-4 pts" if fatigue_status == "GETTING TIRED" else "0 pts"),
                "details": fatigue_reason
            })
            st.session_state.incident_cooldowns["Fatigue State Change"] = current_sim_step
            st.session_state.last_fatigue_status = fatigue_status

    # ------------------------------------------------------------
    # OVERSPEED DETECTION & COMPOSITE SAFETY SCORE (0-100)
    # ------------------------------------------------------------
    speed_kmh = float(current_state.operation.speed_kmh)
    active_speed_limit = HAZARD_SPEED_LIMIT if hazard_zone in ["AMBER", "RED"] else STANDARD_SPEED_LIMIT
    is_overspeed = speed_kmh > active_speed_limit

    score_deductions = []

    if not current_state.safety.seatbelt_fastened and current_state.safety.operator_present:
        score_deductions.append({"issue": "Seatbelt Violation", "pts": -10, "details": "Seatbelt unfastened while in operator seat"})

    if is_overspeed:
        score_deductions.append({"issue": "Overspeed Event", "pts": -8, "details": f"Speed {speed_kmh:.1f} km/h exceeded limit ({active_speed_limit:.1f} km/h)"})

    if hazard_zone == "RED":
        score_deductions.append({"issue": "Proximity RED Danger", "pts": -12, "details": f"Ground worker 2.4m near {hazard_dir} zone"})
    elif hazard_zone == "AMBER":
        score_deductions.append({"issue": "Proximity AMBER Caution", "pts": -4, "details": f"Obstacle 6.2m near {hazard_dir} zone"})

    if current_state.operation.idle_time_minutes > 15:
        score_deductions.append({"issue": "Excessive Idling", "pts": -5, "details": f"Idling for {current_state.operation.idle_time_minutes:.0f} mins (>15m threshold)"})

    # Fatigue Factor in Safety Score
    if fatigue_status == "TAKE A BREAK":
        score_deductions.append({"issue": "Critical Fatigue Risk", "pts": -10, "details": f"Alertness score {alertness_score:.0f}% (Take a Break)"})
    elif fatigue_status == "GETTING TIRED":
        score_deductions.append({"issue": "Elevated Fatigue Level", "pts": -4, "details": f"Alertness score {alertness_score:.0f}% (Getting Tired)"})

    # Pre-Op Checklist & Training Impact on Composite Safety Score
    pre_op_passed_count = sum(1 for status in st.session_state.pre_op_status.values() if status == "PASSED")
    pre_op_flagged_count = sum(1 for status in st.session_state.pre_op_status.values() if status == "ISSUE_FLAGGED")
    pre_op_complete = (pre_op_passed_count + pre_op_flagged_count) == len(PRE_OP_CHECKLIST_ITEMS)
    pre_op_all_clean = pre_op_complete and pre_op_flagged_count == 0

    if pre_op_flagged_count > 0:
        score_deductions.append({"issue": "Pre-Op Inspection Defect", "pts": -5, "details": f"{pre_op_flagged_count} pre-op item(s) flagged with issues"})
    elif not pre_op_complete:
        score_deductions.append({"issue": "Incomplete Pre-Op Inspection", "pts": -3, "details": f"Pre-op checklist incomplete ({pre_op_passed_count}/{len(PRE_OP_CHECKLIST_ITEMS)})"})

    passed_training_count = sum(1 for m in st.session_state.training_modules if m["status"] == "Passed")
    training_bonus = 3 if passed_training_count >= 3 else 0
    pre_op_bonus = 5 if pre_op_all_clean else 0

    total_deduction = sum(item["pts"] for item in score_deductions)
    composite_safety_score = max(35, min(100, 100 + total_deduction + pre_op_bonus + training_bonus))

    # Track safety score trend
    st.session_state.safety_score_history.append(composite_safety_score)
    if len(st.session_state.safety_score_history) > 10:
        st.session_state.safety_score_history.pop(0)

    recent_scores = st.session_state.safety_score_history
    if len(recent_scores) >= 2:
        if recent_scores[-1] > recent_scores[-2]:
            score_trend = "RISING ↗️"
        elif recent_scores[-1] < recent_scores[-2]:
            score_trend = "DECLINING ↘️"
        else:
            score_trend = "STABLE ➡️"
    else:
        score_trend = "STABLE ➡️"

    if composite_safety_score >= 88:
        score_status = "EXCELLENT"
        score_color = "#166534"
        score_bg = "#dcfce7"
        score_icon = "🟢"
    elif composite_safety_score >= 70:
        score_status = "GOOD"
        score_color = "#92400e"
        score_bg = "#fef3c7"
        score_icon = "🟡"
    else:
        score_status = "NEEDS ATTENTION"
        score_color = "#991b1b"
        score_bg = "#fee2e2"
        score_icon = "🔴"

    if score_deductions:
        worst_ded = min(score_deductions, key=lambda x: x["pts"])
        main_factor_text = f"Main factor: {worst_ded['issue']} ({worst_ded['pts']} pts)"
    elif pre_op_all_clean:
        main_factor_text = "Main factor: Clean Pre-Op Checklist (+5 pts)"
    else:
        main_factor_text = "Main factor: All operations normal"

    # Incident Logging for Safety Score Deductions
    cooldown_steps = 5
    for ded in score_deductions:
        issue_key = ded["issue"]
        last_step = st.session_state.incident_cooldowns.get(issue_key, -999)
        if (current_sim_step - last_step) >= cooldown_steps:
            is_eff = issue_key in ["Excessive Idling"]
            st.session_state.incident_log.insert(0, {
                "time": current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current",
                "type": issue_key,
                "severity": "CRITICAL" if ded["pts"] <= -10 else "WARNING",
                "category": "OPERATING EFFICIENCY" if is_eff else "HEALTH & SAFETY",
                "impact": f"{ded['pts']} pts",
                "details": ded["details"]
            })
            st.session_state.incident_cooldowns[issue_key] = current_sim_step

    # ------------------------------------------------------------
    # EVALUATE AUTOMATED ESCALATION TRIGGERS FOR SUPERVISOR
    # ------------------------------------------------------------
    active_triggers = []

    if composite_safety_score < ESCALATION_CONFIG["SAFETY_SCORE_MIN_THRESHOLD"]:
        active_triggers.append({
            "key": "low_safety_score",
            "trigger": f"Low Safety Score ({composite_safety_score}/100 < {ESCALATION_CONFIG['SAFETY_SCORE_MIN_THRESHOLD']} threshold)",
            "severity": "CRITICAL"
        })

    if ESCALATION_CONFIG["RED_PROXIMITY_ENABLED"] and hazard_zone == "RED":
        active_triggers.append({
            "key": "red_proximity",
            "trigger": f"Red-Zone Proximity Danger ({hazard_dist}m breach in {hazard_dir} zone)",
            "severity": "CRITICAL"
        })

    if ESCALATION_CONFIG["SEATBELT_ACTIVE_OP_ENABLED"] and (not current_state.safety.seatbelt_fastened and current_state.safety.operator_present):
        active_triggers.append({
            "key": "seatbelt_violation",
            "trigger": "Seatbelt Unfastened During Active Operation",
            "severity": "CRITICAL"
        })

    if ESCALATION_CONFIG["FATIGUE_TAKE_BREAK_ENABLED"] and fatigue_status == "TAKE A BREAK":
        active_triggers.append({
            "key": "fatigue_break",
            "trigger": f"Critical Operator Fatigue (Alertness: {alertness_score:.0f}% - Mandatory Break)",
            "severity": "WARNING"
        })

    if hazard_zone == "AMBER":
        st.session_state.amber_event_count += 1
        if st.session_state.amber_event_count >= ESCALATION_CONFIG["REPEATED_AMBER_COUNT"]:
            active_triggers.append({
                "key": "repeated_amber",
                "trigger": f"Repeated Amber-Zone Proximity Events ({st.session_state.amber_event_count} events in shift)",
                "severity": "WARNING"
            })
    else:
        st.session_state.amber_event_count = 0

    for trg in active_triggers:
        last_step = st.session_state.escalation_cooldowns.get(trg["key"], -999)
        if (current_sim_step - last_step) >= 10:
            esc_item = {
                "id": f"esc_{len(st.session_state.escalations)+1}_{current_sim_step}",
                "time": current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current",
                "step": current_sim_step,
                "operator": "Alex M.",
                "machine_id": current_state.machine_id,
                "trigger": trg["trigger"],
                "severity": trg["severity"],
                "status": "Active",
                "ack_time": None,
                "res_time": None
            }
            st.session_state.escalations.insert(0, esc_item)
            st.session_state.escalation_cooldowns[trg["key"]] = current_sim_step

    # Task progress % computation
    for task in st.session_state.shift_tasks:
        if task["status"] == "Completed":
            task["progress"] = 100
        elif task["status"] == "Pending":
            task["progress"] = 0
        else:
            task["progress"] = min(99, max(5, int((task["elapsed_min"] / max(1, task["est_min"])) * 100)))

    # ------------------------------------------------------------
    # IN-CAB COPILOT ENGINE & TOP-LEVEL PARAMETER HANDLER
    # ------------------------------------------------------------
    active_task_curr = st.session_state.shift_tasks[st.session_state.active_task_idx % len(st.session_state.shift_tasks)]

    def process_copilot_query(query_text):
        q = str(query_text).lower()
        print(f"[COPILOT BACKEND LOG] Executing process_copilot_query for input: '{query_text}'")
        
        # Fresh, live serialization of current state at query time
        live_context = {
            "machine_id": str(current_state.machine_id),
            "active_task": str(active_task_curr['name']),
            "task_progress": f"{active_task_curr['progress']}%",
            "task_elapsed_min": active_task_curr['elapsed_min'],
            "task_est_min": active_task_curr['est_min'],
            "safety_score": f"{composite_safety_score}/100",
            "safety_status": str(score_status),
            "main_factor": str(main_factor_text),
            "proximity_zone": str(hazard_zone),
            "proximity_label": str(hazard_label),
            "speed_kmh": f"{speed_kmh:.1f} km/h",
            "active_speed_limit": f"{active_speed_limit:.1f} km/h",
            "fatigue_status": str(fatigue_status),
            "alertness_score": f"{alertness_score:.0f}%",
            "fuel_level_pct": f"{current_state.fuel.level_percent:.1f}%",
            "wasted_fuel_l": f"{wasted_fuel_l:.1f} L",
            "co2_waste_kg": f"{co2_kg:.1f} kg",
            "machine_health": f"{current_state.machine_health_score:.1f}%",
            "engine_temp": f"{current_state.engine.temperature_c:.1f}°C",
            "hydraulic_press": f"{current_state.hydraulics.pressure_bar:.1f} bar"
        }
        st.session_state.copilot_last_debug_context = live_context

        # Securely read Groq API key from Streamlit secrets or environment
        groq_key = ""
        try:
            if "GROQ_API_KEY" in st.secrets:
                groq_key = str(st.secrets["GROQ_API_KEY"]).strip()
        except Exception:
            pass
        if not groq_key:
            import os
            groq_key = os.environ.get("GROQ_API_KEY", "").strip()

        if not groq_key:
            resp = "⚠️ Assistant unavailable: GROQ_API_KEY is not configured."
            detail = "Please create `.streamlit/secrets.toml` containing `GROQ_API_KEY = \"your_groq_api_key_here\"` to activate Groq AI responses."
            return resp, detail

        try:
            from groq import Groq
            client = Groq(api_key=groq_key, timeout=10.0)

            system_prompt = (
                "You are the In-Cab AI Assistant for a heavy excavator operator (Alex M.). "
                "Answer the operator's question directly using the live Digital Twin machine telemetry below.\n"
                "CRITICAL INSTRUCTIONS:\n"
                "1. Keep responses concise (1-3 short spoken sentences max), clear, and direct so it sounds natural when read aloud in a noisy cab.\n"
                "2. State key telemetry numbers accurately when relevant.\n"
                "3. Maintain a professional, encouraging, and safety-focused tone.\n\n"
                f"LIVE TELEMETRY SNAPSHOT:\n"
                f"- Machine ID: {live_context['machine_id']}\n"
                f"- Active Task: {live_context['active_task']} ({live_context['task_progress']} complete, {live_context['task_elapsed_min']}/{live_context['task_est_min']} mins)\n"
                f"- Safety Score: {live_context['safety_score']} ({live_context['safety_status']}) | {live_context['main_factor']}\n"
                f"- Proximity Radar: {live_context['proximity_zone']} zone ({live_context['proximity_label']})\n"
                f"- Speed: {live_context['speed_kmh']} (Limit: {live_context['active_speed_limit']})\n"
                f"- Operator Fatigue: {live_context['fatigue_status']} ({live_context['alertness_score']})\n"
                f"- Fuel Level: {live_context['fuel_level_pct']} (Idle waste: {live_context['wasted_fuel_l']} / {live_context['co2_waste_kg']} CO2)\n"
                f"- Machine Health: {live_context['machine_health']} (Temp: {live_context['engine_temp']}, Hydraulic Pressure: {live_context['hydraulic_press']})\n"
            )

            candidate_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]
            resp = ""
            used_model = "Groq AI"
            last_exception = None

            for m_name in candidate_models:
                try:
                    completion = client.chat.completions.create(
                        model=m_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": query_text}
                        ],
                        temperature=0.3,
                        max_tokens=220
                    )
                    raw_out = (completion.choices[0].message.content or "").strip()
                    if raw_out:
                        resp = raw_out
                        used_model = m_name
                        break
                except Exception as ex:
                    last_exception = ex
                    continue

            if not resp and last_exception:
                raise last_exception

            detail = f"Generated by Groq AI ({used_model}) | Telemetry context: Safety {live_context['safety_score']}, Fuel {live_context['fuel_level_pct']}, Health {live_context['machine_health']}."
            return resp, detail


        except Exception as e:
            err_msg = str(e)
            print(f"[GROQ ERROR] {err_msg}")
            if "invalid_api_key" in err_msg.lower() or "401" in err_msg or "authentication" in err_msg.lower():
                resp = "⚠️ Assistant unavailable: Invalid GROQ_API_KEY provided."
                detail = "Check your API key in `.streamlit/secrets.toml`."
            elif "rate_limit" in err_msg.lower() or "429" in err_msg:
                resp = "⚠️ Assistant unavailable: Groq API rate limit reached."
                detail = "Please wait a moment before trying again."
            elif "timeout" in err_msg.lower():
                resp = "⚠️ Assistant unavailable: Groq API call timed out (10s limit)."
                detail = "Check your internet connection and try again."
            else:
                resp = f"⚠️ Assistant unavailable: Couldn't reach Groq AI backend."
                detail = f"Error details: {err_msg[:120]}"
            return resp, detail

    def generate_shift_summary_groq():
        groq_key = ""
        try:
            if "GROQ_API_KEY" in st.secrets:
                groq_key = str(st.secrets["GROQ_API_KEY"]).strip()
        except Exception:
            pass
        if not groq_key:
            import os
            groq_key = os.environ.get("GROQ_API_KEY", "").strip()

        if not groq_key:
            return {
                "error": True,
                "title": "⚠️ AI Shift Summary Unavailable: GROQ_API_KEY is not configured.",
                "detail": "Please create `.streamlit/secrets.toml` containing `GROQ_API_KEY = \"your_groq_api_key_here\"` to activate Groq AI shift summaries.",
                "highlights": [
                    f"Completed target tasks in active shift cycle.",
                    f"Hydraulic pump pressure maintained smoothly (avg {current_state.hydraulics.pressure_bar:.1f} bar).",
                    f"Finished pre-op inspection checklist ({pre_op_passed_count}/15 passed)."
                ],
                "focus_areas": [
                    f"Fatigue alert status: {fatigue_status} ({alertness_score:.0f}% score).",
                    f"Reduce travel speed near high-density work zones (recorded {speed_kmh:.1f} km/h).",
                    f"Turn off engine during wait queues > 5 mins (idle CO₂: {wasted_fuel_l * DIESEL_CO2_PER_LITER:.1f} kg)."
                ],
                "coaching_tip": f"Great digging control today, Alex! Your safety score is {composite_safety_score}/100 ({score_status}). Your smooth hydraulic application prevented high pressure surges. To reach a 98+ shift score tomorrow, keep travel speed under {active_speed_limit:.1f} km/h and take regular rest breaks."
            }

        tasks_summary = ", ".join([f"{t['name']} ({t['progress']}%)" for t in st.session_state.shift_tasks])
        incidents_summary = ", ".join([f"{inc['type']} ({inc['severity']})" for inc in st.session_state.incident_log[:3]]) or "No severe safety incidents logged."

        prompt_data = (
            f"Operator: Alex M. | Machine: {current_state.machine_id}\n"
            f"Shift Duration: {shift_hours:.1f} hours\n"
            f"Composite Safety Score: {composite_safety_score}/100 ({score_status})\n"
            f"Main Safety Factor: {main_factor_text}\n"
            f"Pre-Op Checklist: {pre_op_passed_count}/15 items passed ({'Clean' if pre_op_all_clean else 'Defects/Incomplete'})\n"
            f"Tasks Status: {tasks_summary}\n"
            f"Recent Safety Incidents/Events: {incidents_summary}\n"
            f"Idle Time: {idle_mins:.1f} mins | Idle Fuel Wasted: {wasted_fuel_l:.1f} L ({co2_kg:.1f} kg CO2)\n"
            f"Fuel Remaining: {current_state.fuel.level_percent:.1f}%\n"
            f"Operator Fatigue / Alertness: {fatigue_status} ({alertness_score:.0f}% score)\n"
            f"Machine Speed & Limits: Current {speed_kmh:.1f} km/h (Limit: {active_speed_limit:.1f} km/h)\n"
            f"Hydraulic Pump Pressure: {current_state.hydraulics.pressure_bar:.1f} bar\n"
        )

        try:
            from groq import Groq
            client = Groq(api_key=groq_key, timeout=10.0)

            system_prompt = (
                "You are an AI Heavy Equipment Shift Performance & Safety Coach for excavator operator Alex M. "
                "Analyze the shift telemetry data and generate a JSON object with exactly three keys:\n"
                "1. \"highlights\": Array of 3 short bullet points celebrating key accomplishments or smooth operation today.\n"
                "2. \"focus_areas\": Array of 3 short bullet points covering specific areas for improvement for the next shift (e.g. speed, idle waste, fatigue).\n"
                "3. \"coaching_tip\": A warm, supportive, encouraging 2-3 sentence personalized coaching advice for Alex M., highlighting positive practices and giving actionable advice for tomorrow.\n\n"
                "Return ONLY valid raw JSON matching this schema, without markdown formatting or codeblocks."
            )

            candidate_models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]
            raw_resp = ""
            last_exception = None

            for m_name in candidate_models:
                try:
                    completion = client.chat.completions.create(
                        model=m_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt_data}
                        ],
                        temperature=0.4,
                        max_tokens=500
                    )
                    out = (completion.choices[0].message.content or "").strip()
                    if out:
                        raw_resp = out
                        break
                except Exception as ex:
                    last_exception = ex
                    continue

            if not raw_resp and last_exception:
                raise last_exception

            if raw_resp.startswith("```"):
                lines = raw_resp.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_resp = "\n".join(lines).strip()


            import json
            parsed = json.loads(raw_resp)
            return {
                "error": False,
                "highlights": parsed.get("highlights", []),
                "focus_areas": parsed.get("focus_areas", []),
                "coaching_tip": parsed.get("coaching_tip", "")
            }

        except Exception as e:
            err_msg = str(e)
            print(f"[GROQ SHIFT SUMMARY ERROR] {err_msg}")
            if "invalid_api_key" in err_msg.lower() or "401" in err_msg or "authentication" in err_msg.lower():
                title = "⚠️ AI Shift Summary Unavailable: Invalid GROQ_API_KEY."
                detail = "Check your API key in `.streamlit/secrets.toml`."
            elif "rate_limit" in err_msg.lower() or "429" in err_msg:
                title = "⚠️ AI Shift Summary Unavailable: Rate Limit Exceeded."
                detail = "Please wait a moment before refreshing."
            elif "timeout" in err_msg.lower():
                title = "⚠️ AI Shift Summary Unavailable: Request Timed Out (10s)."
                detail = "Check your internet connection and try again."
            else:
                title = "⚠️ AI Shift Summary Unavailable: Couldn't reach Groq AI backend."
                detail = f"Error details: {err_msg[:120]}"

            return {
                "error": True,
                "title": title,
                "detail": detail,
                "highlights": [
                    f"Completed target tasks in active shift cycle.",
                    f"Hydraulic pump pressure maintained smoothly (avg {current_state.hydraulics.pressure_bar:.1f} bar).",
                    f"Finished pre-op inspection checklist ({pre_op_passed_count}/15 passed)."
                ],
                "focus_areas": [
                    f"Fatigue alert status: {fatigue_status} ({alertness_score:.0f}% score).",
                    f"Reduce travel speed near high-density work zones (recorded {speed_kmh:.1f} km/h).",
                    f"Turn off engine during wait queues > 5 mins (idle CO₂: {wasted_fuel_l * DIESEL_CO2_PER_LITER:.1f} kg)."
                ],
                "coaching_tip": f"Great digging control today, Alex! Your safety score is {composite_safety_score}/100 ({score_status}). Maintain smooth hydraulic control and take regular rest breaks to keep fatigue low on your next shift."
            }

    # Top-Level Handling of Voice Query Parameter (Ensures execution before any Tab/Radio gating)

    if "voice_query" in st.query_params:
        raw_val = st.query_params.get("voice_query")
        voice_text = raw_val[0] if isinstance(raw_val, list) else str(raw_val or "").strip()
        
        if voice_text:
            print(f"[COPILOT BACKEND LOG] Voice query received at top level: '{voice_text}'")
            st.session_state.op_assistant_nav = "💬 Cab Copilot"
            try:
                resp_str, detail_str = process_copilot_query(voice_text)
                print(f"[COPILOT BACKEND LOG] Voice query processed successfully: '{resp_str[:60]}...'")
                t_now = current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current"
                st.session_state.copilot_history.insert(0, {
                    "time": t_now,
                    "sender": "Copilot",
                    "text": resp_str,
                    "detail": detail_str
                })
                st.session_state.copilot_history.insert(1, {
                    "time": t_now,
                    "sender": "Operator",
                    "text": f"🎤 {voice_text}"
                })
                st.session_state.copilot_last_voice = voice_text
                st.session_state.copilot_last_debug_pipeline = "Button clicked → Query processed → Response received → History updated"
            except Exception as exc:
                print(f"[COPILOT BACKEND ERROR] Exception during process_copilot_query: {exc}")
                import traceback
                traceback.print_exc()
                st.session_state.copilot_last_debug_pipeline = f"ERROR in Backend: {exc}"
            finally:
                try:
                    st.query_params.clear()
                except Exception:
                    pass
                st.rerun()

    # ------------------------------------------------------------
    # IN-CAB TABLET STYLING & GLOVE-FRIENDLY TYPOGRAPHY ENHANCEMENTS
    # ------------------------------------------------------------
    st.markdown(
        """
<style>
/* Cat In-Cab Tablet Navigation CSS System & High-Glare Typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800;900&display=swap');

/* Default / Inactive Button Block - Targets native HTML button DOM node */
div.cab-nav-inactive div[data-testid="stButton"] button,
div.cab-nav-inactive button {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 2px solid #cbd5e1 !important;
    border-left: 6px solid #cbd5e1 !important;
    border-radius: 16px !important;
    height: 74px !important;
    min-height: 74px !important;
    padding: 14px 18px !important;
    font-size: 1.15rem !important; /* ~18-19px BIG text */
    font-weight: 700 !important;
    text-align: left !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    transition: background-color 0.15s ease, border-color 0.15s ease, transform 0.15s ease !important;
    cursor: pointer !important;
}

/* Hover State - Triggers over ANY part of the rectangular button block */
div.cab-nav-inactive div[data-testid="stButton"] button:hover,
div.cab-nav-inactive button:hover {
    background-color: #f8fafc !important;
    border-color: #f59e0b !important;
    border-left: 6px solid #f59e0b !important;
    color: #b45309 !important;
    transform: translateX(4px) !important;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15) !important;
}

/* Active / Selected State (Current Page) */
div.cab-nav-active div[data-testid="stButton"] button,
div.cab-nav-active button {
    background-color: #fffbeb !important; /* Distinct warm gold tint */
    color: #0f172a !important;
    border: 3px solid #f59e0b !important; /* Caterpillar Yellow Accent Border */
    border-left: 12px solid #f59e0b !important; /* Bold 12px Accent Bar */
    border-radius: 16px !important;
    height: 74px !important;
    min-height: 74px !important;
    padding: 14px 18px !important;
    font-size: 1.22rem !important; /* ~20px BIG text */
    font-weight: 800 !important;
    text-align: left !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
    box-shadow: 0 6px 20px rgba(245, 158, 11, 0.25) !important;
    transition: background-color 0.15s ease !important;
    cursor: pointer !important;
}
</style>
""",
        unsafe_allow_html=True
    )

    # LIVE IN-THE-MOMENT COACHING NUDGE (computed early so the sticky bar can show it)
    active_nudge = None
    if hazard_zone == "RED" and "proximity_red_nudge" not in st.session_state.dismissed_nudges:
        active_nudge = {
            "id": "proximity_red_nudge",
            "cat": "HEALTH & SAFETY",
            "icon": "🚨",
            "text": f"PROXIMITY DANGER: Ground worker detected 2.4m behind REAR swing zone!",
            "bg": "#fee2e2", "fg": "#991b1b"
        }
    elif hazard_zone == "AMBER" and "proximity_amber_nudge" not in st.session_state.dismissed_nudges:
        active_nudge = {
            "id": "proximity_amber_nudge",
            "cat": "HEALTH & SAFETY",
            "icon": "⚠️",
            "text": f"PROXIMITY CAUTION: Site pickup truck 6.2m near RIGHT track.",
            "bg": "#fef3c7", "fg": "#92400e"
        }
    elif fatigue_status == "TAKE A BREAK" and "fatigue_break_nudge" not in st.session_state.dismissed_nudges:
        active_nudge = {
            "id": "fatigue_break_nudge",
            "cat": "HEALTH & SAFETY",
            "icon": "☕",
            "text": f"Fatigue Alert: Operating {shift_hours:.1f} hrs with elevated idle trend. Mandatory 15-min stretch break recommended.",
            "bg": "#fee2e2", "fg": "#991b1b"
        }
    elif is_overspeed and "overspeed_nudge" not in st.session_state.dismissed_nudges:
        active_nudge = {
            "id": "overspeed_nudge",
            "cat": "HEALTH & SAFETY",
            "icon": "🏎️",
            "text": f"Overspeed Warning: Machine speed ({speed_kmh:.1f} km/h) exceeds safe limit ({active_speed_limit:.1f} km/h).",
            "bg": "#fee2e2", "fg": "#991b1b"
        }
    elif not current_state.safety.seatbelt_fastened and "seatbelt_nudge" not in st.session_state.dismissed_nudges:
        active_nudge = {
            "id": "seatbelt_nudge",
            "cat": "HEALTH & SAFETY",
            "icon": "🚨",
            "text": "Safety Nudge: Buckle seatbelt before initiating boom travel.",
            "bg": "#fee2e2", "fg": "#991b1b"
        }

    # STICKY CAB STATUS BAR — title + safety score + live alert stay pinned on scroll
    _nudge_html = ""
    if active_nudge:
        _cat_badge = "<span style='background:#166534; color:white; font-size:0.72rem; font-weight:800; padding:0.2rem 0.55rem; border-radius:6px; margin-right:0.55rem;'>🛡️ HEALTH & SAFETY</span>"
        _nudge_html = (
            f"<div style='margin-top:0.6rem;background-color:{active_nudge['bg']};color:{active_nudge['fg']};"
            f"padding:0.65rem 0.9rem;border-radius:12px;font-weight:700;font-size:0.98rem;'>"
            f"{_cat_badge}{active_nudge['icon']} {active_nudge['text']}</div>"
        )

    # Twin warnings merged into the same sticky block, so the dashboard
    # alert bar shows Digital Twin faults on every record.
    _twin_bar_alerts = _active_twin_alerts()

    _twin_html = "".join(
        _twin_alert_banner_html(a) for a in _twin_bar_alerts
    )

    st.markdown(
        f"""
<div class="cab-sticky-bar" style="background:#eef2f6;padding:0.4rem 0.1rem 0.6rem 0.1rem;">
<div style="background:linear-gradient(90deg, rgba(245,168,0,0.22), transparent 55%), linear-gradient(135deg, #0f172a 0%, #1e293b 70%);padding:0.85rem 1.2rem;border-radius:16px;color:white;display:flex;align-items:center;justify-content:space-between;gap:0.8rem;flex-wrap:wrap;border:1px solid rgba(245,168,0,0.35);box-shadow:0 8px 22px rgba(15,23,42,0.25);">
<div>
<div style="font-size:0.7rem;font-weight:800;letter-spacing:0.14em;color:#fbbf24;">VISIONLINK CAB OS · SHIFT A</div>
<span style="font-size:1.35rem;font-weight:900;letter-spacing:-0.01em;">🚜 Operator Workspace</span>
<span style="color:#cbd5e1;font-size:0.95rem;font-weight:700;margin-left:0.7rem;">| {current_state.machine_id} · Alex M.</span>
</div>
<div style="background-color:{score_bg};color:{score_color};font-weight:800;padding:0.55rem 1rem;border-radius:999px;font-size:1rem;white-space:nowrap;">
{score_icon} SAFETY: {composite_safety_score} ({score_status})
</div>
</div>
{_nudge_html}
{_twin_html}
</div>
""",
        unsafe_allow_html=True
    )

    # Quick actions under the sticky bar (Copilot shortcut + Dismiss buttons)
    _act_cols = st.columns([2.2, 1, 1] if _twin_bar_alerts else [3, 1])
    with _act_cols[0]:
        if st.button("💬 OPEN CAB COPILOT", use_container_width=True, key="quick_copilot_hdr"):
            st.session_state.op_assistant_nav = "💬 Cab Copilot"
            st.rerun()
    with _act_cols[1]:
        if active_nudge:
            if st.button("✖ DISMISS", key=f"dismiss_{active_nudge['id']}", use_container_width=True):
                st.session_state.dismissed_nudges.add(active_nudge['id'])
                st.rerun()
        elif not _twin_bar_alerts:
            st.markdown("<div style='text-align:center;color:#16a34a;font-weight:800;padding:0.6rem;'>✅ NO ACTIVE ALERTS</div>", unsafe_allow_html=True)
    if _twin_bar_alerts:
        with _act_cols[2]:
            if st.button(f"✖ DISMISS TWIN ({len(_twin_bar_alerts)})", key="dismiss_all_twin", use_container_width=True):
                for _a in _twin_bar_alerts:
                    st.session_state.dismissed_twin_alerts.add(_a["id"])
                st.rerun()

    # 2-COLUMN LAYOUT (CAT IN-CAB TABLET MENU)
    nav_col, main_col = st.columns([1.45, 3.55])

    with nav_col:
        st.markdown(
            """
<div style="font-size: 0.95rem; font-weight: 900; color: #475569; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 0.8rem; padding-left: 0.4rem;">
🚜 IN-CAB TABLET MENU
</div>
""",
            unsafe_allow_html=True
        )
        
        nav_options = [
            "📋 Shift Tasks",
            "🦺 Safety & Hazard Radar",
            "🌱 Fuel & Pattern Alerts",
            "🎓 Training & Pre-Op Hub",
            "💬 Cab Copilot",
            "🤖 Shift Summary",
            "📊 Fleet Overview"
        ]

        for opt in nav_options:
            is_active = (st.session_state.op_assistant_nav == opt)
            css_class = "cab-nav-item cab-nav-active" if is_active else "cab-nav-item cab-nav-inactive"
            circle_icon = "🟡" if is_active else "○"
            btn_text = f"{opt}   {circle_icon}"

            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(btn_text, key=f"nav_btn_{opt}", use_container_width=True):
                st.session_state.op_assistant_nav = opt
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)




    with main_col:
        # (Live alert already shown in the sticky bar above; dismissed via its DISMISS button.)

        # SECTION 1: 📋 SHIFT TASKS
        if st.session_state.op_assistant_nav == "📋 Shift Tasks":
            st.markdown("## 📋 Active Shift Task Focus")
            
            # GATING CHECK: Pre-op checklist must be fully completed and passed without flagged issues
            if not pre_op_complete or pre_op_flagged_count > 0:
                st.markdown(
                    f"""

<div style="background-color: #fee2e2; border: 3px solid #ef4444; border-radius: 18px; padding: 1.2rem; margin-bottom: 1.2rem;">
<div style="display: flex; align-items: center; gap: 1rem;">
<span style="font-size: 2.5rem;">🚫</span>
<div>
<span style="background:#991b1b; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">SHIFT START LOCKED</span>
<div style="font-size: 1.3rem; font-weight: 900; color: #991b1b; margin-top:0.2rem;">PRE-OPERATION CHECKLIST INCOMPLETE OR HAS FLAGGED DEFECTS</div>
<div style="color: #b91c1c; font-size: 1.05rem; font-weight: 700; margin-top: 0.3rem;">
Completed: {pre_op_passed_count}/{len(PRE_OP_CHECKLIST_ITEMS)} items passed | Flagged defects: {pre_op_flagged_count}. Resolve flagged items in the <strong>🎓 Training & Pre-Op Hub</strong> before starting shift tasks.
</div>
</div>
</div>
</div>

""",
                    unsafe_allow_html=True
                )

            tasks = st.session_state.shift_tasks
            idx = st.session_state.active_task_idx % len(tasks)
            active_task = tasks[idx]

            step_c1, step_c2, step_c3 = st.columns([1, 2, 1])
            with step_c1:
                if st.button("⬅ PREVIOUS TASK", use_container_width=True, key="prev_task_btn"):
                    st.session_state.active_task_idx = (idx - 1) % len(tasks)
                    st.rerun()
            with step_c2:
                st.markdown(f"<div style='text-align: center; font-weight: 800; font-size: 1.1rem; color: #475569;'>TASK {idx + 1} OF {len(tasks)}</div>", unsafe_allow_html=True)
            with step_c3:
                if st.button("NEXT TASK ➔", use_container_width=True, key="next_task_btn"):
                    st.session_state.active_task_idx = (idx + 1) % len(tasks)
                    st.rerun()

            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

            with st.container(border=True):
                t_badge_bg = "#dcfce7" if active_task['status'] == "Completed" else ("#fef3c7" if active_task['status'] == "In-Progress" else "#f1f5f9")
                t_badge_fg = "#166534" if active_task['status'] == "Completed" else ("#92400e" if active_task['status'] == "In-Progress" else "#475569")
                
                st.markdown(
                    f"""

<div style="background-color: #f8fafc; border-radius: 16px; padding: 1.5rem; border: 1px solid #e2e8f0;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<span style="background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px; margin-right:0.6rem;">⚡ OPERATING EFFICIENCY</span>
<span style="font-size: 1.8rem; font-weight: 900; color: #0f172a;">{active_task['name']}</span>
</div>
<span style="font-size: 1.2rem; font-weight: 800; padding: 0.6rem 1.4rem; border-radius: 999px; background-color: {t_badge_bg}; color: {t_badge_fg};">
{active_task['status'].upper()}
</span>
</div>
<div style="font-size: 1.1rem; color: #64748b; margin-top: 0.6rem;">
📍 <strong>Location:</strong> {active_task['zone']} &nbsp;|&nbsp; ⏱️ <strong>Target Duration:</strong> {active_task['est_min']} Minutes &nbsp;|&nbsp; ⏳ <strong>Elapsed:</strong> {active_task['elapsed_min']} Min
</div>
</div>

""",
                    unsafe_allow_html=True
                )

                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                st.progress(active_task['progress'] / 100.0, text=f"Task Completion (Time Elapsed vs Target): {active_task['progress']}%")

                st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)
                st.markdown("##### 👆 QUICK TAP STATUS TOGGLE")
                
                st_c1, st_c2, st_c3 = st.columns(3)
                with st_c1:
                    if st.button("⏳ MARK PENDING", use_container_width=True, key=f"t_pend_{idx}"):
                        active_task['status'] = "Pending"
                        st.rerun()
                with st_c2:
                    if st.button("▶ MARK IN-PROGRESS", use_container_width=True, key=f"t_inprog_{idx}"):
                        if not pre_op_complete or pre_op_flagged_count > 0:
                            st.error("🚫 Cannot start shift task! Resolve flagged items in Pre-Op Checklist first.")
                        else:
                            active_task['status'] = "In-Progress"
                            st.rerun()
                with st_c3:
                    if st.button("✅ MARK COMPLETED", use_container_width=True, key=f"t_comp_{idx}"):
                        active_task['status'] = "Completed"
                        active_task['progress'] = 100
                        st.rerun()

            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("### 📊 Shift Task Summary Grid")
            
            for i, t in enumerate(tasks):
                is_curr = (i == idx)
                border_color = "#0284c7" if is_curr else "#cbd5e1"
                bg_color = "#f0f9ff" if is_curr else "#ffffff"
                
                with st.container(border=True):
                    grid_c1, grid_c2, grid_c3 = st.columns([3, 1.2, 1.2])
                    with grid_c1:
                        curr_indicator = "👉 " if is_curr else ""
                        st.markdown(f"**{curr_indicator}Task {i+1}: {t['name']}**")
                        st.caption(f"Zone: {t['zone']} | Est: {t['est_min']} mins")
                    with grid_c2:
                        st.markdown(f"**Progress:** {t['progress']}%")
                    with grid_c3:
                        st.markdown(f"**Status:** `{t['status']}`")

        # SECTION 2: 🦺 SAFETY & HAZARD RADAR
        elif st.session_state.op_assistant_nav == "🦺 Safety & Hazard Radar":
            st.markdown("## 🦺 Safety & Hazard Radar System")

            # OPERATOR SAFETY SCORE (GLANCEABLE DEFAULT VIEW + SEE DETAILS EXPANDER)

            st.markdown(
                f"""

<div style="background-color: {score_bg}; border: 3px solid {score_color}; border-radius: 20px; padding: 1.4rem; margin-bottom: 0.8rem;">
<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
<div style="display: flex; align-items: center; gap: 1.2rem;">
<span style="font-size: 3.5rem;">{score_icon}</span>
<div>
<span style="background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
<div style="font-size: 2.2rem; font-weight: 900; color: #0f172a; margin-top:0.2rem;">{composite_safety_score} <span style="font-size: 1.3rem; color: {score_color}; font-weight: 800;">— {score_status}</span></div>
<div style="color: {score_color}; font-size: 1.05rem; font-weight: 700;">{main_factor_text} &nbsp;|&nbsp; Trend: {score_trend}</div>
</div>
</div>
</div>
</div>

""",
                unsafe_allow_html=True
            )

            with st.expander("🔍 See details (Full Weighted Breakdown)", expanded=False):
                st.write("**Base Score:** 100 Points")
                if pre_op_all_clean:
                    st.write("🟢 **+5 Pts:** Clean Pre-Operation Checklist Passed")
                if training_bonus > 0:
                    st.write("🟢 **+3 Pts:** Training Modules Passed Bonus")
                if not score_deductions and pre_op_all_clean:
                    st.success("No safety score deductions active!")
                else:
                    for d in score_deductions:
                        st.write(f"🔴 **{d['pts']} Pts ({d['issue']}):** {d['details']}")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            
            # COMPOSITE FATIGUE & ATTENTION-DRIFT SCORING MODULE (FEATURE 2 DISPLAY)
            st.markdown(
                f"""

<div style="background-color: {fatigue_bg}; border: 3px solid {fatigue_color}; border-radius: 20px; padding: 1.4rem; margin-bottom: 0.8rem;">
<div style="display: flex; align-items: center; justify-content: space-between;">
<div style="display: flex; align-items: center; gap: 1.2rem;">
<span style="font-size: 3rem;">{fatigue_icon}</span>
<div>
<span style="background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
<div style="font-size: 1.6rem; font-weight: 900; color: {fatigue_color}; margin-top:0.2rem;">FATIGUE & ALERTNESS: {fatigue_status} ({alertness_score:.0f}%)</div>
<div style="color: {fatigue_color}; font-size: 1.05rem; font-weight: 700;">{fatigue_reason}</div>
</div>
</div>
</div>
</div>

""",
                unsafe_allow_html=True
            )

            with st.expander("🔍 See fatigue & attention breakdown", expanded=False):
                st.write(f"**Composite Alertness Score:** {alertness_score:.0f} / 100 ({fatigue_status})")
                st.write(f"• **Shift Duration:** {shift_hours:.1f} hrs elapsed (-{duration_penalty:.1f} pts)")
                st.write(f"• **Idle-to-Active Trend:** {recent_idle_avg:.1f} min avg (-{idle_trend_penalty:.1f} pts)")
                st.write(f"• **Time-of-Day Risk:** Circadian risk factor (-{time_of_day_risk:.1f} pts)")
                st.write(f"• **Reaction Consistency Proxy:** Task pace variance (-{reaction_variance_penalty:.1f} pts)")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

            # TOP-DOWN ANIMATED RADAR (REDESIGN)
            st.markdown("### 📡 3-Zone Top-Down Proximity Radar")
            st.caption("Live 360° sweep · RED < 3.0 m · AMBER 3–10 m · GREEN > 10 m · Swing radius shaded red.")

            _dir_angle = {"FRONT": -90, "RIGHT": 0, "REAR": 90, "LEFT": 180, "NONE": -90}
            _ang = _dir_angle.get(hazard_dir, -90)
            import math as _math
            _radius_px = max(8, min(132, (hazard_dist / 13.0) * 132)) if hazard_zone != "GREEN" else 0
            _rad = _math.radians(_ang)
            _bx = 150 + _radius_px * _math.cos(_rad)
            _by = 150 - _radius_px * _math.sin(_rad) * -1
            # NOTE: screen y grows downward, so invert
            _by = 150 + _radius_px * _math.sin(_rad) * -1
            _by = 150 - _radius_px * _math.sin(_rad)
            # simpler: compute directly
            _bx = 150 + _radius_px * _math.cos(_rad)
            _by = 150 + _radius_px * _math.sin(_rad)

            _blip_color = "#dc2626" if hazard_zone == "RED" else ("#f59e0b" if hazard_zone == "AMBER" else "#22c55e")
            _ring_color = "#dc2626" if hazard_zone == "RED" else ("#f59e0b" if hazard_zone == "AMBER" else "#22c55e")
            _panel_bg = "#fef2f2" if hazard_zone == "RED" else ("#fffbeb" if hazard_zone == "AMBER" else "#f0fdf4")
            _panel_bd = "#ef4444" if hazard_zone == "RED" else ("#f59e0b" if hazard_zone == "AMBER" else "#22c55e")
            _status_txt = "🔴 RED DANGER — STOP SWING" if hazard_zone == "RED" else ("🟡 AMBER CAUTION — SLOW TO < 2 KM/H" if hazard_zone == "AMBER" else "🟢 GREEN SAFE — ALL ZONES CLEAR")
            _blip_html = (
                f"<circle cx='{_bx:.1f}' cy='{_by:.1f}' r='16' fill='{_blip_color}' opacity='0.22'>"
                f"<animate attributeName='r' values='10;20;10' dur='1.4s' repeatCount='indefinite'/></circle>"
                f"<circle cx='{_bx:.1f}' cy='{_by:.1f}' r='8' fill='{_blip_color}' stroke='white' stroke-width='2.5'/>"
                f"<text x='{_bx:.1f}' y='{_by - 16:.1f}' text-anchor='middle' font-size='12' font-weight='800' fill='{_blip_color}'>{hazard_dist:.1f}m</text>"
                if hazard_zone != "GREEN" else ""
            )
            _sweep_anim = (
                "<g class='radar-sweep'><line x1='150' y1='150' x2='150' y2='18' stroke='#f5a800' stroke-width='3' opacity='0.9'/>"
                "<circle cx='150' cy='150' r='132' fill='none'/></g>"
                if True else ""
            )
            st.markdown(
                f"""
<div style="background:{_panel_bg};border:3px solid {_panel_bd};border-radius:20px;padding:1.2rem 1.4rem;margin-bottom:1.2rem;">
<div style="font-size:1.05rem;font-weight:900;color:#0f172a;text-align:center;margin-bottom:0.2rem;">{_status_txt}</div>
<div style="text-align:center;color:#475569;font-weight:600;font-size:0.92rem;margin-bottom:0.8rem;">{hazard_label}</div>
<div style="display:flex;gap:1.2rem;flex-wrap:wrap;align-items:center;justify-content:center;">
<div style="position:relative;width:300px;height:300px;flex:0 0 300px;">
<svg viewBox="0 0 300 300" style="width:300px;height:300px;display:block;background:radial-gradient(circle,#0f172a 0%,#1e293b 70%);border-radius:50%;border:3px solid {_ring_color};">
<circle cx="150" cy="150" r="132" fill="none" stroke="#334155" stroke-width="1" stroke-dasharray="5 5"/>
<circle cx="150" cy="150" r="102" fill="none" stroke="#f59e0b" stroke-width="1.5" opacity="0.8"/>
<circle cx="150" cy="150" r="40" fill="rgba(220,38,38,0.18)" stroke="#dc2626" stroke-width="2"/>
<text x="150" y="34" text-anchor="middle" font-size="10" font-weight="800" fill="#94a3b8">FRONT · 10m</text>
<text x="150" y="196" text-anchor="middle" font-size="10" font-weight="800" fill="#fca5a5">3m SWING</text>
<text x="22" y="154" text-anchor="middle" font-size="10" font-weight="800" fill="#94a3b8">LEFT</text>
<text x="278" y="154" text-anchor="middle" font-size="10" font-weight="800" fill="#94a3b8">RIGHT</text>
<text x="150" y="272" text-anchor="middle" font-size="10" font-weight="800" fill="#94a3b8">REAR</text>
<g opacity="0.9">
<line x1="150" y1="18" x2="150" y2="282" stroke="#334155" stroke-width="1"/>
<line x1="18" y1="150" x2="282" y2="150" stroke="#334155" stroke-width="1"/>
</g>
{_blip_html}
<g>
<rect x="128" y="128" width="44" height="44" rx="10" fill="#f5a800" stroke="white" stroke-width="2"/>
<text x="150" y="155" text-anchor="middle" font-size="22">🚜</text>
</g>
<g>
<animateTransform attributeName="transform" type="rotate" from="0 150 150" to="360 150 150" dur="4s" repeatCount="indefinite"/>
<line x1="150" y1="150" x2="150" y2="20" stroke="#f5a800" stroke-width="3" opacity="0.85"/>
<polygon points="150,20 144,34 156,34" fill="#f5a800"/>
</g>
</svg>
</div>
<div style="flex:1 1 220px;min-width:220px;">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;">
<div style="background:white;border-radius:12px;padding:0.7rem;border:2px solid {'#ef4444' if hazard_dir=='FRONT' else '#e2e8f0'};text-align:center;font-weight:800;">FRONT<br/><span style="color:{'#dc2626' if hazard_dir=='FRONT' else '#16a34a'};">{'🔴 ' + f'{hazard_dist:.1f}m' if hazard_dir=='FRONT' else '🟢 CLEAR'}</span></div>
<div style="background:white;border-radius:12px;padding:0.7rem;border:2px solid {'#ef4444' if hazard_dir=='REAR' else '#e2e8f0'};text-align:center;font-weight:800;">REAR<br/><span style="color:{'#dc2626' if hazard_dir=='REAR' else '#16a34a'};">{'🔴 ' + f'{hazard_dist:.1f}m' if hazard_dir=='REAR' else '🟢 CLEAR'}</span></div>
<div style="background:white;border-radius:12px;padding:0.7rem;border:2px solid {'#f59e0b' if hazard_dir=='LEFT' else '#e2e8f0'};text-align:center;font-weight:800;">LEFT<br/><span style="color:{'#b45309' if hazard_dir=='LEFT' else '#16a34a'};">{'🟡 ' + f'{hazard_dist:.1f}m' if hazard_dir=='LEFT' else '🟢 CLEAR'}</span></div>
<div style="background:white;border-radius:12px;padding:0.7rem;border:2px solid {'#f59e0b' if hazard_dir=='RIGHT' else '#e2e8f0'};text-align:center;font-weight:800;">RIGHT<br/><span style="color:{'#b45309' if hazard_dir=='RIGHT' else '#16a34a'};">{'🟡 ' + f'{hazard_dist:.1f}m' if hazard_dir=='RIGHT' else '🟢 CLEAR'}</span></div>
</div>
<div style="margin-top:0.7rem;background:#0f172a;color:#f8fafc;border-radius:12px;padding:0.7rem 0.9rem;font-size:0.88rem;font-weight:600;">
{"⛔ STOP swing + sound horn + radio-confirm before ANY movement." if hazard_zone=="RED" else ("⚠️ Reduce speed below 2.0 km/h, horn, confirm obstacle before swinging." if hazard_zone=="AMBER" else "✅ No action needed — maintain sweep watch and normal speed.")}
<br/><span style="color:#fbbf24;">Safe speed now: {active_speed_limit:.1f} km/h · Current: {speed_kmh:.1f} km/h{' · ⚠️ OVERSPEED' if is_overspeed else ''}</span>
</div>
</div>
</div>
</div>
""",
                unsafe_allow_html=True
            )

            # Seatbelt Card
            if current_state.safety.seatbelt_fastened:
                st.markdown(
                    """

<div style="background-color: #f0fdf4; border: 3px solid #22c55e; border-radius: 20px; padding: 1.4rem;">
<div style="display: flex; align-items: center; gap: 1.2rem;">
<span style="font-size: 3rem;">🟢</span>
<div>
<span style="background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
<div style="font-size: 1.6rem; font-weight: 900; color: #166534; margin-top:0.2rem;">SEATBELT SECURE</div>
<div style="color: #15803d; font-size: 1.05rem; font-weight: 600;">Operator seated & safety belt buckled. Safe for operation.</div>
</div>
</div>
</div>

""",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    """

<div style="background-color: #fee2e2; border: 3px solid #ef4444; border-radius: 20px; padding: 1.4rem;">
<div style="display: flex; align-items: center; gap: 1.2rem;">
<span style="font-size: 3rem;">🚨</span>
<div>
<span style="background:#991b1b; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
<div style="font-size: 1.6rem; font-weight: 900; color: #991b1b; margin-top:0.2rem;">SAFETY VIOLATION: SEATBELT UNFASTENED (-10 PTS)</div>
<div style="color: #b91c1c; font-size: 1.05rem; font-weight: 700;">FASTEN SEATBELT IMMEDIATELY BEFORE OPERATING HYDRAULICS!</div>
</div>
</div>
</div>

""",
                    unsafe_allow_html=True
                )

            # Incident Log
            st.markdown("### 📝 Safety Incident Log")
            
            with st.expander("➕ REPORT SITE INCIDENT / HAZARD", expanded=False):
                with st.form("cab_incident_form"):
                    inc_type = st.selectbox("Hazard Category", ["Ground Worker In Zone", "Near-miss", "Hydraulic Warning", "Material Obstacle", "Other"])
                    inc_sev = st.radio("Severity Level", ["INFO", "WARNING", "CRITICAL"], horizontal=True)
                    inc_notes = st.text_input("Brief Details", placeholder="e.g. Worker walked near swing radius without radio call")
                    if st.form_submit_button("LOG INCIDENT NOW", use_container_width=True):
                        st.session_state.incident_log.insert(0, {
                            "time": "Just now",
                            "type": inc_type,
                            "severity": inc_sev,
                            "category": "HEALTH & SAFETY",
                            "impact": "-5 pts",
                            "details": inc_notes or "Manual report logged by operator."
                        })
                        st.success("Incident logged!")
                        st.rerun()

            for inc in st.session_state.incident_log[:5]:
                sev_icon = "🔴" if inc["severity"] == "CRITICAL" else ("🟡" if inc["severity"] == "WARNING" else "🔵")
                cat_tag_html = f"<span style='background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.5rem; border-radius:4px; margin-right:0.5rem;'>🛡️ HEALTH & SAFETY</span>" if inc.get("category") == "HEALTH & SAFETY" else f"<span style='background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.5rem; border-radius:4px; margin-right:0.5rem;'>⚡ OPERATING EFFICIENCY</span>"
                impact_text = f" &nbsp;|&nbsp; Impact: <strong style='color:#ef4444;'>{inc['impact']}</strong>" if "impact" in inc else ""
                with st.container(border=True):
                    st.markdown(f"{cat_tag_html} <span style='font-size: 1.1rem; font-weight: 800;'>{sev_icon} [{inc['time']}] {inc['type']}</span>{impact_text}", unsafe_allow_html=True)
                    st.write(inc["details"])

        # SECTION 3: 🌱 FUEL & PATTERN ALERTS
        elif st.session_state.op_assistant_nav == "🌱 Fuel & Pattern Alerts":
            st.markdown("## 🌱 Fuel Waste & Pattern Alerts")

            shift_history_df = df.iloc[:rec_num + 1] if not df.empty else None
            shift_baseline_idle = shift_history_df['idle_time_minutes'].mean() if shift_history_df is not None and not shift_history_df.empty else 8.5
            idle_ratio_vs_baseline = idle_mins / max(1.0, shift_baseline_idle)

            st.markdown(
                f"""

<div style="background-color: #f0fdf4; border: 3px solid #22c55e; border-radius: 20px; padding: 1.8rem; text-align: center; margin-bottom: 1.2rem;">
<span style="background:#0284c7; color:white; font-size:0.8rem; font-weight:800; padding:0.25rem 0.7rem; border-radius:6px;">⚡ OPERATING EFFICIENCY</span>
<div style="font-size: 1.1rem; color: #166534; font-weight: 800; margin-top:0.4rem;">IDLE FUEL WASTE & EMISSIONS</div>
<div style="font-size: 3rem; font-weight: 900; color: #15803d; margin: 0.4rem 0;">
💨 {co2_kg:.1f} kg CO₂ WASTED
</div>
<div style="font-size: 1.3rem; font-weight: 800; color: #047857;">
⛽ {wasted_fuel_l:.2f} Liters Wasted in Idle Today
</div>
<div style="margin-top: 1rem; padding: 0.8rem; background-color: #dcfce7; border-radius: 12px; font-size: 1.05rem; font-weight: 700; color: #166534;">
🚗 Equivalent to driving a standard passenger car for <strong>{km_equivalent:.1f} km</strong> (based on {DIESEL_CO2_PER_LITER} kg CO₂/L).
</div>
</div>

""",
                unsafe_allow_html=True
            )

            if idle_mins > 15:
                st.markdown(
                    f"""

<div style="background-color: #fef3c7; border: 3px solid #f59e0b; border-radius: 18px; padding: 1.4rem; margin-bottom: 1rem;">
<span style="background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">⚡ OPERATING EFFICIENCY</span>
<div style="font-size: 1.4rem; font-weight: 900; color: #92400e; margin-top:0.3rem;">🟡 EXCESSIVE IDLE PATTERN DETECTED</div>
<div style="font-size: 1.1rem; color: #78350f; margin-top: 0.4rem;">
Current idle time (<strong>{idle_mins:.1f} mins</strong>) is <strong>{idle_ratio_vs_baseline:.1f}x higher</strong> than your shift average ({shift_baseline_idle:.1f} mins).
</div>
<div style="margin-top: 0.8rem; font-size: 1rem; color: #92400e; font-weight: 800;">
💡 1-TAP ADVICE: Turn off engine if waiting more than 5 minutes to save fuel.
</div>
</div>

""",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""

<div style="background-color: #f0fdf4; border: 3px solid #4ade80; border-radius: 18px; padding: 1.4rem; margin-bottom: 1rem;">
<span style="background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">⚡ OPERATING EFFICIENCY</span>
<div style="font-size: 1.4rem; font-weight: 900; color: #166534; margin-top:0.3rem;">🟢 OPTIMAL IDLE PATTERN</div>
<div style="font-size: 1.05rem; color: #15803d; margin-top: 0.3rem;">
Idle time ({idle_mins:.1f} mins) is within target limits (shift avg: {shift_baseline_idle:.1f} mins).
</div>
</div>

""",
                    unsafe_allow_html=True
                )

        # SECTION 4: 🎓 TRAINING & PRE-OP HUB
        elif st.session_state.op_assistant_nav == "🎓 Training & Pre-Op Hub":
            st.markdown("## 🎓 Operator Training & Pre-Op Hub")
            st.caption("Watch video lessons first, then complete your 15-item daily pre-operation walkaround checklist and practice scored scenario modules.")

            hub_tab3, hub_tab1, hub_tab2 = st.tabs(["🎬 Video Training Library", "📋 15-Item Pre-Op Checklist", "🎓 Scored Training Simulations"])

            # PRE-OPERATION CHECKLIST (STEP-THROUGH FLOW)
            with hub_tab1:
                st.markdown("### 📋 Pre-Operation 15-Item Walkaround Checklist")
                
                check_bg = "#f0fdf4" if pre_op_all_clean else ("#fee2e2" if pre_op_flagged_count > 0 else "#fffbeb")
                check_border = "#22c55e" if pre_op_all_clean else ("#ef4444" if pre_op_flagged_count > 0 else "#f59e0b")
                check_title = "🟢 PRE-OPERATION CHECKLIST PASSED — SHIFT READY" if pre_op_all_clean else (f"🔴 DEFECT DETECTED ({pre_op_flagged_count} ITEM(S) FLAGGED)" if pre_op_flagged_count > 0 else f"🟡 INCOMPLETE CHECKLIST ({pre_op_passed_count}/15 PASSED)")

                st.markdown(
                    f"""

<div style="background-color: {check_bg}; border: 3px solid {check_border}; border-radius: 18px; padding: 1.3rem; margin-bottom: 1.2rem;">
<span style="background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🛡️ HEALTH & SAFETY</span>
<div style="font-size: 1.5rem; font-weight: 900; color: #0f172a; margin-top:0.3rem;">{check_title}</div>
<div style="font-size: 1.05rem; color: #334155; margin-top:0.3rem; font-weight: 600;">
Passed: <strong>{pre_op_passed_count} / {len(PRE_OP_CHECKLIST_ITEMS)}</strong> | Flagged Defects: <strong>{pre_op_flagged_count}</strong> | Safety Bonus: <strong>{'+5 Pts' if pre_op_all_clean else ('-5 Pts Defect' if pre_op_flagged_count > 0 else '0 Pts')}</strong>
</div>
</div>

""",
                    unsafe_allow_html=True
                )

                p_idx = st.session_state.active_preop_idx % len(PRE_OP_CHECKLIST_ITEMS)
                item = PRE_OP_CHECKLIST_ITEMS[p_idx]
                curr_status = st.session_state.pre_op_status.get(item["id"], "UNCHECKED")

                # Step controls
                po_c1, po_c2, po_c3 = st.columns([1, 2, 1])
                with po_c1:
                    if st.button("⬅ PREV ITEM", use_container_width=True, key="preop_step_prev"):
                        st.session_state.active_preop_idx = (p_idx - 1) % len(PRE_OP_CHECKLIST_ITEMS)
                        st.rerun()
                with po_c2:
                    st.markdown(f"<div style='text-align: center; font-weight: 800; font-size: 1.1rem; color: #475569;'>ITEM {p_idx + 1} OF {len(PRE_OP_CHECKLIST_ITEMS)}</div>", unsafe_allow_html=True)
                with po_c3:
                    if st.button("NEXT ITEM ➔", use_container_width=True, key="preop_step_next"):
                        st.session_state.active_preop_idx = (p_idx + 1) % len(PRE_OP_CHECKLIST_ITEMS)
                        st.rerun()

                st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
                st.progress((p_idx + 1) / len(PRE_OP_CHECKLIST_ITEMS), text=f"Step Inspection Progress: Item {p_idx + 1} of {len(PRE_OP_CHECKLIST_ITEMS)}")

                card_bg = "#f0fdf4" if curr_status == "PASSED" else ("#fee2e2" if curr_status == "ISSUE_FLAGGED" else "#f8fafc")
                card_border = "#22c55e" if curr_status == "PASSED" else ("#ef4444" if curr_status == "ISSUE_FLAGGED" else "#cbd5e1")
                cat_icon = "💧" if item["cat"] == "Fluids & Engine" else ("⚙️" if item["cat"] == "Mechanical" else ("🦺" if item["cat"] in ["Cab & Safety", "Safety Equipment"] else "⚡"))

                with st.container(border=True):
                    st.markdown(
                        f"""

<div style="background-color: {card_bg}; border: 3px solid {card_border}; border-radius: 20px; padding: 1.8rem; margin-bottom: 1.2rem;">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
<div>
<span style="background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px; margin-right:0.6rem;">{item['cat'].upper()}</span>
<span style="font-size: 1.7rem; font-weight: 900; color: #0f172a;">{cat_icon} {p_idx+1}. {item['name']}</span>
</div>
<span style="font-size: 1.1rem; font-weight: 800; padding: 0.4rem 1.2rem; border-radius: 999px; background-color: {'#dcfce7' if curr_status=='PASSED' else ('#fee2e2' if curr_status=='ISSUE_FLAGGED' else '#f1f5f9')}; color: {'#166534' if curr_status=='PASSED' else ('#991b1b' if curr_status=='ISSUE_FLAGGED' else '#475569')};">
{'🟢 PASSED' if curr_status=='PASSED' else ('🔴 DEFECT FLAGGED' if curr_status=='ISSUE_FLAGGED' else '⚪ UNCHECKED')}
</span>
</div>
<div style="font-size: 1.15rem; color: #475569; margin-top: 0.8rem; font-weight: 600;">
{item['desc']}
</div>
</div>

""",
                        unsafe_allow_html=True
                    )

                    st.markdown("##### 👆 TAP ACTION (AUTO-ADVANCES TO NEXT ITEM):")
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("✓ PASS ITEM", use_container_width=True, key=f"step_pass_{item['id']}"):
                            st.session_state.pre_op_status[item["id"]] = "PASSED"
                            st.session_state.active_preop_idx = (p_idx + 1) % len(PRE_OP_CHECKLIST_ITEMS)
                            st.rerun()
                    with b2:
                        if st.button("⚠ FLAG ISSUE", use_container_width=True, key=f"step_flag_{item['id']}"):
                            st.session_state.pre_op_status[item["id"]] = "ISSUE_FLAGGED"
                            st.session_state.incident_log.insert(0, {
                                "time": current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current",
                                "type": f"Pre-Op Defect: {item['name']}",
                                "severity": "CRITICAL",
                                "category": "HEALTH & SAFETY",
                                "impact": "-5 pts",
                                "details": f"Flagged during daily pre-op step inspection: {item['desc']}"
                            })
                            st.session_state.active_preop_idx = (p_idx + 1) % len(PRE_OP_CHECKLIST_ITEMS)
                            st.rerun()

                q_c1, q_c2 = st.columns(2)
                with q_c1:
                    if st.button("✅ MARK ALL 15 PASSED (QUICK START)", use_container_width=True, key="pass_all_chk"):
                        for itm in PRE_OP_CHECKLIST_ITEMS:
                            st.session_state.pre_op_status[itm["id"]] = "PASSED"
                        st.success("All 15 pre-operation checklist items marked PASSED!")
                        st.rerun()
                with q_c2:
                    if st.button("🔄 RESET CHECKLIST TO UNCHECKED", use_container_width=True, key="reset_all_chk"):
                        for itm in PRE_OP_CHECKLIST_ITEMS:
                            st.session_state.pre_op_status[itm["id"]] = "UNCHECKED"
                        st.rerun()

                with st.expander("📋 Review All 15 Items Summary", expanded=False):
                    for idx, itm in enumerate(PRE_OP_CHECKLIST_ITEMS):
                        curr_st = st.session_state.pre_op_status.get(itm["id"], "UNCHECKED")
                        st.write(f"**{idx+1}. {itm['name']}**: `{curr_st}`")

            # SCORED TRAINING SIMULATIONS (STEP-THROUGH ONE SCENARIO AT A TIME + WHY? EXPANDER)
            with hub_tab2:
                st.markdown("### 🎓 Scored Scenario Training Simulations")

                tot_mods = len(st.session_state.training_modules)
                passed_mods = sum(1 for m in st.session_state.training_modules if m["status"] == "Passed")
                avg_score_pct = int((passed_mods / max(1, tot_mods)) * 100)

                st.markdown(
                    f"""

<div style="background-color: #f0f9ff; border: 3px solid #0284c7; border-radius: 18px; padding: 1.3rem; margin-bottom: 1.2rem;">
<span style="background:#0284c7; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">🎓 OPERATOR ACADEMY HISTORY</span>
<div style="font-size: 1.5rem; font-weight: 900; color: #0369a1; margin-top:0.3rem;">TRAINING PROGRESS: {passed_mods} / {tot_mods} MODULES PASSED ({avg_score_pct}%)</div>
<div style="font-size: 1.05rem; color: #0c4a6e; margin-top:0.2rem; font-weight: 600;">
Safety Score Impact: <strong>{'+3 Pts Bonus' if passed_mods >= 3 else 'Complete 3+ modules for +3 pts safety bonus'}</strong>
</div>
</div>

""",
                    unsafe_allow_html=True
                )

                m_idx = st.session_state.active_train_idx % tot_mods
                mod = st.session_state.training_modules[m_idx]

                # Step controls
                tc1, tc2, tc3 = st.columns([1, 2, 1])
                with tc1:
                    if st.button("⬅ PREV MODULE", use_container_width=True, key="train_step_prev"):
                        st.session_state.active_train_idx = (m_idx - 1) % tot_mods
                        st.rerun()
                with tc2:
                    st.markdown(f"<div style='text-align: center; font-weight: 800; font-size: 1.1rem; color: #475569;'>MODULE {m_idx + 1} OF {tot_mods}</div>", unsafe_allow_html=True)
                with tc3:
                    if st.button("NEXT MODULE ➔", use_container_width=True, key="train_step_next"):
                        st.session_state.active_train_idx = (m_idx + 1) % tot_mods
                        st.rerun()

                st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

                m_status = mod["status"]
                m_border = "#22c55e" if m_status == "Passed" else ("#f59e0b" if m_status == "Needs Review" else "#cbd5e1")
                m_bg = "#f0fdf4" if m_status == "Passed" else ("#fffbeb" if m_status == "Needs Review" else "#ffffff")

                with st.container(border=True):
                    st.markdown(
                        f"""

<div style="background-color: {m_bg}; padding: 1.4rem; border-radius: 18px; border: 3px solid {m_border}; margin-bottom: 1rem;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span style="font-size: 1.4rem; font-weight: 900; color: #0f172a;">{mod['title']}</span>
<span style="background: {'#166534' if m_status=='Passed' else ('#92400e' if m_status=='Needs Review' else '#64748b')}; color: white; padding: 0.3rem 0.9rem; border-radius: 999px; font-weight: 800; font-size: 0.9rem;">
{m_status.upper()}
</span>
</div>
<div style="font-size: 1.15rem; color: #334155; margin-top: 0.8rem; font-weight: 600;">
📝 <strong>Scenario:</strong> {mod['scenario']}
</div>
</div>

""",
                        unsafe_allow_html=True
                    )

                    st.markdown("##### 👆 TAP YOUR DECISION OPTION:")
                    for opt_idx, opt_text in enumerate(mod["options"]):
                        is_chosen = (mod["user_answer"] == opt_idx)
                        is_correct = (opt_idx == mod["correct_idx"])

                        btn_label = f"{'✅ ' if is_chosen and is_correct else ('❌ ' if is_chosen and not is_correct else '')}{opt_text}"
                        if st.button(btn_label, key=f"mod_step_{m_idx}_opt_{opt_idx}", use_container_width=True):
                            mod["user_answer"] = opt_idx
                            if opt_idx == mod["correct_idx"]:
                                mod["status"] = "Passed"
                            else:
                                mod["status"] = "Needs Review"
                            st.rerun()

                    if mod["user_answer"] is not None:
                        if mod["user_answer"] == mod["correct_idx"]:
                            st.markdown(
                                """

<div style="background-color: #dcfce7; border: 2px solid #22c55e; border-radius: 14px; padding: 0.9rem 1.2rem; margin-top: 0.8rem; font-weight: 800; font-size: 1.2rem; color: #166534;">
🟢 Correct! (+25 Pts)
</div>

""",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                """

<div style="background-color: #fef3c7; border: 2px solid #f59e0b; border-radius: 14px; padding: 0.9rem 1.2rem; margin-top: 0.8rem; font-weight: 800; font-size: 1.2rem; color: #92400e;">
🔴 Not quite — review coaching explanation below.
</div>

""",
                                unsafe_allow_html=True
                            )

                        with st.expander("❓ Why? (Coaching Explanation)", expanded=False):
                            st.info(f"💡 **Coaching Explanation**: {mod['explanation']}")

        # ----- VIDEO TRAINING LIBRARY TAB -----
            with hub_tab3:
                st.markdown(
                    """
                    <div class="video-library-hero">
                        <h3>🎬 Video Training Library</h3>
                        <p>Watch assigned safety & efficiency lessons, then add your own site videos via link or MP4 upload. Progress syncs to your safety score.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                vids = st.session_state.training_videos
                total_v = len(vids)
                watched_v = sum(1 for v in vids if v.get("watched"))
                sample_v = sum(1 for v in vids if v.get("is_sample"))
                custom_v = total_v - sample_v

                vs1, vs2, vs3, vs4 = st.columns(4)
                with vs1:
                    st.markdown(f"<div class='video-stat'><b>{total_v}</b><span>Total Videos</span></div>", unsafe_allow_html=True)
                with vs2:
                    st.markdown(f"<div class='video-stat'><b>{watched_v}/{total_v}</b><span>Watched</span></div>", unsafe_allow_html=True)
                with vs3:
                    st.markdown(f"<div class='video-stat'><b>{sample_v}</b><span>Sample Lessons</span></div>", unsafe_allow_html=True)
                with vs4:
                    st.markdown(f"<div class='video-stat'><b>{custom_v}</b><span>Site Uploads</span></div>", unsafe_allow_html=True)

                st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
                if total_v > 0:
                    st.progress(watched_v / max(1, total_v), text=f"Library completion: {watched_v}/{total_v} watched ({int(watched_v/max(1,total_v)*100)}%)")

                # Add-video form
                with st.expander("➕ ADD NEW TRAINING VIDEO (Link or MP4 Upload)", expanded=False):
                    with st.form("add_training_video_form", clear_on_submit=True):
                        nv_title = st.text_input("Video Title *", placeholder="e.g. Night Shift Lighting Setup — Stockpile A")
                        c1, c2 = st.columns(2)
                        with c1:
                            nv_cat = st.selectbox("Category", ["HEALTH & SAFETY", "OPERATING EFFICIENCY", "MAINTENANCE", "SITE INDUCTION"])
                        with c2:
                            nv_level = st.selectbox("Skill Level", ["Beginner", "Intermediate", "Advanced"])
                        nv_desc = st.text_area("What will the operator learn?", placeholder="3-4 key takeaways from this video…")
                        nv_url = st.text_input("Video URL (YouTube / MP4 link)", placeholder="https://www.youtube.com/watch?v=…  or  https://…/video.mp4")
                        nv_file = st.file_uploader("…or upload MP4 / WebM from this device", type=["mp4", "webm", "mov"])
                        nv_dur = st.text_input("Duration label", placeholder="e.g. 4:32", value="")

                        submitted = st.form_submit_button("📥 SAVE TO LIBRARY", use_container_width=True)
                        if submitted:
                            if not nv_title.strip():
                                st.error("Please enter a video title.")
                            elif not nv_url.strip() and nv_file is None:
                                st.error("Paste a video URL or upload a video file.")
                            else:
                                import time as _time
                                vid_src = nv_url.strip() if nv_url.strip() else nv_file
                                new_vid = {
                                    "id": f"vid_{int(_time.time())}",
                                    "title": nv_title.strip(),
                                    "category": nv_cat,
                                    "level": nv_level,
                                    "duration": nv_dur.strip() or "—",
                                    "description": nv_desc.strip() or "Site training video added by supervisor.",
                                    "url": vid_src,
                                    "watched": False,
                                    "is_sample": False,
                                }
                                st.session_state.training_videos.insert(0, new_vid)
                                st.success(f"✅ \"{nv_title.strip()}\" added to the library!")
                                st.rerun()

                    st.caption("Tip: YouTube links play inline. MP4 uploads play instantly and stay in this session — for permanent storage, upload to your site drive and paste the link.")

                # Filter + search
                f1, f2 = st.columns([1, 2])
                with f1:
                    cats = ["All"] + sorted(set(v.get("category", "General") for v in vids))
                    st.session_state.video_filter = st.selectbox("Filter by category", cats, index=cats.index(st.session_state.video_filter) if st.session_state.video_filter in cats else 0)
                with f2:
                    video_search = st.text_input("Search videos", placeholder="Search title or description…", label_visibility="collapsed")

                filt = st.session_state.video_filter
                q = (video_search or "").lower().strip()
                filtered = [v for v in vids if (filt == "All" or v.get("category") == filt) and (not q or q in v.get("title","").lower() or q in v.get("description","").lower())]

                if not filtered:
                    st.info("No videos match this filter. Try another category or add a new video above.")
                else:
                    for v in filtered:
                        cat = v.get("category", "General")
                        badge_cls = "safety" if cat == "HEALTH & SAFETY" else ("efficiency" if cat == "OPERATING EFFICIENCY" else ("maintenance" if cat == "MAINTENANCE" else "default"))
                        watched_tag = "✅ WATCHED" if v.get("watched") else "○ NOT WATCHED"
                        sample_tag = " · SAMPLE" if v.get("is_sample") else " · SITE VIDEO"
                        with st.container(border=True):
                            st.markdown(
                                f"<div class='video-card-top'><span class='video-badge {badge_cls}'>{cat}</span> "
                                f"<span style='font-size:0.78rem;font-weight:800;color:#64748b;margin-left:0.5rem;'>{v.get('level','')} · ⏱ {v.get('duration','—')} · {watched_tag}{sample_tag}</span>"
                                f"<div style='font-size:1.25rem;font-weight:900;color:#0f172a;margin-top:0.3rem;'>🎬 {v.get('title')}</div>"
                                f"<div style='color:#475569;font-size:0.95rem;margin-top:0.2rem;'>{v.get('description')}</div></div>",
                                unsafe_allow_html=True
                            )
                            try:
                                st.video(v.get("url"))
                            except Exception:
                                st.warning("Unable to play this video source. Check the URL.")
                            b1, b2, b3 = st.columns([1, 1, 1])
                            with b1:
                                if st.button(("↩ MARK UNWATCHED" if v.get("watched") else "✅ MARK WATCHED"), key=f"watch_{v['id']}", use_container_width=True):
                                    v["watched"] = not v.get("watched")
                                    st.rerun()
                            with b2:
                                if v.get("url") and isinstance(v.get("url"), str) and v["url"].startswith("http"):
                                    st.link_button("🔗 OPEN SOURCE", v["url"], use_container_width=True)
                                else:
                                    st.caption("Local upload — plays inline only.")
                            with b3:
                                if st.button("🗑 DELETE", key=f"del_{v['id']}", use_container_width=True):
                                    st.session_state.training_videos = [x for x in st.session_state.training_videos if x["id"] != v["id"]]
                                    st.success("Video removed.")
                                    st.rerun()

        # SECTION 5: 💬 IN-CAB CONVERSATIONAL COPILOT (FEATURE 1)
        elif st.session_state.op_assistant_nav == "💬 Cab Copilot":
            st.markdown("## 💬 In-Cab Voice & Text Conversational Copilot")
            st.caption("Ask natural voice or typed questions grounded in live telemetry, active tasks, safety score, and fuel data.")

            cp_top1, cp_top2 = st.columns([3, 1])
            with cp_top1:
                audio_status_text = "🔊 AUDIO VOICE RESPONSES ENABLED" if st.session_state.copilot_audio_enabled else "🔇 AUDIO VOICE RESPONSES MUTED"
                audio_status_color = "#166534" if st.session_state.copilot_audio_enabled else "#991b1b"
                st.markdown(f"<div style='font-size: 1.05rem; font-weight: 800; color: {audio_status_color};'>{audio_status_text}</div>", unsafe_allow_html=True)
            with cp_top2:
                if st.button("🔊 TOGGLE AUDIO", use_container_width=True, key="toggle_copilot_audio"):
                    st.session_state.copilot_audio_enabled = not st.session_state.copilot_audio_enabled
                    st.rerun()

            # Active Task info for context
            active_task_curr = st.session_state.shift_tasks[st.session_state.active_task_idx % len(st.session_state.shift_tasks)]

            latest_resp_text = st.session_state.copilot_history[0]['text'].replace('"', "'").replace('\n', ' ') if st.session_state.copilot_history else "Ready for query"

            # ------------------------------------------------------------
            # NATIVE IN-CAB VOICE INPUT (STREAMLIT + GROQ WHISPER AI)
            # ------------------------------------------------------------
            with st.container(border=True):
                st.markdown("### 🎙️ Hands-Free Voice Input (Groq Whisper AI)")
                st.caption("Click the microphone below, speak your question in English, and tap stop. Groq Whisper AI will transcribe and answer instantly!")
                recorded_audio = st.audio_input("Tap microphone icon to record voice query", key="copilot_voice_recorder")

                if recorded_audio is not None:
                    audio_bytes = recorded_audio.read()
                    audio_hash = hash(audio_bytes)
                    if getattr(st.session_state, "last_processed_audio_hash", None) != audio_hash:
                        st.session_state.last_processed_audio_hash = audio_hash
                        with st.spinner("⚡ Transcribing voice audio via Groq Whisper AI..."):
                            groq_key = ""
                            try:
                                if "GROQ_API_KEY" in st.secrets:
                                    groq_key = str(st.secrets["GROQ_API_KEY"]).strip()
                            except Exception:
                                pass
                            if not groq_key:
                                import os
                                groq_key = os.environ.get("GROQ_API_KEY", "").strip()

                            transcribed_text = ""
                            if groq_key:
                                try:
                                    from groq import Groq
                                    client = Groq(api_key=groq_key, timeout=10.0)
                                    audio_filename = getattr(recorded_audio, "name", "voice_input.wav") or "voice_input.wav"
                                    transcription = client.audio.transcriptions.create(
                                        model="whisper-large-v3-turbo",
                                        file=(audio_filename, audio_bytes),
                                        response_format="text"
                                    )
                                    transcribed_text = str(transcription or "").strip()
                                except Exception as e:
                                    print(f"[GROQ WHISPER ERROR] {e}")

                            if transcribed_text:
                                st.success(f"🎤 Voice Recognized: \"{transcribed_text}\"")
                                resp_str, detail_str = process_copilot_query(transcribed_text)
                                t_now = current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current"
                                st.session_state.copilot_history.insert(0, {
                                    "time": t_now,
                                    "sender": "Copilot",
                                    "text": resp_str,
                                    "detail": detail_str
                                })
                                st.session_state.copilot_history.insert(1, {
                                    "time": t_now,
                                    "sender": "Operator",
                                    "text": f"🎤 {transcribed_text}"
                                })
                                st.rerun()
                            else:
                                st.warning("⚠️ Could not detect spoken words in the audio. Please speak clearly into your microphone or type your question below.")


            # ------------------------------------------------------------
            # STAGE 3 — RESPONSE DELIVERY (TEXT & TRANSCRIPT)
            # ------------------------------------------------------------
            if st.session_state.copilot_history:
                last_msg = st.session_state.copilot_history[0]
                resp_bg = "#f0fdf4" if last_msg["sender"] == "Copilot" else "#f0f9ff"
                resp_border = "#22c55e" if last_msg["sender"] == "Copilot" else "#0284c7"
                resp_icon = "🤖 COPILOT RESPONSE" if last_msg["sender"] == "Copilot" else "👷 OPERATOR QUESTION"

                st.markdown(
                    f"""

<div style="background-color: {resp_bg}; border: 3px solid {resp_border}; border-radius: 20px; padding: 1.6rem; margin-bottom: 1rem;">
<span style="background:{'#166534' if last_msg['sender']=='Copilot' else '#0284c7'}; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:6px;">{resp_icon}</span>
<div style="font-size: 1.4rem; font-weight: 900; color: #0f172a; margin-top: 0.5rem;">
"{last_msg['text']}"
</div>
<div style="font-size: 0.9rem; color: #64748b; margin-top: 0.4rem; font-weight: 600;">
⏱️ Logged at {last_msg['time']}
</div>
</div>

""",
                    unsafe_allow_html=True
                )

                if last_msg.get("detail"):
                    with st.expander("💡 Want more detail?", expanded=False):
                        st.info(last_msg["detail"])

            # Interactive Input Form for Queries
            st.markdown("##### 👆 TYPE OR ASK A QUESTION:")
            with st.form("copilot_query_form"):
                user_q = st.text_input("Operator Query", placeholder="e.g. How am I doing? / What's my next task? / How much fuel left?", label_visibility="collapsed")
                c_submit = st.form_submit_button("SEND QUESTION TO COPILOT ➔", use_container_width=True)

                if c_submit and user_q.strip():
                    q_text = user_q.strip()
                    resp_str, detail_str = process_copilot_query(q_text)

                    t_now = current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current"
                    st.session_state.copilot_history.insert(0, {
                        "time": t_now,
                        "sender": "Copilot",
                        "text": resp_str,
                        "detail": detail_str
                    })
                    st.session_state.copilot_history.insert(1, {
                        "time": t_now,
                        "sender": "Operator",
                        "text": q_text
                    })
                    st.rerun()

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

            # Sample Quick Tap Question Buttons
            st.markdown("##### 💡 QUICK SAMPLE QUESTION TAPS:")
            sq1, sq2, sq3 = st.columns(3)
            with sq1:
                if st.button("❓ How am I doing?", use_container_width=True, key="sq_how"):
                    resp_str, detail_str = process_copilot_query("How am I doing?")
                    t_now = current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current"
                    st.session_state.copilot_history.insert(0, {"time": t_now, "sender": "Copilot", "text": resp_str, "detail": detail_str})
                    st.session_state.copilot_history.insert(1, {"time": t_now, "sender": "Operator", "text": "How am I doing?"})
                    st.rerun()
            with sq2:
                if st.button("❓ What's my next task?", use_container_width=True, key="sq_task"):
                    resp_str, detail_str = process_copilot_query("What's my next task?")
                    t_now = current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current"
                    st.session_state.copilot_history.insert(0, {"time": t_now, "sender": "Copilot", "text": resp_str, "detail": detail_str})
                    st.session_state.copilot_history.insert(1, {"time": t_now, "sender": "Operator", "text": "What's my next task?"})
                    st.rerun()
            with sq3:
                if st.button("❓ Fuel level & waste?", use_container_width=True, key="sq_fuel"):
                    resp_str, detail_str = process_copilot_query("Fuel level and waste?")
                    t_now = current_state.timestamp.split(" ")[-1] if " " in str(current_state.timestamp) else "Current"
                    st.session_state.copilot_history.insert(0, {"time": t_now, "sender": "Copilot", "text": resp_str, "detail": detail_str})
                    st.session_state.copilot_history.insert(1, {"time": t_now, "sender": "Operator", "text": "Fuel level and waste?"})
                    st.rerun()

            with st.expander("📜 Conversation History Transcript", expanded=False):
                for h in st.session_state.copilot_history:
                    icon_tag = "🤖 Copilot" if h["sender"] == "Copilot" else "👷 Operator"
                    st.write(f"**[{h['time']}] {icon_tag}:** {h['text']}")

            # ------------------------------------------------------------
            # PERSISTENT DEV-MODE DEBUG / STATUS INDICATOR
            # ------------------------------------------------------------
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            show_dev_debug = st.checkbox("🛠️ COPILOT PIPELINE DEBUGGER (DEV MODE)", value=False, key="copilot_dev_mode_toggle")
            
            if show_dev_debug:
                last_voice = getattr(st.session_state, 'copilot_last_voice', 'None recorded yet')
                last_ctx = getattr(st.session_state, 'copilot_last_debug_context', {})
                
                st.markdown(
                    f"""
<div style="background-color: #0f172a; border: 2px dashed #0284c7; border-radius: 14px; padding: 1.2rem; color: #f8fafc; font-family: monospace; font-size: 0.88rem;">
<div style="font-weight: 800; font-size: 1rem; color: #38bdf8; margin-bottom: 0.6rem;">🔍 COPILOT PIPELINE REAL-TIME DIAGNOSTIC STATUS</div>
<div>• <strong>Stage 1 (Voice Input):</strong> Bridge Active | Last Voice Input: <code>{last_voice}</code></div>
<div>• <strong>Stage 2 (Context Passing):</strong> Fresh Telemetry Serialized ({len(last_ctx)} keys captured)</div>
<div>• <strong>Stage 3 (Text Delivery):</strong> History Items Count: <code>{len(st.session_state.copilot_history)}</code></div>
<div>• <strong>Stage 4 (Voice Output):</strong> Audio Status: <code>{'ENABLED' if st.session_state.copilot_audio_enabled else 'MUTED'}</code> | Web Speech TTS Ready</div>
</div>
""",
                    unsafe_allow_html=True
                )
                with st.expander("🔬 View Serialized Telemetry Snapshot (Stage 2)", expanded=False):
                    st.json(last_ctx if last_ctx else {"info": "Trigger a query to view serialized snapshot."})

        # SECTION 6: 🤖 SHIFT SUMMARY
        elif st.session_state.op_assistant_nav == "🤖 Shift Summary":
            st.markdown("## 🤖 Daily Operator AI Shift Summary")
            
            with st.container(border=True):
                c_head1, c_head2 = st.columns([3, 1])
                with c_head1:
                    st.markdown(
                        f"""
<div style="font-size: 1.5rem; font-weight: 900; color: #0f172a;">
📋 Shift Operational Brief & Coaching Digest
</div>
<div style="font-size: 1.05rem; color: #475569; margin-top: 0.3rem;">
Shift Duration: <strong>{shift_hours:.1f} Hours</strong> &nbsp;|&nbsp; Pre-Op Checklist: <strong>{'Passed' if pre_op_all_clean else 'Incomplete/Defect'}</strong> &nbsp;|&nbsp; Safety Score: <strong>{composite_safety_score}/100</strong>
</div>
""",
                        unsafe_allow_html=True
                    )
                with c_head2:
                    if st.button("🔄 Refresh Groq AI Summary", key="btn_refresh_shift_summary", use_container_width=True):
                        st.session_state.ai_shift_summary_data = generate_shift_summary_groq()
                        st.rerun()

            # Auto-generate on first view
            if "ai_shift_summary_data" not in st.session_state or st.session_state.ai_shift_summary_data is None:
                with st.spinner("Generating AI Shift Summary via Groq..."):
                    st.session_state.ai_shift_summary_data = generate_shift_summary_groq()

            summary_res = st.session_state.ai_shift_summary_data

            if summary_res.get("error"):
                st.warning(f"**{summary_res.get('title')}**\n\n{summary_res.get('detail')}")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                with st.container(border=True):
                    st.markdown("#### 🌟 Shift Highlights (Groq AI)")
                    for hl in summary_res.get("highlights", []):
                        st.write(f"• {hl}")
            with c_s2:
                with st.container(border=True):
                    st.markdown("#### ⚠️ Focus Areas for Next Shift (Groq AI)")
                    for fa in summary_res.get("focus_areas", []):
                        st.write(f"• {fa}")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown(
                f"""
<div style="background-color: #f0fdf4; border-left: 6px solid #22c55e; padding: 1.2rem; border-radius: 12px; margin-top: 1.2rem;">
<span style='background:#166534; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.5rem; border-radius:4px; margin-left:0.4rem;'>🛡️ HEALTH & SAFETY</span>
<div style="font-size: 1.2rem; font-weight: 900; color: #166534; margin-top:0.4rem;">🌟 Supportive Operator Coaching Tip</div>
<div style="color: #15803d; font-size: 1.05rem; margin-top: 0.4rem; font-weight: 600;">
"{summary_res.get('coaching_tip', '')}"
</div>
</div>
""",
                unsafe_allow_html=True
            )


        # SECTION 7: 📊 FLEET OVERVIEW (SUPERVISOR VIEW WITH AUTOMATED ESCALATIONS)
        elif st.session_state.op_assistant_nav == "📊 Fleet Overview":
            st.markdown("## 📊 VisionLink Fleet Overview (Supervisor View)")
            st.caption("Fleet-wide productivity, fuel efficiency, machine health benchmarks, and automated supervisor escalation workflow.")

            # SUPERVISOR AUTOMATED ESCALATION CONTROL CENTER
            st.markdown("### 🚨 Automated Supervisor Escalation Control Panel")

            total_esc = len(st.session_state.escalations)
            act_esc = sum(1 for e in st.session_state.escalations if e["status"] == "Active")
            ack_esc = sum(1 for e in st.session_state.escalations if e["status"] == "Acknowledged")
            res_esc = sum(1 for e in st.session_state.escalations if e["status"] == "Resolved")

            esc_m1, esc_m2, esc_m3, esc_m4 = st.columns(4)
            with esc_m1:
                st.metric("Total Escalations", total_esc, delta=f"{act_esc} Active Alerts", delta_color="inverse")
            with esc_m2:
                st.metric("🔴 Active Needs Action", act_esc)
            with esc_m3:
                st.metric("🟡 Acknowledged", ack_esc)
            with esc_m4:
                st.metric("🟢 Resolved Today", res_esc)

            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)

            # Interactive Supervisor Workflow Table for Escalations
            with st.container(border=True):
                st.markdown("#### 🚨 Fleet Safety & Operational Escalation Log")
                st.caption("Centralized real-time alerts automatically triggered by operator cab signals (safety score, proximity breaches, fatigue, seatbelt violations).")

                if not st.session_state.escalations:
                    st.info("🟢 No safety escalations triggered today. All machines operating normally.")
                else:
                    for esc in st.session_state.escalations[:8]:
                        st_bg = "#fee2e2" if esc["status"] == "Active" else ("#fef3c7" if esc["status"] == "Acknowledged" else "#f0fdf4")
                        st_border = "#ef4444" if esc["status"] == "Active" else ("#f59e0b" if esc["status"] == "Acknowledged" else "#22c55e")
                        st_icon = "🔴 ACTIVE" if esc["status"] == "Active" else ("🟡 ACKNOWLEDGED" if esc["status"] == "Acknowledged" else "🟢 RESOLVED")

                        st.markdown(
                            f"""

<div style="background-color: {st_bg}; border: 2px solid {st_border}; border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem;">
<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
<div>
<span style="background:#1e293b; color:white; font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:4px; margin-right:0.5rem;">{esc['machine_id']}</span>
<span style="font-size: 1.15rem; font-weight: 900; color: #0f172a;">{esc['operator']} &nbsp;|&nbsp; {esc['trigger']}</span>
</div>
<span style="font-weight: 800; font-size: 0.95rem; color: #0f172a;">
⏱️ {esc['time']} &nbsp;|&nbsp; <strong>{st_icon}</strong>
</span>
</div>
</div>

""",
                            unsafe_allow_html=True
                        )

                        e_btn1, e_btn2 = st.columns([1, 1])
                        with e_btn1:
                            if esc["status"] != "Acknowledged" and esc["status"] != "Resolved":
                                if st.button("👁️ ACKNOWLEDGE ALERT", key=f"ack_{esc['id']}", use_container_width=True):
                                    esc["status"] = "Acknowledged"
                                    esc["ack_time"] = "Just now"
                                    st.success(f"Escalated alert {esc['id']} marked ACKNOWLEDGED.")
                                    st.rerun()
                        with e_btn2:
                            if esc["status"] != "Resolved":
                                if st.button("✅ MARK RESOLVED", key=f"res_{esc['id']}", use_container_width=True):
                                    esc["status"] = "Resolved"
                                    esc["res_time"] = "Just now"
                                    st.success(f"Escalated alert {esc['id']} marked RESOLVED.")
                                    st.rerun()

            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)

            f_m1, f_m2, f_m3, f_m4 = st.columns(4)
            with f_m1:
                st.metric("Fleet Active Machines", "4 / 4", delta="100% Operational")
            with f_m2:
                st.metric("Fleet Avg Health", "89.8%", delta="-1.2%")
            with f_m3:
                st.metric("Fleet Fuel Used", "342 Liters", delta="-14 L vs target")
            with f_m4:
                st.metric("Fleet Idle Ratio", "18.5%", delta="Target < 20%")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

            fleet_data = [
                {"machine": "CAT-SIM-EXC-001", "type": "Excavator", "operator": "Alex M.", "status": "🟢 NORMAL", "health": 94, "idle_pct": 14, "fuel_pct": 87},
                {"machine": "KOM-LOAD-500", "type": "Wheel Loader", "operator": "Sarah T.", "status": "🟡 WARNING", "health": 88, "idle_pct": 26, "fuel_pct": 62},
                {"machine": "VOL-HAUL-A40", "type": "Articulated Hauler", "operator": "David K.", "status": "🟢 NORMAL", "health": 98, "idle_pct": 8, "fuel_pct": 91},
                {"machine": "CAT-DOZ-D8", "type": "Dozer", "operator": "James R.", "status": "🔴 CRITICAL", "health": 79, "idle_pct": 31, "fuel_pct": 34},
            ]

            st.markdown("#### 🚜 Fleet Machine Status Grid")
            for m in fleet_data:
                with st.container(border=True):
                    fc1, fc2, fc3, fc4, fc5 = st.columns([1.5, 1.2, 1, 1, 1])
                    with fc1:
                        st.write(f"**{m['machine']}** ({m['type']})")
                        st.caption(f"Operator: {m['operator']}")
                    with fc2:
                        st.write(f"**Status:** {m['status']}")
                    with fc3:
                        st.write(f"**Health:** {m['health']}%")
                    with fc4:
                        st.write(f"**Idle Ratio:** {m['idle_pct']}%")
                    with fc5:
                        st.write(f"**Fuel:** {m['fuel_pct']}%")

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown("#### 📈 Fleet Idle Ratio Comparison")

            fleet_df = pd.DataFrame(fleet_data)
            st.bar_chart(fleet_df.set_index("machine")["idle_pct"])
            st.info("💡 **Takeaway**: Komatsu Loader 500 and Cat Dozer D8 exceed the target 20% idle ratio threshold today.")

    st.divider()
    st.caption("VisionLink Cab OS · Supervised Operator Assistance Prototype")


def render_digital_twin_view(current_record, current_state, previous_state, changes, trends, decisions, recommendations, highest_priority_recommendation, trend_result):
    # GLOBAL TWIN ALERT BAR — same warnings as the dashboard, pinned on scroll
    render_global_twin_alert_bar()

    # TELEMETRY VALUES
    # ============================================================
    
    machine_id = current_record[
        "machine_id"
    ]
    
    timestamp = current_record[
        "timestamp"
    ]
    
    scenario = current_record[
        "scenario"
    ]
    
    engine_temperature = float(
        current_record[
            "engine_temperature_c"
        ]
    )
    
    engine_rpm = float(
        current_record[
            "engine_rpm"
        ]
    )
    
    hydraulic_pressure = float(
        current_record[
            "hydraulic_pressure_bar"
        ]
    )
    
    fuel_consumption = float(
        current_record[
            "fuel_consumption_lph"
        ]
    )
    
    fuel_level = float(
        current_record[
            "fuel_level_percent"
        ]
    )
    
    load = float(
        current_record[
            "load_percentage"
        ]
    )
    
    idle_time = float(
        current_record[
            "idle_time_minutes"
        ]
    )
    
    speed = float(
        current_record[
            "machine_speed_kmh"
        ]
    )
    
    machine_health = float(
        current_record[
            "machine_health_score"
        ]
    )
    
    seatbelt_fastened = bool(
        current_record[
            "seatbelt_fastened"
        ]
    )
    
    operator_present = bool(
        current_record[
            "operator_present"
        ]
    )
    
    
    # ============================================================
    # VISUAL DIGITAL TWIN HELPERS
    # ============================================================
    
    def twin_status_class(status):
        """Convert a Digital Twin status into a CSS state class."""
        status = str(status).upper()
    
        if "CRITICAL" in status:
            return "critical"
        if any(word in status for word in ["WARNING", "HEAVY", "OVERHEATING", "LOW_", "HIGH_", "EXCESSIVE", "VIOLATION"]):
            return "warning"
        return "normal"
    
    
    def twin_status_label(status):
        """Create a short human-readable label for the visual twin."""
        status = str(status).upper()
    
        if "CRITICAL" in status:
            return "CRITICAL"
        if any(word in status for word in ["WARNING", "HEAVY", "OVERHEATING", "LOW_", "HIGH_", "EXCESSIVE", "VIOLATION"]):
            return "WARNING"
        if "NORMAL" in status or "SAFE" in status:
            return "NORMAL"
        return status.replace("_", " ")
    
    
    def clamp_percentage(value):
        return max(0, min(100, float(value)))
    
    
    def render_visual_digital_twin(
        state,
        health,
        temperature,
        hydraulic,
        fuel,
        load,
        recommendations
    ):
        """Render the excavator as a live visual representation of MachineState."""
    
        engine_status = twin_status_class(state.engine.status)
        hydraulic_status = twin_status_class(state.hydraulics.status)
        fuel_status = twin_status_class(state.fuel.status)
        operation_status = twin_status_class(state.operation.status)
        safety_status = twin_status_class(state.safety.status)
        overall_status = twin_status_class(state.overall_status)
    
        engine_label = twin_status_label(state.engine.status)
        hydraulic_label = twin_status_label(state.hydraulics.status)
        fuel_label = twin_status_label(state.fuel.status)
        operation_label = twin_status_label(state.operation.status)
        safety_label = twin_status_label(state.safety.status)
        overall_label = twin_status_label(state.overall_status)
    
        health_width = clamp_percentage(health)
        fuel_width = clamp_percentage(fuel)
        load_width = clamp_percentage(load)
    
        # The machine is rendered with HTML/CSS so Streamlit can reliably
        # display it. Each subsystem still receives its state class from the
        # actual Digital Twin MachineState.
    
        svg = f"""
        <div class="excavator-stage">
            <div class="excavator-ground"></div>
    
            <div class="excavator">
    
                <div class="exc-track left twin-component {operation_status}"></div>
                <div class="exc-track right twin-component {operation_status}"></div>
    
                <div class="exc-base twin-component {operation_status}"></div>
    
                <div class="exc-engine twin-component {engine_status}">
                    <div class="exc-engine-core"></div>
                </div>
    
                <div class="exc-cabin twin-component {safety_status}">
                    <div class="exc-window"></div>
                </div>
    
                <div class="exc-pivot twin-component {hydraulic_status}"></div>
    
                <div class="exc-boom twin-component {hydraulic_status}"></div>
                <div class="exc-arm twin-component {hydraulic_status}"></div>
                <div class="exc-cylinder twin-component {hydraulic_status}"></div>
                <div class="exc-bucket twin-component {operation_status}"></div>
    
                <div class="twin-alert-dot engine {engine_status}"
                     title="Engine: {engine_label}"></div>
                <div class="twin-alert-dot hydraulic {hydraulic_status}"
                     title="Hydraulics: {hydraulic_label}"></div>
                <div class="twin-alert-dot fuel {fuel_status}"
                     title="Fuel: {fuel_label}"></div>
                <div class="twin-alert-dot safety {safety_status}"
                     title="Safety: {safety_label}"></div>
    
                {
                    f'<div class="twin-callout engine {engine_status}"><strong>Engine</strong>{engine_label}<br>{temperature:.1f} °C</div>'
                    if engine_status != "normal" else ""
                }
    
                {
                    f'<div class="twin-callout hydraulic {hydraulic_status}"><strong>Hydraulics</strong>{hydraulic_label}<br>{hydraulic:.1f} bar</div>'
                    if hydraulic_status != "normal" else ""
                }
    
                {
                    f'<div class="twin-callout fuel {fuel_status}"><strong>Fuel</strong>{fuel_label}<br>{fuel:.1f}% remaining</div>'
                    if fuel_status != "normal" else ""
                }
    
                {
                    f'<div class="twin-callout safety {safety_status}"><strong>Safety</strong>{safety_label}</div>'
                    if safety_status != "normal" else ""
                }
    
                {
                    f'<div class="twin-callout operation {operation_status}"><strong>Operation</strong>{operation_label}<br>Load {load:.1f}%</div>'
                    if operation_status != "normal" else ""
                }
            </div>
        </div>
        """
    
        status_class = overall_status
        explanation = (
            "The virtual machine is mirroring the current Digital Twin state. "
            "Highlighted subsystems correspond to the engine, hydraulic, "
            "fuel/operation and safety states calculated from telemetry."
        )
    
        if overall_status == "critical":
            badge = "CRITICAL"
        elif overall_status == "warning":
            badge = "WARNING"
        else:
            badge = "NORMAL"
    
        # Use the already-computed Recommendation Engine output.
        # This keeps the visual twin aligned with the existing decision pipeline.
        primary_recommendation = None
        if recommendations:
            priority_order = {"CRITICAL": 3, "WARNING": 2, "NORMAL": 1, "UNKNOWN": 0}
            primary_recommendation = max(
                recommendations,
                key=lambda item: priority_order.get(item.get("priority", "UNKNOWN"), 0)
            )
    
        if primary_recommendation:
            interpretation_title = primary_recommendation.get(
                "title", "Machine condition detected"
            )
            interpretation_message = primary_recommendation.get(
                "message", "The Digital Twin detected a machine condition."
            )
            interpretation_action = primary_recommendation.get(
                "action", "Inspect the machine condition."
            )
        else:
            interpretation_title = "Machine operating normally"
            interpretation_message = "No active operator issue was detected."
            interpretation_action = "Continue operation while monitoring telemetry."
    
        state_cards = [
            ("Engine", engine_label, engine_status),
            ("Hydraulics", hydraulic_label, hydraulic_status),
            ("Fuel", fuel_label, fuel_status),
            ("Operation", operation_label, operation_status),
            ("Safety", safety_label, safety_status),
        ]
    
        cards_html = ""
        for name, label, css_class in state_cards:
            cards_html += f"""
            <div class="twin-state-card">
                <div class="twin-state-row">
                    <span class="twin-state-name">{name}</span>
                    <span class="twin-state-value {css_class}">{label}</span>
                </div>
            </div>
            """
    
        html = f"""
        <div class="twin-panel">
            <div class="twin-header">
                <div>
                    <div class="twin-title">🚜 Live Visual Digital Twin</div>
                    <div class="twin-subtitle">
                        A virtual representation of the excavator's current machine state
                    </div>
                </div>
                <div class="twin-live-badge {status_class}">
                    ● TWIN STATUS: {badge}
                </div>
            </div>
    
            <div class="twin-body">
                <div class="twin-machine">
                    {svg}
                </div>
    
                <div class="twin-side">
                    {cards_html}
    
                    <div class="twin-state-card">
                        <div class="twin-state-name">Machine Load</div>
                        <div class="twin-gauge">
                            <div class="twin-gauge-fill"
                                 style="width:{load_width:.1f}%"></div>
                        </div>
                        <div class="twin-state-row" style="margin-top:0.35rem">
                            <span class="twin-state-name">Current load</span>
                            <strong>{load:.1f}%</strong>
                        </div>
                    </div>
    
                    <div class="twin-state-card">
                        <div class="twin-state-name">Fuel Level</div>
                        <div class="twin-gauge">
                            <div class="twin-gauge-fill"
                                 style="width:{fuel_width:.1f}%"></div>
                        </div>
                        <div class="twin-state-row" style="margin-top:0.35rem">
                            <span class="twin-state-name">Available fuel</span>
                            <strong>{fuel:.1f}%</strong>
                        </div>
                    </div>
    
                    <div class="twin-interpretation">
                        <div class="twin-interpretation-title">
                            🧠 Twin Interpretation
                        </div>
                        <div class="twin-interpretation-main">
                            {interpretation_title}
                        </div>
                        <div class="twin-interpretation-detail">
                            {interpretation_message}
                        </div>
                        <div class="twin-action">
                            <strong>Operator action:</strong>
                            {interpretation_action}
                        </div>
                    </div>
    
                    <div class="twin-explanation">
                        <strong>How to read this:</strong><br>
                        {explanation}
                    </div>
                </div>
            </div>
        </div>
        """
    
        twin_view = st.radio(
            "Twin view",
            ["3D Interactive", "2D Schematic"],
            horizontal=True,
            key="twin_view_mode",
        )

        if twin_view == "3D Interactive":
            import streamlit.components.v1 as _components

            _boom_deg = 20 + (float(load) / 100.0) * 24
            _hyd_norm = max(0.0, min(1.0, (float(hydraulic) - 80.0) / 270.0))
            _stick_deg = 38 + _hyd_norm * 32
            _bucket_deg = 28 + (float(load) / 100.0) * 30
            _status_js = {
                "engine": engine_status, "hydraulic": hydraulic_status,
                "fuel": fuel_status, "operation": operation_status,
                "safety": safety_status, "overall": overall_status,
            }

            three_html = f"""
<div style="border-radius:22px;overflow:hidden;border:1px solid #e2e8f0;border-top:6px solid #f5a800;background:#0f172a;box-shadow:0 10px 30px rgba(15,23,42,0.12);">
<div style="display:flex;justify-content:space-between;align-items:center;padding:0.9rem 1.2rem;flex-wrap:wrap;gap:0.5rem;">
<div>
<div style="font-size:1.25rem;font-weight:900;color:white;">🚜 Live 3D Digital Twin</div>
<div style="color:#94a3b8;font-size:0.85rem;">Drag to orbit · Scroll to zoom · Right-drag to pan — live telemetry pose</div>
</div>
<div style="background:{'#dcfce7' if overall_status=='normal' else ('#fef3c7' if overall_status=='warning' else '#fee2e2')};color:{'#166534' if overall_status=='normal' else ('#92400e' if overall_status=='warning' else '#991b1b')};font-weight:800;padding:0.45rem 0.9rem;border-radius:999px;font-size:0.8rem;">● TWIN STATUS: {badge}</div>
</div>
<div id="twin3d-wrap" style="position:relative;">
<div id="twin3d-hud" style="position:absolute;top:10px;left:10px;display:flex;gap:0.4rem;flex-wrap:wrap;z-index:5;">
<span style="background:rgba(15,23,42,0.82);color:#fde68a;border:1px solid rgba(245,168,0,0.5);font-size:0.72rem;font-weight:800;padding:0.3rem 0.6rem;border-radius:999px;">🌡 {temperature:.1f}°C · {engine_label}</span>
<span style="background:rgba(15,23,42,0.82);color:#bae6fd;border:1px solid rgba(125,211,252,0.4);font-size:0.72rem;font-weight:800;padding:0.3rem 0.6rem;border-radius:999px;">💧 {hydraulic:.0f} bar · {hydraulic_label}</span>
<span style="background:rgba(15,23,42,0.82);color:#bbf7d0;border:1px solid rgba(134,239,172,0.4);font-size:0.72rem;font-weight:800;padding:0.3rem 0.6rem;border-radius:999px;">⛽ {fuel:.0f}% · 🏋️ {load:.0f}%</span>
</div>
<div id="twin3d-mount" style="width:100%;height:480px;"></div>
<div style="position:absolute;bottom:10px;right:12px;color:#64748b;font-size:0.72rem;font-weight:600;z-index:5;">three.js · procedural excavator · pose from live telemetry</div>
</div>
</div>
<script type="importmap">
{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}}}
</script>
<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
import {{ RoundedBoxGeometry }} from 'three/addons/geometries/RoundedBoxGeometry.js';

const STATUS = {{engine: "{_status_js['engine']}", hydraulic: "{_status_js['hydraulic']}", fuel: "{_status_js['fuel']}", operation: "{_status_js['operation']}", safety: "{_status_js['safety']}", overall: "{_status_js['overall']}"}};
const BOOM_DEG = {_boom_deg:.1f}, STICK_DEG = {_stick_deg:.1f}, BUCKET_DEG = {_bucket_deg:.1f};
const TEMP = {float(temperature):.1f}, HYD = {float(hydraulic):.1f}, FUEL = {float(fuel):.1f}, LOAD = {float(load):.1f};

const col = s => s === "critical" ? 0xef4444 : (s === "warning" ? 0xf59e0b : 0x22c55e);
const mount = document.getElementById("twin3d-mount");
const W = mount.clientWidth || 800, H = 480;

const renderer = new THREE.WebGLRenderer({{antialias: true}});
renderer.setSize(W, H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
mount.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0f172a);
scene.fog = new THREE.Fog(0x0f172a, 18, 40);

const camera = new THREE.PerspectiveCamera(45, W / H, 0.1, 100);
camera.position.set(7.6, 5.2, 8.4);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0.6, 1.6, 0);
controls.enableDamping = true;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.7;
controls.maxPolarAngle = Math.PI * 0.495;
controls.minDistance = 4; controls.maxDistance = 22;

scene.add(new THREE.HemisphereLight(0xfde68a, 0x0f172a, 0.85));
const sun = new THREE.DirectionalLight(0xfff7ed, 1.6);
sun.position.set(6, 10, 4);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
scene.add(sun);
const rim = new THREE.DirectionalLight(0x7dd3fc, 0.5);
rim.position.set(-6, 4, -6);
scene.add(rim);

const ground = new THREE.Mesh(
  new THREE.CircleGeometry(15, 64),
  new THREE.MeshStandardMaterial({{color: 0x1e293b, roughness: 1}})
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);
const grid = new THREE.GridHelper(28, 28, 0xf5a800, 0x334155);
grid.material.transparent = true; grid.material.opacity = 0.35;
grid.position.y = 0.01;
scene.add(grid);
const swingRing = new THREE.Mesh(
  new THREE.RingGeometry(2.6, 3.1, 48),
  new THREE.MeshBasicMaterial({{color: 0xdc2626, transparent: true, opacity: 0.5, side: THREE.DoubleSide}})
);
swingRing.rotation.x = -Math.PI / 2; swingRing.position.y = 0.02;
scene.add(swingRing);

const YELLOW = 0xf5a800, DARK = 0x1f2937, STEEL = 0x9ca3af;
const yellowMat = new THREE.MeshStandardMaterial({{color: YELLOW, roughness: 0.45, metalness: 0.25}});
const darkMat = new THREE.MeshStandardMaterial({{color: 0x111827, roughness: 0.8, metalness: 0.3}});
const steelMat = new THREE.MeshStandardMaterial({{color: STEEL, roughness: 0.35, metalness: 0.7}});
const glassMat = new THREE.MeshStandardMaterial({{color: 0x7dd3fc, roughness: 0.1, metalness: 0.4, transparent: true, opacity: 0.85}});
const engineMat = new THREE.MeshStandardMaterial({{color: 0xfbbf24, roughness: 0.5, metalness: 0.2, emissive: col(STATUS.engine), emissiveIntensity: STATUS.engine === "normal" ? 0.08 : 0.55}});
const hydMat = new THREE.MeshStandardMaterial({{color: YELLOW, roughness: 0.45, metalness: 0.25, emissive: col(STATUS.hydraulic), emissiveIntensity: STATUS.hydraulic === "normal" ? 0.05 : 0.5}});
const opMat = new THREE.MeshStandardMaterial({{color: YELLOW, roughness: 0.45, metalness: 0.25, emissive: col(STATUS.operation), emissiveIntensity: STATUS.operation === "normal" ? 0.05 : 0.5}});
const fuelMat = new THREE.MeshStandardMaterial({{color: 0xfbbf24, roughness: 0.5, metalness: 0.3, emissive: col(STATUS.fuel), emissiveIntensity: STATUS.fuel === "normal" ? 0.05 : 0.55}});
const whiteMat = new THREE.MeshStandardMaterial({{color: 0xf8fafc, roughness: 0.5, metalness: 0.1}});
const lampMat = new THREE.MeshStandardMaterial({{color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 2.2}});
const tailMat = new THREE.MeshStandardMaterial({{color: 0x7f1d1d, emissive: 0xef4444, emissiveIntensity: 1.4}});

function box(w, h, d, mat, x, y, z, parent) {{
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  (parent || scene).add(m);
  return m;
}}

function rbox(w, h, d, r, mat, x, y, z, parent) {{
  const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 3, r), mat);
  m.position.set(x, y, z);
  m.castShadow = true; m.receiveShadow = true;
  (parent || scene).add(m);
  return m;
}}

function makeLabel(text, hex) {{
  const c = document.createElement("canvas");
  c.width = 512; c.height = 128;
  const g = c.getContext("2d");
  const css = "#" + hex.toString(16).padStart(6, "0");
  const r = 28, w = 512, h = 128;
  g.beginPath();
  g.moveTo(r, 4); g.lineTo(w - r, 4); g.quadraticCurveTo(w - 4, 4, w - 4, r);
  g.lineTo(w - 4, h - r); g.quadraticCurveTo(w - 4, h - 4, w - r, h - 4);
  g.lineTo(r, h - 4); g.quadraticCurveTo(4, h - 4, 4, h - r);
  g.lineTo(4, r); g.quadraticCurveTo(4, 4, r, 4); g.closePath();
  g.fillStyle = "rgba(15,23,42,0.92)"; g.fill();
  g.lineWidth = 6; g.strokeStyle = css; g.stroke();
  g.fillStyle = css; g.beginPath(); g.arc(58, 64, 24, 0, Math.PI * 2); g.fill();
  g.fillStyle = "#ffffff"; g.font = "900 54px Arial";
  g.textAlign = "center"; g.textBaseline = "middle";
  g.fillText("!", 58, 68);
  g.textAlign = "left"; g.font = "800 42px Arial";
  g.fillText(text, 96, 66);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const sp = new THREE.Sprite(new THREE.SpriteMaterial({{map: tex, transparent: true, depthTest: false}}));
  sp.scale.set(2.5, 0.62, 1);
  sp.renderOrder = 20;
  return sp;
}}

const markers = [];
function addMarker(parent, x, y, z, text, colorHex) {{
  const grp = new THREE.Group();
  grp.position.set(x, y, z);
  parent.add(grp);
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.3, 0.44, 40),
    new THREE.MeshBasicMaterial({{color: colorHex, transparent: true, opacity: 0.9, side: THREE.DoubleSide}}));
  ring.rotation.x = -Math.PI / 2;
  grp.add(ring);
  const dot = new THREE.Mesh(new THREE.SphereGeometry(0.11, 16, 16),
    new THREE.MeshBasicMaterial({{color: colorHex}}));
  grp.add(dot);
  const label = makeLabel(text, colorHex);
  label.position.y = 0.85;
  grp.add(label);
  const pl = new THREE.PointLight(colorHex, 5, 6);
  grp.add(pl);
  markers.push({{grp: grp, ring: ring, pl: pl, baseY: y}});
  return grp;
}}

for (const s of [-0.85, 0.85]) {{
  box(3.6, 0.7, 0.7, STATUS.operation === "normal" ? darkMat : opMat, 0, 0.4, s);
  box(3.7, 0.12, 0.78, yellowMat, 0, 0.8, s);
  for (let i = -2; i <= 2; i++) {{
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.74, 20), steelMat);
    wheel.rotation.x = Math.PI / 2;
    wheel.position.set(i * 0.65, 0.38, s);
    wheel.castShadow = true;
    scene.add(wheel);
    const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.78, 12), darkMat);
    hub.rotation.x = Math.PI / 2;
    hub.position.set(i * 0.65, 0.38, s);
    scene.add(hub);
  }}
}}
box(3.0, 0.35, 1.9, yellowMat, 0, 0.92, 0);

const upper = new THREE.Group();
upper.position.y = 1.1;
scene.add(upper);
rbox(2.7, 0.5, 1.9, 0.1, yellowMat, -0.1, 0.25, 0, upper);
rbox(0.7, 0.85, 1.7, 0.18, yellowMat, -1.35, 0.55, 0, upper);
box(2.0, 0.09, 0.02, whiteMat, -0.1, 0.3, 0.96, upper);
box(2.0, 0.09, 0.02, whiteMat, -0.1, 0.3, -0.96, upper);
const hood = rbox(1.2, 0.7, 1.25, 0.1, engineMat, -0.55, 0.9, 0.15, upper);
box(1.0, 0.06, 1.0, darkMat, -0.55, 1.28, 0.15, upper);
const stack = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.75, 12), darkMat);
stack.position.set(-0.9, 1.62, 0.5); stack.castShadow = true;
upper.add(stack);
const stackCap = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.05, 12), darkMat);
stackCap.position.set(-0.9, 2.02, 0.5);
upper.add(stackCap);
const fuelTank = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 1.0, 20), fuelMat);
fuelTank.rotation.z = Math.PI / 2;
fuelTank.position.set(0.25, 0.85, 0.62);
fuelTank.castShadow = true; fuelTank.receiveShadow = true;
upper.add(fuelTank);
for (const sx of [-0.05, 0.55]) {{
  const strap = new THREE.Mesh(new THREE.TorusGeometry(0.35, 0.03, 8, 24), darkMat);
  strap.rotation.y = Math.PI / 2;
  strap.position.set(sx, 0.85, 0.62);
  upper.add(strap);
}}
const cabBody = rbox(1.0, 1.15, 0.95, 0.09, yellowMat, 0.62, 1.05, -0.42, upper);
box(0.7, 0.6, 0.06, glassMat, 0.62, 1.15, 0.08, upper);
box(0.06, 0.6, 0.7, glassMat, 1.13, 1.15, -0.42, upper);
box(0.72, 0.5, 0.06, glassMat, 0.62, 1.2, -0.9, upper);
rbox(1.1, 0.12, 1.05, 0.04, darkMat, 0.62, 1.68, -0.42, upper);
box(0.08, 0.14, 0.18, lampMat, 1.14, 1.52, -0.62, upper);
box(0.08, 0.14, 0.18, lampMat, 1.14, 1.52, -0.22, upper);
box(0.06, 0.16, 0.2, tailMat, -1.72, 0.6, 0.5, upper);
box(0.06, 0.16, 0.2, tailMat, -1.72, 0.6, -0.5, upper);
const beaconMat = new THREE.MeshStandardMaterial({{color: 0xef4444, emissive: 0xef4444, emissiveIntensity: 1}});
const beacon = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.12, 0.22, 16), beaconMat);
beacon.position.set(0.62, 1.85, -0.42);
upper.add(beacon);
const beaconLight = new THREE.PointLight(STATUS.overall === "normal" ? 0x22c55e : (STATUS.overall === "warning" ? 0xf59e0b : 0xef4444), 6, 8);
beaconLight.position.copy(beacon.position);
upper.add(beaconLight);

const boomGroup = new THREE.Group();
boomGroup.position.set(1.05, 0.75, 0.35);
boomGroup.rotation.z = THREE.MathUtils.degToRad(BOOM_DEG);
upper.add(boomGroup);
const boom = box(2.9, 0.38, 0.32, hydMat, 1.45, 0, 0, boomGroup);
boom.geometry.translate(0, 0, 0);
const cyl1 = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 1.6, 12), steelMat);
cyl1.position.set(0.7, -0.45, 0); cyl1.rotation.z = 0.9; cyl1.castShadow = true;
boomGroup.add(cyl1);

const stickGroup = new THREE.Group();
stickGroup.position.set(2.9, 0, 0);
stickGroup.rotation.z = THREE.MathUtils.degToRad(-STICK_DEG);
boomGroup.add(stickGroup);
box(2.3, 0.28, 0.24, hydMat, 1.15, 0, 0, stickGroup);
const cyl2 = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 1.4, 12), steelMat);
cyl2.position.set(0.6, 0.35, 0); cyl2.rotation.z = -0.7; cyl2.castShadow = true;
stickGroup.add(cyl2);

const bucketGroup = new THREE.Group();
bucketGroup.position.set(2.3, 0, 0);
bucketGroup.rotation.z = THREE.MathUtils.degToRad(STICK_DEG - BOOM_DEG + BUCKET_DEG - 60);
stickGroup.add(bucketGroup);
const bucket = rbox(0.75, 0.65, 0.9, 0.08, opMat, 0.3, -0.35, 0, bucketGroup);
bucket.rotation.z = -0.35;
for (let i = -1; i <= 1; i++) {{
  const tooth = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.3, 8), steelMat);
  tooth.position.set(0.55, -0.75, i * 0.28);
  tooth.rotation.z = Math.PI;
  tooth.castShadow = true;
  bucketGroup.add(tooth);
}}

const alertLight = new THREE.PointLight(col(STATUS.overall), 10, 12);
alertLight.position.set(1, 4, 1);
scene.add(alertLight);

if (STATUS.engine !== "normal") {{ addMarker(upper, -0.55, 1.75, 0.15, "ENGINE " + TEMP + " C", col(STATUS.engine)); }}
if (STATUS.hydraulic !== "normal") {{ addMarker(boomGroup, 1.6, 0.65, 0, "HYD " + HYD + " bar", col(STATUS.hydraulic)); }}
if (STATUS.operation !== "normal") {{ addMarker(bucketGroup, 0.3, 0.6, 0, "LOAD " + LOAD + " %", col(STATUS.operation)); }}
if (STATUS.fuel !== "normal") {{ addMarker(upper, 0.25, 1.55, 0.62, "FUEL " + FUEL + " %", col(STATUS.fuel)); }}
if (STATUS.safety !== "normal") {{ addMarker(upper, 0.62, 2.35, -0.42, "SAFETY ALERT", col(STATUS.safety)); }}

const clock = new THREE.Clock();
function animate() {{
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();
  upper.rotation.y = Math.sin(t * 0.35) * 0.28;
  const shake = STATUS.overall === "critical" ? Math.sin(t * 30) * 0.02 : 0;
  upper.position.y = 1.1 + shake;
  const pulse = (Math.sin(t * (STATUS.overall === "critical" ? 9 : 4)) + 1) / 2;
  if (STATUS.overall !== "normal") {{
    beaconMat.emissiveIntensity = 0.4 + pulse * 2.2;
    beaconLight.intensity = 2 + pulse * 8;
    alertLight.intensity = 3 + pulse * 9;
  }} else {{
    beaconMat.emissiveIntensity = 0.6;
    beaconLight.intensity = 2.5;
    alertLight.intensity = 2;
  }}
  for (const m of markers) {{
    const s = 1 + pulse * 0.4;
    m.ring.scale.set(s, s, 1);
    m.ring.material.opacity = 0.45 + pulse * 0.55;
    m.pl.intensity = 2 + pulse * 7;
    m.grp.position.y = m.baseY + Math.sin(t * 3 + m.baseY) * 0.07;
  }}
  controls.update();
  renderer.render(scene, camera);
}}
animate();

new ResizeObserver(() => {{
  const w = mount.clientWidth || 800;
  camera.aspect = w / H;
  camera.updateProjectionMatrix();
  renderer.setSize(w, H);
}}).observe(mount);
</script>
"""

            _components.html(three_html, height=620)

            st.html(
                f"""<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0.6rem;margin:0.8rem 0;">{cards_html}</div>
<div class="twin-state-card" style="margin-bottom:0.6rem;">
<div class="twin-state-name">Machine Load — {load:.1f}% · Fuel — {fuel:.1f}%</div>
<div class="twin-gauge"><div class="twin-gauge-fill" style="width:{load_width:.1f}%"></div></div>
<div class="twin-gauge" style="margin-top:0.4rem;"><div class="twin-gauge-fill" style="width:{fuel_width:.1f}%"></div></div>
</div>
<div class="twin-interpretation"><div class="twin-interpretation-title">🧠 Twin Interpretation</div>
<div class="twin-interpretation-main">{interpretation_title}</div>
<div class="twin-interpretation-detail">{interpretation_message}</div>
<div class="twin-action"><strong>Operator action:</strong> {interpretation_action}</div></div>"""
            )
        else:
            st.html(html)
    
    
    # ============================================================
    # HERO
    # ============================================================
    
    st.markdown(
        """
        <div class="hero">

        <h1>🚜 VisionLink Command Center</h1>

        <p>
        Live Digital Twin · Fleet Intelligence · In-Cab Operator Copilot — one workspace for safety, fuel and productivity.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )
    
    
    # ============================================================
    # MACHINE HEADER
    # ============================================================
    
    header_left, header_right = st.columns(
        [3, 1]
    )
    
    
    with header_left:
    
        st.subheader(
            f"Machine: {machine_id}"
        )
    
        st.caption(
            f"Telemetry: {timestamp}"
        )
    
        st.caption(
            f"Operating scenario: {scenario}"
        )
    
    
    with header_right:
    
        status = snapshot.overall_status
    
    
        if status == "CRITICAL":
    
            st.error(
                "🔴 MACHINE CRITICAL"
            )
    
        elif status == "WARNING":
    
            st.warning(
                "🟡 MACHINE WARNING"
            )
    
        else:
    
            st.success(
                "🟢 MACHINE NORMAL"
            )
    
    
    # ============================================================
    # VISUAL DIGITAL TWIN
    # ============================================================
    
    render_visual_digital_twin(
        current_state,
        machine_health,
        engine_temperature,
        hydraulic_pressure,
        fuel_level,
        load,
        recommendations
    )
    
    
    # ============================================================
    # LIVE MACHINE STATE
    # ============================================================
    
    st.markdown(
        "## 📊 Live Machine State"
    )
    
    
    metric1, metric2, metric3, metric4 = st.columns(
        4
    )
    
    
    with metric1:
    
        st.metric(
            "🌡️ Engine Temperature",
            f"{engine_temperature:.1f} °C"
        )
    
    
    with metric2:
    
        st.metric(
            "⚙️ Engine RPM",
            f"{engine_rpm:.0f}"
        )
    
    
    with metric3:
    
        st.metric(
            "💧 Hydraulic Pressure",
            f"{hydraulic_pressure:.1f} bar"
        )
    
    
    with metric4:
    
        st.metric(
            "⛽ Fuel Level",
            f"{fuel_level:.1f}%"
        )
    
    
    metric5, metric6, metric7, metric8 = st.columns(
        4
    )
    
    
    with metric5:
    
        st.metric(
            "🏋️ Load",
            f"{load:.1f}%"
        )
    
    
    with metric6:
    
        st.metric(
            "🚜 Speed",
            f"{speed:.1f} km/h"
        )
    
    
    with metric7:
    
        st.metric(
            "⏱️ Idle Time",
            f"{idle_time:.1f} min"
        )
    
    
    with metric8:
    
        st.metric(
            "❤️ Machine Health",
            f"{machine_health:.1f}/100"
        )
    
    
    # ============================================================
    # OPERATOR ASSISTANT
    # ============================================================
    
    st.markdown(
        "## 🤖 Digital Twin Operator Assistant"
    )
    
    
    if recommendations:
    
        for recommendation in recommendations:
    
            priority = recommendation[
                "priority"
            ]
    
            title = recommendation[
                "title"
            ]
    
            message = recommendation[
                "message"
            ]
    
            reason = recommendation[
                "reason"
            ]
    
            action = recommendation[
                "action"
            ]
    
    
            if priority == "CRITICAL":
    
                with st.container(
                    border=True
                ):
    
                    st.error(
                        f"🚨 {title}"
                    )
    
                    st.write(
                        message
                    )
    
                    st.markdown(
                        "**Why?**"
                    )
    
                    st.write(
                        reason
                    )
    
                    st.markdown(
                        "**Recommended Action**"
                    )
    
                    st.warning(
                        action
                    )
    
    
            elif priority == "WARNING":
    
                with st.container(
                    border=True
                ):
    
                    st.warning(
                        f"⚠️ {title}"
                    )
    
                    st.write(
                        message
                    )
    
                    st.markdown(
                        "**Why?**"
                    )
    
                    st.write(
                        reason
                    )
    
                    st.markdown(
                        "**Recommended Action**"
                    )
    
                    st.info(
                        action
                    )
    
    
            else:
    
                with st.container(
                    border=True
                ):
    
                    st.success(
                        f"✅ {title}"
                    )
    
                    st.write(
                        message
                    )
    
                    st.markdown(
                        "**Why?**"
                    )
    
                    st.write(
                        reason
                    )
    
                    st.markdown(
                        "**Recommended Action**"
                    )
    
                    st.info(
                        action
                    )
    
    
    # ============================================================
    # RECENT HISTORY
    # ============================================================
    
    chart_history = df.iloc[
        max(
            0,
            record_number - 99
        ):
        record_number + 1
    ].copy()
    
    
    # ============================================================
    # MACHINE TRENDS
    # ============================================================
    
    st.markdown(
        "## 📈 Machine Trends"
    )
    
    
    chart1, chart2 = st.columns(
        2
    )
    
    
    # ============================================================
    # ENGINE TEMPERATURE
    # ============================================================
    
    with chart1:
    
        st.markdown(
            "#### 🌡️ Engine Temperature"
        )
    
        fig, ax = plt.subplots(
            figsize=(7, 4)
        )
    
        ax.plot(
            chart_history["timestamp"],
            chart_history[
                "engine_temperature_c"
            ]
        )
    
        ax.axhline(
            100,
            linestyle="--",
            label="Warning"
        )
    
        ax.axhline(
            120,
            linestyle="--",
            label="Critical"
        )
    
        ax.set_ylabel(
            "Temperature (°C)"
        )
    
        ax.set_xlabel(
            "Time"
        )
    
        ax.legend()
    
        plt.xticks(
            rotation=30
        )
    
        plt.tight_layout()
    
        st.pyplot(
            fig,
            use_container_width=True
        )
    
        plt.close(fig)
    
    
    # ============================================================
    # MACHINE HEALTH
    # ============================================================
    
    with chart2:
    
        st.markdown(
            "#### ❤️ Machine Health"
        )
    
        fig, ax = plt.subplots(
            figsize=(7, 4)
        )
    
        ax.plot(
            chart_history["timestamp"],
            chart_history[
                "machine_health_score"
            ]
        )
    
        ax.axhline(
            80,
            linestyle="--",
            label="Warning"
        )
    
        ax.set_ylabel(
            "Health Score"
        )
    
        ax.set_xlabel(
            "Time"
        )
    
        ax.legend()
    
        plt.xticks(
            rotation=30
        )
    
        plt.tight_layout()
    
        st.pyplot(
            fig,
            use_container_width=True
        )
    
        plt.close(fig)
    
    
    # ============================================================
    # LOAD + HYDRAULICS
    # ============================================================
    
    chart3, chart4 = st.columns(
        2
    )
    
    
    with chart3:
    
        st.markdown(
            "#### 🏋️ Operating Load"
        )
    
        fig, ax = plt.subplots(
            figsize=(7, 4)
        )
    
        ax.plot(
            chart_history["timestamp"],
            chart_history[
                "load_percentage"
            ]
        )
    
        ax.axhline(
            80,
            linestyle="--",
            label="Heavy Load"
        )
    
        ax.axhline(
            95,
            linestyle="--",
            label="Critical Load"
        )
    
        ax.set_ylabel(
            "Load (%)"
        )
    
        ax.set_xlabel(
            "Time"
        )
    
        ax.legend()
    
        plt.xticks(
            rotation=30
        )
    
        plt.tight_layout()
    
        st.pyplot(
            fig,
            use_container_width=True
        )
    
        plt.close(fig)
    
    
    with chart4:
    
        st.markdown(
            "#### 💧 Hydraulic Pressure"
        )
    
        fig, ax = plt.subplots(
            figsize=(7, 4)
        )
    
        ax.plot(
            chart_history["timestamp"],
            chart_history[
                "hydraulic_pressure_bar"
            ]
        )
    
        ax.axhline(
            100,
            linestyle="--",
            label="Low Pressure"
        )
    
        ax.axhline(
            350,
            linestyle="--",
            label="High Pressure"
        )
    
        ax.set_ylabel(
            "Pressure (bar)"
        )
    
        ax.set_xlabel(
            "Time"
        )
    
        ax.legend()
    
        plt.xticks(
            rotation=30
        )
    
        plt.tight_layout()
    
        st.pyplot(
            fig,
            use_container_width=True
        )
    
        plt.close(fig)
    
    
    # ============================================================
    # AI TREND INTERPRETATION
    # ============================================================
    
    st.markdown(
        "## 🧠 Trend Analysis"
    )
    
    trend_columns = st.columns(
        6
    )
    
    
    trend_items = [
        (
            "Engine Temp",
            trends.get(
                "engine_temperature",
                "N/A"
            )
        ),
        (
            "RPM",
            trends.get(
                "engine_rpm",
                "N/A"
            )
        ),
        (
            "Hydraulic",
            trends.get(
                "hydraulic_pressure",
                "N/A"
            )
        ),
        (
            "Fuel",
            trends.get(
                "fuel_level",
                "N/A"
            )
        ),
        (
            "Load",
            trends.get(
                "load",
                "N/A"
            )
        ),
        (
            "Health",
            trends.get(
                "machine_health",
                "N/A"
            )
        )
    ]
    
    
    for column, (
        name,
        trend
    ) in zip(
        trend_columns,
        trend_items
    ):
    
        with column:
    
            if trend == "RISING":
    
                icon = "📈"
    
            elif trend == "FALLING":
    
                icon = "📉"
    
            elif trend == "STABLE":
    
                icon = "➡️"
    
            else:
    
                icon = "❓"
    
    
            st.metric(
                name,
                f"{icon} {trend}"
            )
    
    
    # ============================================================
    # OPERATING CONDITIONS
    # ============================================================
    
    st.markdown(
        "## ⚙️ Operating Conditions"
    )
    
    
    condition1, condition2, condition3, condition4 = st.columns(
        4
    )
    
    
    with condition1:
    
        st.metric(
            "Engine Status",
            str(
                current_state.engine.status
            )
        )
    
    
    with condition2:
    
        st.metric(
            "Hydraulic Status",
            str(
                current_state.hydraulics.status
            )
        )
    
    
    with condition3:
    
        st.metric(
            "Fuel Status",
            str(
                current_state.fuel.status
            )
        )
    
    
    with condition4:
    
        st.metric(
            "Operation Status",
            str(
                current_state.operation.status
            )
        )
    
    
    # ============================================================
    # SAFETY
    # ============================================================
    
    st.markdown(
        "## 🦺 Safety Status"
    )
    
    
    safety1, safety2 = st.columns(
        2
    )
    
    
    with safety1:
    
        if operator_present:
    
            st.success(
                "👷 Operator detected"
            )
    
        else:
    
            st.warning(
                "⚠️ No operator detected"
            )
    
    
    with safety2:
    
        if seatbelt_fastened:
    
            st.success(
                "✅ Seatbelt fastened"
            )
    
        else:
    
            st.error(
                "🚨 Seatbelt violation"
            )
    
    
    # ============================================================
    # EVENT / ANOMALY INFORMATION
    # ============================================================
    
    st.markdown(
        "## 🚨 Current Event Status"
    )
    
    
    event1, event2, event3 = st.columns(
        3
    )
    
    
    with event1:
    
        anomaly = bool(
            current_record[
                "anomaly_label"
            ]
        )
    
        if anomaly:
    
            st.error(
                "🚨 Anomaly Detected"
            )
    
        else:
    
            st.success(
                "✅ No Anomaly Detected"
            )
    
    
    with event2:
    
        if bool(
            current_record["refueled"]
        ):
    
            st.info(
                "⛽ Refueling Event"
            )
    
        else:
    
            st.write(
                "No refueling event"
            )
    
    
    with event3:
    
        st.metric(
            "Fuel Consumption",
            f"{fuel_consumption:.2f} L/h"
        )
    # ============================================================
    # MACHINE EVENT TIMELINE
    # ============================================================
    
    st.markdown(
        "## 🚨 Machine Event Timeline"
    )
    
    st.caption(
        "Recent machine events detected from the Digital Twin telemetry."
    )
    
    
    # ------------------------------------------------------------
    # Build events from recent telemetry
    # ------------------------------------------------------------
    
    timeline_history = df.iloc[
        max(
            0,
            record_number - 99
        ):
        record_number + 1
    ].copy()
    
    
    events = []
    
    
    for _, row in timeline_history.iterrows():
    
        event_time = row["timestamp"]
    
        event_scenario = row["scenario"]
    
        temp = float(
            row["engine_temperature_c"]
        )
    
        hydraulic = float(
            row["hydraulic_pressure_bar"]
        )
    
        fuel = float(
            row["fuel_level_percent"]
        )
    
        load_value = float(
            row["load_percentage"]
        )
    
        idle = float(
            row["idle_time_minutes"]
        )
    
        speed_value = float(
            row["machine_speed_kmh"]
        )
    
        health = float(
            row["machine_health_score"]
        )
    
        seatbelt = bool(
            row["seatbelt_fastened"]
        )
    
        operator = bool(
            row["operator_present"]
        )
    
    
        # --------------------------------------------------------
        # CRITICAL EVENTS
        # --------------------------------------------------------
    
        if temp >= 120:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "CRITICAL",
                    "icon": "🔴",
                    "title": "Engine Overheating",
                    "reason":
                        f"Engine temperature reached "
                        f"{temp:.1f} °C.",
                    "action":
                        "Stop heavy operation and allow "
                        "the engine to cool."
                }
            )
    
    
        elif hydraulic > 350:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "CRITICAL",
                    "icon": "🔴",
                    "title": "High Hydraulic Pressure",
                    "reason":
                        f"Hydraulic pressure reached "
                        f"{hydraulic:.1f} bar.",
                    "action":
                        "Reduce hydraulic load and inspect "
                        "the hydraulic system."
                }
            )
    
    
        elif hydraulic < 100:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "CRITICAL",
                    "icon": "🔴",
                    "title": "Low Hydraulic Pressure",
                    "reason":
                        f"Hydraulic pressure dropped to "
                        f"{hydraulic:.1f} bar.",
                    "action":
                        "Inspect the hydraulic system "
                        "before continuing heavy operation."
                }
            )
    
    
        elif operator and not seatbelt:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "CRITICAL",
                    "icon": "🔴",
                    "title": "Seatbelt Safety Violation",
                    "reason":
                        "Operator detected without "
                        "seatbelt fastened.",
                    "action":
                        "Fasten the seatbelt before "
                        "continuing operation."
                }
            )
    
    
        # --------------------------------------------------------
        # WARNING EVENTS
        # --------------------------------------------------------
    
        elif temp >= 100:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "WARNING",
                    "icon": "🟡",
                    "title": "Engine Temperature Warning",
                    "reason":
                        f"Engine temperature reached "
                        f"{temp:.1f} °C.",
                    "action":
                        "Reduce load and monitor "
                        "engine temperature."
                }
            )
    
    
        elif load_value >= 95:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "WARNING",
                    "icon": "🟡",
                    "title": "Critical Operating Load",
                    "reason":
                        f"Machine load reached "
                        f"{load_value:.1f}%.",
                    "action":
                        "Reduce the operating load "
                        "to prevent machine stress."
                }
            )
    
    
        elif load_value >= 80:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "WARNING",
                    "icon": "🟡",
                    "title": "Heavy Load",
                    "reason":
                        f"Machine load reached "
                        f"{load_value:.1f}%.",
                    "action":
                        "Monitor machine load and "
                        "avoid prolonged heavy operation."
                }
            )
    
    
        elif idle >= 15 and speed_value == 0:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "WARNING",
                    "icon": "🟡",
                    "title": "Excessive Idling",
                    "reason":
                        f"Machine has been idle for "
                        f"{idle:.1f} minutes.",
                    "action":
                        "Reduce unnecessary idling "
                        "to improve fuel efficiency."
                }
            )
    
    
        elif fuel <= 10:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "WARNING",
                    "icon": "🟡",
                    "title": "Critically Low Fuel",
                    "reason":
                        f"Fuel level dropped to "
                        f"{fuel:.1f}%.",
                    "action":
                        "Refuel the machine soon."
                }
            )
    
    
        elif fuel <= 20:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "WARNING",
                    "icon": "🟡",
                    "title": "Low Fuel",
                    "reason":
                        f"Fuel level is "
                        f"{fuel:.1f}%.",
                    "action":
                        "Plan a refueling stop."
                }
            )
    
    
        elif health < 80:
    
            events.append(
                {
                    "timestamp": event_time,
                    "severity": "WARNING",
                    "icon": "🟡",
                    "title": "Machine Health Declining",
                    "reason":
                        f"Machine health score is "
                        f"{health:.1f}/100.",
                    "action":
                        "Inspect the machine and "
                        "monitor health indicators."
                }
            )
    
    
    # ------------------------------------------------------------
    # Remove consecutive duplicate events
    # ------------------------------------------------------------
    
    filtered_events = []
    
    previous_event_key = None
    
    
    for event in events:
    
        event_key = (
            event["title"]
        )
    
        if event_key != previous_event_key:
    
            filtered_events.append(
                event
            )
    
            previous_event_key = event_key
    
    
    # ------------------------------------------------------------
    # Display timeline
    # ------------------------------------------------------------
    
    if filtered_events:
    
        # Show newest events first
    
        display_events = filtered_events[
            ::-1
        ][:10]
    
    
        for event in display_events:
    
            severity = event[
                "severity"
            ]
    
    
            if severity == "CRITICAL":
    
                with st.container(
                    border=True
                ):
    
                    st.error(
                        f'{event["icon"]} '
                        f'{event["title"]}'
                    )
    
                    st.caption(
                        event["timestamp"]
                    )
    
                    st.write(
                        f'**Why:** '
                        f'{event["reason"]}'
                    )
    
                    st.write(
                        f'**Action:** '
                        f'{event["action"]}'
                    )
    
    
            else:
    
                with st.container(
                    border=True
                ):
    
                    st.warning(
                        f'{event["icon"]} '
                        f'{event["title"]}'
                    )
    
                    st.caption(
                        event["timestamp"]
                    )
    
                    st.write(
                        f'**Why:** '
                        f'{event["reason"]}'
                    )
    
                    st.write(
                        f'**Action:** '
                        f'{event["action"]}'
                    )
    
    
    else:
    
        st.success(
            "🟢 No machine events detected "
            "in the current telemetry window."
        )
    
    
    # ------------------------------------------------------------
    # Event summary
    # ------------------------------------------------------------
    
    critical_events = sum(
        1
        for event in filtered_events
        if event["severity"] == "CRITICAL"
    )
    
    warning_events = sum(
        1
        for event in filtered_events
        if event["severity"] == "WARNING"
    )
    
    
    summary1, summary2, summary3 = st.columns(
        3
    )
    
    
    with summary1:
    
        st.metric(
            "Total Events",
            len(filtered_events)
        )
    
    
    with summary2:
    
        st.metric(
            "Critical Events",
            critical_events
        )
    
    
    with summary3:
    
        st.metric(
            "Warning Events",
            warning_events
        )
    
    # ============================================================
    # DIGITAL TWIN DETAILS
    # ============================================================
    
    st.markdown(
        "## 🔍 Digital Twin Details"
    )
    
    
    with st.expander(
        "View Digital Twin State"
    ):
    
        st.json(
            current_state.to_dict()
        )
    
    
    with st.expander(
        "View AI Decisions"
    ):
    
        st.json(
            decisions
        )
    
    
    with st.expander(
        "View Operator Recommendations"
    ):
    
        st.json(
            recommendations
        )
    
    
    with st.expander(
        "View State Changes"
    ):
    
        st.json(
            changes
        )
    
    
    # ============================================================
    # FOOTER
    # ============================================================
    
    st.divider()
    
    st.caption(
        "VisionLink Digital Twin for Construction Equipment "
        "| Supervised Operator Assistance Prototype"
    )
    
    
    # ============================================================

# ============================================================
# VIEW ROUTING
# ============================================================

if st.session_state.view_mode == "🌐 Digital Twin Monitor":
    render_digital_twin_view(
        current_record,
        current_state,
        previous_state,
        changes,
        trends,
        decisions,
        recommendations,
        highest_priority_recommendation,
        trend_result
    )
else:
    render_operator_assistant_view(
        current_record,
        current_state,
        highest_priority_recommendation,
        decisions
    )


# AUTO PLAY
# ============================================================

if st.session_state.playing:

    if st.session_state.record_number < len(df) - 1:

        time.sleep(
            speed_settings[
                simulation_speed
            ]
        )

        st.session_state.record_number += 1

        st.rerun()

    else:

        st.session_state.playing = False

        st.success(
            "🏁 Simulation completed."
        )