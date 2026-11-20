"""
PulsePoint Cyber-Medical Intelligence System
Futuristic Glassmorphic KPI Card Component
"""

import streamlit as st

def render_kpi_card(title: str, value: str, subtext: str = "", status: str = "normal"):
    """
    Renders a responsive, glowing cyber-medical KPI card.
    status options: 'normal', 'critical', 'high', 'info'
    """
    color_map = {
        "normal": "#00f5a0",
        "critical": "#ff3366",
        "high": "#ffaa00",
        "info": "#00f2fe"
    }
    accent = color_map.get(status, "#00f2fe")

    html = f"""
    <div class="kpi-container" style="border-left: 4px solid {accent}; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-subtext" style="color: {accent};">{subtext}</div>' if subtext else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
