"""
PulsePoint Cyber-Medical OS v6.0
Standalone Cyber-Medical Control Center, 2FA + JWT Security Gateway & AI Health Chatbot
"""

import importlib
import streamlit as st
import pandas as pd
from pathlib import Path
from streamlit_option_menu import option_menu

from data_pipeline.exporter import load_dataset
from core.rasp_shield import (
    BackendIsolationGuard,
    BuildObfuscationEngine,
    AntiTamperRaspEngine,
    AntiLLMTrapEngine,
)
from ui.theme import CYBER_MEDICAL_CSS
import ui.components.navbar as _navbar_mod
if not hasattr(_navbar_mod, "render_2fa_login_screen"):
    importlib.reload(_navbar_mod)
from ui.components.navbar import render_navbar, render_2fa_login_screen
from ui.components.filters import render_global_filters
from ui.components.anatomical_viewer import render_anatomical_organ_viewer

# Import dedicated view modules (each renders on its own fast, isolated page)
import ui.views.dashboard_a_executive as p_exec
import ui.views.ai_doctor_assistant as p_ai_doc
import ui.views.dashboard_b_clinical as p_clin
import ui.views.dashboard_c_lifestyle as p_life
import ui.views.dashboard_d_population as p_pop
import ui.views.ml_risk_predictor as p_ml
import ui.views.patient_360 as p_pt360
import ui.views.alert_center as p_alerts
import ui.views.reports_exports as p_reports
import ui.views.tableau_studio as p_tableau
import ui.views.privacy_policy as p_privacy

