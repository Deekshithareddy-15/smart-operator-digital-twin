import streamlit as st

st.set_page_config(layout="wide")

st.markdown("""
<style>
/* Cat In-Cab Tablet UI Navigation System */
div.cab-tablet-active button {
    background: #fffbeb !important; /* Warm gold tint background */
    color: #0f172a !important;
    border: 3px solid #f59e0b !important; /* Caterpillar Yellow/Gold border */
    border-left: 12px solid #f59e0b !important; /* Heavy Gold Accent Bar */
    box-shadow: 0 6px 20px rgba(245, 158, 11, 0.25) !important;
    height: 74px !important;
    min-height: 74px !important;
    font-size: 1.2rem !important; /* ~19-20px BIG Text */
    font-weight: 800 !important;
    border-radius: 18px !important;
    text-align: left !important;
    justify-content: space-between !important;
    padding: 0 1.4rem !important;
    margin-bottom: 0.85rem !important;
    cursor: pointer !important;
}

div.cab-tablet-inactive button {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 2px solid #cbd5e1 !important;
    border-left: 6px solid #cbd5e1 !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    height: 74px !important;
    min-height: 74px !important;
    font-size: 1.15rem !important; /* ~18-19px BIG Text */
    font-weight: 700 !important;
    border-radius: 18px !important;
    text-align: left !important;
    justify-content: space-between !important;
    padding: 0 1.4rem !important;
    margin-bottom: 0.85rem !important;
    transition: all 0.15s ease-in-out !important;
    cursor: pointer !important;
}

div.cab-tablet-inactive button:hover {
    background-color: #f8fafc !important;
    border-color: #f59e0b !important;
    border-left-color: #f59e0b !important;
    color: #b45309 !important;
    transform: translateX(4px) !important;
}
</style>
""", unsafe_allow_html=True)

nav_items = [
    ("📋 Shift Tasks", "Shift Tasks"),
    ("🦺 Safety & Hazard Radar", "Safety & Hazard Radar"),
    ("🌱 Fuel & Pattern Alerts", "Fuel & Pattern Alerts"),
    ("🎓 Training & Pre-Op Hub", "Training & Pre-Op Hub"),
    ("💬 Cab Copilot", "Cab Copilot"),
    ("🤖 Shift Summary", "Shift Summary"),
    ("📊 Fleet Overview", "Fleet Overview")
]

if "test_nav" not in st.session_state:
    st.session_state.test_nav = "📋 Shift Tasks"

c1, c2 = st.columns([1.45, 3.55])

with c1:
    st.markdown("### 🚜 BACKHOE & EXCAVATOR CAB MENU")
    for raw_label, key_name in nav_items:
        is_active = (st.session_state.test_nav == raw_label)
        css_class = "cab-tablet-active" if is_active else "cab-tablet-inactive"
        circle_icon = "🟡" if is_active else "○"
        btn_display = f"{raw_label}   {circle_icon}"
        
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button(btn_display, key=f"tbl_btn_{key_name}", use_container_width=True):
            st.session_state.test_nav = raw_label
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.title(f"Selected Section: {st.session_state.test_nav}")
