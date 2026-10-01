import streamlit as st

st.set_page_config(layout="wide")

st.markdown("""
<style>
/* Cab Menu Tablet Block Button System */
div.cab-nav-item {
    margin-bottom: 0.75rem !important;
}

/* Default / Inactive Button Block */
div.cab-nav-inactive div[data-testid="stButton"] button,
div.cab-nav-inactive button {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 2px solid #cbd5e1 !important;
    border-left: 6px solid #cbd5e1 !important;
    border-radius: 14px !important;
    height: 66px !important;
    min-height: 66px !important;
    padding: 14px 18px !important;
    font-size: 1.15rem !important; /* ~18-19px */
    font-weight: 700 !important;
    text-align: left !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04) !important;
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
    transform: translateX(3px) !important;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15) !important;
}

/* Active / Selected State (Current Page) */
div.cab-nav-active div[data-testid="stButton"] button,
div.cab-nav-active button {
    background-color: #fffbeb !important; /* Distinct warm yellow/gold tint */
    color: #0f172a !important;
    border: 3px solid #f59e0b !important; /* Caterpillar Yellow Accent Border */
    border-left: 12px solid #f59e0b !important; /* Bold 12px Accent Bar */
    border-radius: 14px !important;
    height: 66px !important;
    min-height: 66px !important;
    padding: 14px 18px !important;
    font-size: 1.2rem !important; /* ~19-20px */
    font-weight: 800 !important;
    text-align: left !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
    box-shadow: 0 6px 18px rgba(245, 158, 11, 0.25) !important;
    transition: background-color 0.15s ease !important;
    cursor: pointer !important;
}
</style>
""", unsafe_allow_html=True)

nav_options = [
    "📋 Shift Tasks",
    "🦺 Safety & Hazard Radar",
    "🌱 Fuel & Pattern Alerts",
    "🎓 Training & Pre-Op Hub",
    "💬 Cab Copilot",
    "🤖 Shift Summary",
    "📊 Fleet Overview"
]

if "test_nav" not in st.session_state:
    st.session_state.test_nav = "📋 Shift Tasks"

c1, c2 = st.columns([1.45, 3.55])

with c1:
    st.markdown("### 🚜 IN-CAB TABLET MENU")
    for opt in nav_options:
        is_active = (st.session_state.test_nav == opt)
        css_class = "cab-nav-item cab-nav-active" if is_active else "cab-nav-item cab-nav-inactive"
        circle_icon = "🟡" if is_active else "○"
        btn_text = f"{opt}   {circle_icon}"

        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button(btn_text, key=f"exact_btn_{opt}", use_container_width=True):
            st.session_state.test_nav = opt
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.title(f"Active Page: {st.session_state.test_nav}")