# Page Configuration (Zero framework branding)
st.set_page_config(
    page_title="PulsePoint Cyber-Medical OS v6.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Cyber-Medical Stylesheet
st.markdown(CYBER_MEDICAL_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=600, max_entries=16)
def get_cached_dataset() -> pd.DataFrame:
    """Load and cache processed chronic disease cohort in shared server memory."""
    return load_dataset()


def _navigate_to(page_name: str):
    """Switch active Control Center page immediately."""
    st.session_state["selected_control_page"] = page_name
    st.session_state["nav_sync_version"] = st.session_state.get("nav_sync_version", 0) + 1
    st.rerun()


def main():
    # 0. Initialize RASP Anti-Tamper Baseline, Client Build Obfuscation Shield & Anti-LLM DOM Honeypot
    AntiTamperRaspEngine.initialize_baseline()
    st.markdown(
        BuildObfuscationEngine.get_client_obfuscation_shield_html()
        + AntiLLMTrapEngine.get_anti_llm_dom_honeypot_html(),
        unsafe_allow_html=True
    )

    # 1. Render Top Cyber-Medical Navigation Bar (Top-Right Login / Register / Forgot Password)
    render_navbar()

    # 2. If User Clicked Full-Screen Login Page, Render 3-Tab Login / Register / Forgot Password Gate
    if st.session_state.get("show_login_gate", False):
        render_2fa_login_screen()
        return

    # 3. Load Dataset (Uses User's Private Isolated Tenant Namespace Dataset if Active)
    user_info = st.session_state.get("user", {"username": "guest", "full_name": "Guest Visitor", "role": "Guest"})
    username = user_info.get("username", "guest")
    tenant_ns = BackendIsolationGuard.isolate_tenant_namespace(username)
    try:
        if f"custom_uploaded_df_{tenant_ns}" in st.session_state:
            raw_cohort_df = st.session_state[f"custom_uploaded_df_{tenant_ns}"]
        elif f"custom_uploaded_df_{username}" in st.session_state:
            raw_cohort_df = st.session_state[f"custom_uploaded_df_{username}"]
        else:
            raw_cohort_df = get_cached_dataset()
    except Exception as e:
        st.error(f"Isolated Backend Storage Error: {BackendIsolationGuard.sanitize_outbound_error(str(e))}")
        return

    menu_options = [
        "Main Executive Dashboard",
        "AI Doctor & Medicine Guide",
        "Scenario 1: Clinical Risk",
        "Scenario 2: Lifestyle & Habits",
        "Scenario 3: Population Insights",
        "3D Anatomical Digital Twin",
        "AI/ML Risk Simulator",
        "Patient 360 EHR Profile",
        "Clinical Alert Center",
        "Tableau Storyboard Studio",
        "Reports & Data Exports",
        "Security, Access & Privacy"
    ]

    if "selected_control_page" not in st.session_state or st.session_state["selected_control_page"] not in menu_options:
        st.session_state["selected_control_page"] = "Main Executive Dashboard"

    current_default_idx = menu_options.index(st.session_state["selected_control_page"])
    nav_key = f"pulsepoint_ctrl_menu_{st.session_state.get('nav_sync_version', 0)}"

    # 4. Left Sidebar: CONTROL CENTER
    with st.sidebar:
        st.markdown(
            '<div style="padding: 8px 0 12px 0; text-align: center; border-bottom: 1px solid rgba(0,242,254,0.2); margin-bottom: 10px;">'
            '<div style="font-size: 1.18rem; font-weight: 900; color: #00f2fe; letter-spacing: 0.06em;">🎛️ CONTROL CENTER</div>'
            '<div style="font-size: 0.70rem; color: #94a3b8; letter-spacing: 0.06em; margin-top: 2px;">CYBER-MEDICAL INTELLIGENCE OS v6.0</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # Quick AI Health Chatbot Button in Sidebar
        if st.button("🤖 Open AI Health Chatbot", use_container_width=True, key="sidebar_quick_ai_btn"):
            _navigate_to("AI Doctor & Medicine Guide")

        selected_page = option_menu(
            menu_title=None,
            options=menu_options,
            icons=[
                "speedometer2",
                "robot",
                "heart-pulse",
                "activity",
                "people",
                "diagram-3",
                "cpu",
                "person-vcard",
                "bell",
                "bar-chart-line",
                "cloud-arrow-up",
                "shield-lock"
            ],
            menu_icon="cast",
            default_index=current_default_idx,
            key=nav_key,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#00f2fe", "font-size": "14px"},
                "nav-link": {
                    "font-size": "12.5px",
                    "text-align": "left",
                    "margin": "3px 0",
                    "color": "#cbd5e1",
                    "border-radius": "8px",
                    "padding": "8px 12px",
                    "transition": "all 0.2s ease"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(90deg, rgba(0, 242, 254, 0.24) 0%, rgba(79, 172, 254, 0.12) 100%)",
                    "color": "#00f2fe",
                    "border-left": "3px solid #00f2fe",
                    "font-weight": "700"
                }
            }
        )

        # Sync manual sidebar clicks back to session state
        if selected_page != st.session_state["selected_control_page"]:
            st.session_state["selected_control_page"] = selected_page
            st.rerun()

        st.markdown("<hr style='border-color: rgba(0, 242, 254, 0.18); margin: 12px 0 10px 0;'/>", unsafe_allow_html=True)

        # Full Login / Register / Forgot Password Button in Sidebar
        if st.button("🔐 Login / Register / Forgot Password", use_container_width=True, key="sidebar_2fa_btn"):
            st.session_state.show_login_gate = True
            st.rerun()

        if st.button("📄 Download PDF & CSV Reports", use_container_width=True, key="sidebar_pdf_nav_btn"):
            _navigate_to("Reports & Data Exports")

        is_auth = st.session_state.get("authenticated", False)
        status_label = f"🟢 {user_info['full_name']}" if is_auth else "🔓 Guest (Not Logged In)"
        st.markdown(
            f'<div style="margin-top: 8px; padding: 10px 12px; border-radius: 10px; background: rgba(0,242,254,0.06); '
            f'border: 1px solid rgba(0,242,254,0.2); font-size: 0.72rem; color: #94a3b8; line-height: 1.45;">'
            f'<b style="color:#00f2fe;">👤 Session Status:</b><br/>'
            f'<span style="color:#ffffff; font-weight:700;">{status_label}</span><br/>'
            f'<span>{user_info.get("role", "Guest")} • {tenant_ns}</span><br/>'
            f'<span style="color:#00f5a0;">🛡️ RASP + OBF6 + Anti-LLM Trap</span></div>',
            unsafe_allow_html=True
        )

    # 5. Interactive Quick-Jump Scenario & AI Chatbot Cards
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(
            '<div class="scenario-banner-card" style="margin-bottom: 6px;">'
            '<div style="font-size:0.68rem; color:#00f2fe; font-weight:800;">SCENARIO 1 • CLINICAL RISK</div>'
            '<div style="font-size:0.92rem; font-weight:800; color:#fff; margin:2px 0;">🩺 Clinical Biomarker Triage</div>'
            '<div style="font-size:0.74rem; color:#94a3b8;">BP, Glucose, Cholesterol &amp; BMI risk triage.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("🩺 Open Scenario 1 Page →", key="jump_sc1", use_container_width=True):
            _navigate_to("Scenario 1: Clinical Risk")

    with sc2:
        st.markdown(
            '<div class="scenario-banner-card" style="margin-bottom: 6px;">'
            '<div style="font-size:0.68rem; color:#00f5a0; font-weight:800;">SCENARIO 2 • LIFESTYLE HABITS</div>'
            '<div style="font-size:0.92rem; font-weight:800; color:#fff; margin:2px 0;">📈 Behavioral Risk Multipliers</div>'
            '<div style="font-size:0.74rem; color:#94a3b8;">Smoking, Alcohol &amp; Exercise habits impact.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("📈 Open Scenario 2 Page →", key="jump_sc2", use_container_width=True):
            _navigate_to("Scenario 2: Lifestyle & Habits")

    with sc3:
        st.markdown(
            '<div class="scenario-banner-card" style="margin-bottom: 6px;">'
            '<div style="font-size:0.68rem; color:#a855f7; font-weight:800;">SCENARIO 3 • POPULATION MATRIX</div>'
            '<div style="font-size:0.92rem; font-weight:800; color:#fff; margin:2px 0;">🌍 Demographic Stratification</div>'
            '<div style="font-size:0.74rem; color:#94a3b8;">Age × BMI heatmap &amp; regional prevalence.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("🌍 Open Scenario 3 Page →", key="jump_sc3", use_container_width=True):
            _navigate_to("Scenario 3: Population Insights")

    with sc4:
        st.markdown(
            '<div class="scenario-banner-card" style="margin-bottom: 6px; border-color: rgba(0, 245, 160, 0.45);">'
            '<div style="font-size:0.68rem; color:#00f5a0; font-weight:800;">CHATBOT • HEALTH AI &amp; SAHI ILAZ</div>'
            '<div style="font-size:0.92rem; font-weight:800; color:#fff; margin:2px 0;">🤖 AI Doctor Chatbot</div>'
            '<div style="font-size:0.74rem; color:#94a3b8;">Chat in Hindi/English for medicines &amp; care.</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("🤖 Open AI Chatbot →", key="jump_ai_doc", use_container_width=True):
            _navigate_to("AI Doctor & Medicine Guide")

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # 6. Render Global Cohort Filters (for data-driven pages)
    pages_without_cohort_filter = {
        "AI Doctor & Medicine Guide",
        "AI/ML Risk Simulator",
        "Clinical Alert Center",
        "Tableau Storyboard Studio",
        "Security, Access & Privacy"
    }

    if selected_page not in pages_without_cohort_filter:
        filtered_df, active_filters = render_global_filters(raw_cohort_df)
    else:
        filtered_df, active_filters = raw_cohort_df, {}

    # 7. Route to the Single Selected Dedicated Page
    if selected_page == "Main Executive Dashboard":
        p_exec.render(filtered_df, active_filters)
    elif selected_page == "AI Doctor & Medicine Guide":
        p_ai_doc.render(filtered_df)
    elif selected_page == "Scenario 1: Clinical Risk":
        p_clin.render(filtered_df, active_filters)
    elif selected_page == "Scenario 2: Lifestyle & Habits":
        p_life.render(filtered_df, active_filters)
    elif selected_page == "Scenario 3: Population Insights":
        p_pop.render(filtered_df, active_filters)
    elif selected_page == "3D Anatomical Digital Twin":
        render_anatomical_organ_viewer(filtered_df)
    elif selected_page == "AI/ML Risk Simulator":
        p_ml.render()
    elif selected_page == "Patient 360 EHR Profile":
        p_pt360.render(filtered_df)
    elif selected_page == "Clinical Alert Center":
        p_alerts.render()
    elif selected_page == "Tableau Storyboard Studio":
        p_tableau.render()
    elif selected_page == "Reports & Data Exports":
        p_reports.render(filtered_df, active_filters)
    elif selected_page == "Security, Access & Privacy":
        p_privacy.render(filtered_df)


if __name__ == "__main__":
    main()
