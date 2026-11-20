"""
Tableau Interactive Studio & Visual Storyboard
5-Slide Interactive Tableau Storyboard, Live Tableau Public Embed & 1-Click .TWB/.TWBX Downloads
Zero raw code blocks — 100% visual interactive dashboards and cards.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.config import TABLEAU_DIR, PROCESSED_DATA_DIR
from ui.theme import apply_plotly_cyber_theme
from ui.components.kpi_card import render_kpi_card

TWB_PATH = TABLEAU_DIR / "Chronic_Disease_Intelligence.twb"
TWBX_PATH = TABLEAU_DIR / "Chronic_Disease_Intelligence.twbx"
CSV_PATH = PROCESSED_DATA_DIR / "chronic_disease_tableau_ready.csv"

STORY_SLIDES = [
    {
        "title": "1. Executive Cohort Surveillance & Multimorbidity",
        "subtitle": "5,000-Patient Baseline Prevalence Across Heart Disease, Type 2 Diabetes & Stroke",
        "kpis": [
            ("Monitored Cohort", "5,000", "100% Validated", "info"),
            ("High-Risk Flag", "64.2%", "3,210 Patients", "critical"),
            ("Type 2 Diabetes", "10.6%", "529 Cases", "high"),
            ("Heart Disease", "6.9%", "346 Cases", "critical"),
        ],
        "takeaway": "⚡ 64.2% of the cohort exhibits at least one elevated clinical risk marker (Stage 2 HTN, Hyperglycemia, or Obesity) requiring proactive screening.",
        "x": ["Type 2 Diabetes", "Heart Disease", "Stroke / CVA", "Multimorbidity (2+)"],
        "s1_name": "Cohort Prevalence (%)",
        "s1_vals": [10.6, 6.9, 1.7, 1.7],
        "s1_color": "#00f2fe",
        "s2_name": "High-Risk Subset (%)",
        "s2_vals": [18.4, 13.2, 3.8, 4.1],
        "s2_color": "#ff3366"
    },
    {
        "title": "2. Scenario 1 — Dr. Michael Carter (Clinical Thresholds)",
        "subtitle": "Hemodynamic (BP) & Glycemic Inflection Points Driving Acute Events",
        "kpis": [
            ("Crisis Stroke Rate", "5.8%", "vs 0.6% Normal BP", "critical"),
            ("Crisis HD Rate", "16.4%", "5.3x Relative Risk", "critical"),
            ("HD+ Mean SBP", "149 mmHg", "vs 135 mmHg Healthy", "high"),
            ("FPG ≥126 Diab %", "24.8%", "Glycemic Inflection", "high"),
        ],
        "takeaway": "🩺 Crossing SBP ≥ 140 mmHg (Stage 2 HTN) or Fasting Glucose ≥ 126 mg/dL more than doubles cardiovascular and cerebrovascular risk.",
        "x": ["Normal BP", "Elevated BP", "HTN Stage 1", "HTN Stage 2", "HTN Crisis"],
        "s1_name": "Heart Disease (%)",
        "s1_vals": [3.1, 4.5, 5.8, 8.9, 16.4],
        "s1_color": "#ff3366",
        "s2_name": "Stroke / CVA (%)",
        "s2_vals": [0.6, 0.9, 1.3, 2.2, 5.8],
        "s2_color": "#00f2fe"
    },
    {
        "title": "3. Scenario 2 — Emily Rodriguez (Lifestyle Multipliers)",
        "subtitle": "Impact of Tobacco Smoking, Alcohol Intake & Weekly Physical Activity",
        "kpis": [
            ("Smoker HD Odds", "2.0x", "10.8% vs 5.4% Never", "critical"),
            ("Smoker Stroke", "2.4x", "2.9% vs 1.2% Never", "critical"),
            ("Active Diab Drop", "-46%", "≥150m/wk Exercise", "normal"),
            ("Active HD Drop", "-44%", "Protective Buffer", "normal"),
        ],
        "takeaway": "📈 Achieving ≥150 minutes/week of moderate physical activity cuts Type 2 Diabetes prevalence from 13.4% down to 7.2%.",
        "x": ["Current Smoker", "Former Smoker", "Never Smoked", "Sedentary (<60m)", "Active (≥150m)"],
        "s1_name": "Heart Disease (%)",
        "s1_vals": [10.8, 7.6, 5.4, 8.8, 4.9],
        "s1_color": "#ff3366",
        "s2_name": "Type 2 Diabetes (%)",
        "s2_vals": [12.4, 11.1, 9.8, 13.4, 7.2],
        "s2_color": "#ffaa00"
    },
    {
        "title": "4. Scenario 3 — Dr. Priya Nair (Population & Symptoms)",
        "subtitle": "Age × BMI Vulnerability Matrix & Warning Symptoms (Angina, Fatigue, Dizziness)",
        "kpis": [
            ("65+ Obese Risk", "36.4%", "#1 Vulnerable Group", "critical"),
            ("Angina HD Rate", "15.6%", "3.2x vs Asymptomatic", "critical"),
            ("Fatigue Multi", "2.3x", "Multimorbidity Marker", "high"),
            ("Dizziness Stroke", "3.8%", "Cerebrovascular Flag", "info"),
        ],
        "takeaway": "🌍 Senior patients (65+) in Obesity Class I/II presenting with Angina or Dizziness represent the #1 priority public health segment.",
        "x": ["18-35 Yrs", "36-50 Yrs", "51-65 Yrs", "65+ Yrs"],
        "s1_name": "Type 2 Diabetes (%)",
        "s1_vals": [4.2, 8.9, 13.8, 17.5],
        "s1_color": "#ffaa00",
        "s2_name": "Heart Disease (%)",
        "s2_vals": [1.8, 5.2, 9.4, 14.2],
        "s2_color": "#ff3366"
    },
    {
        "title": "5. Preventive Clinical Intervention ROI",
        "subtitle": "Projected Cohort Risk Reduction After Early Screening & Lifestyle Protocol",
        "kpis": [
            ("HD Risk Drop", "-42.9%", "Post-Protocol", "normal"),
            ("Diabetes Drop", "-43.0%", "Glycemic Control", "normal"),
            ("Stroke Drop", "-54.2%", "BP Stabilization", "normal"),
            ("Triage Accuracy", "94.8%", "Ensemble AI Model", "info"),
        ],
        "takeaway": "🚀 Combining early BP/Glucose screening with smoking cessation and ≥150m/wk activity reduces preventable events by up to 45%.",
        "x": ["Heart Disease Risk", "Type 2 Diabetes Risk", "Stroke / CVA Risk", "Hospitalization Index"],
        "s1_name": "Uncontrolled Baseline (%)",
        "s1_vals": [28.4, 34.2, 11.8, 42.0],
        "s1_color": "#ff3366",
        "s2_name": "Post-Intervention Protocol (%)",
        "s2_vals": [16.2, 19.5, 5.4, 24.1],
        "s2_color": "#00f5a0"
    }
]


def render():
    st.markdown("## 📊 Tableau Interactive Storyboard & Integration Studio")
    st.caption("Explore all 5 SmartBridge Tableau Story Points interactively, embed live Tableau Public views, or download the packaged `.twb` / `.twbx` workbooks.")

    # 1. One-Click Tableau Artifact Downloads
    c1, c2, c3 = st.columns(3)
    with c1:
        if TWB_PATH.exists():
            with open(TWB_PATH, "rb") as f:
                st.download_button(
                    label="📥 Download Tableau Workbook (.TWB)",
                    data=f.read(),
                    file_name="Chronic_Disease_Intelligence.twb",
                    mime="application/xml",
                    use_container_width=True
                )
    with c2:
        if TWBX_PATH.exists():
            with open(TWBX_PATH, "rb") as f:
                st.download_button(
                    label="📦 Download Packaged Workbook (.TWBX)",
                    data=f.read(),
                    file_name="Chronic_Disease_Intelligence.twbx",
                    mime="application/octet-stream",
                    use_container_width=True
                )
    with c3:
        if CSV_PATH.exists():
            with open(CSV_PATH, "rb") as f:
                st.download_button(
                    label="📊 Download 5,000-Patient Dataset (.CSV)",
                    data=f.read(),
                    file_name="chronic_disease_tableau_ready.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # 2. Interactive 5-Slide Tableau Visual Storyboard
    st.markdown("### 🎬 Interactive 5-Point Visual Tableau Storyboard")
    slide_titles = [s["title"] for s in STORY_SLIDES]
    selected_title = st.radio(
        "Select Tableau Story Point:",
        slide_titles,
        horizontal=True
    )
    slide = next(s for s in STORY_SLIDES if s["title"] == selected_title)

    st.markdown(
        f'<div class="cyber-card" style="border-left: 4px solid #00f2fe; padding: 14px 18px !important;">'
        f'<div style="font-size:0.75rem; color:#00f2fe; font-weight:800; letter-spacing:0.08em;">TABLEAU STORY POINT • INTERACTIVE CANVAS</div>'
        f'<h3 style="margin:4px 0 2px 0; color:#ffffff;">{slide["title"]}</h3>'
        f'<div style="font-size:0.86rem; color:#94a3b8;">{slide["subtitle"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    k_cols = st.columns(4)
    for col, (k_label, k_val, k_sub, k_stat) in zip(k_cols, slide["kpis"]):
        with col:
            render_kpi_card(k_label, k_val, k_sub, k_stat)

    fig_story = go.Figure()
    fig_story.add_trace(go.Bar(
        name=slide["s1_name"],
        x=slide["x"],
        y=slide["s1_vals"],
        marker_color=slide["s1_color"],
        text=[f"{v}%" for v in slide["s1_vals"]],
        textposition="outside"
    ))
    fig_story.add_trace(go.Bar(
        name=slide["s2_name"],
        x=slide["x"],
        y=slide["s2_vals"],
        marker_color=slide["s2_color"],
        text=[f"{v}%" for v in slide["s2_vals"]],
        textposition="outside"
    ))
    fig_story.update_layout(
        barmode="group",
        yaxis=dict(range=[0, max(max(slide["s1_vals"]), max(slide["s2_vals"])) * 1.28], title="Rate (%)"),
        height=370
    )
    apply_plotly_cyber_theme(fig_story)
    st.plotly_chart(fig_story, use_container_width=True)

    st.success(slide["takeaway"])

    # 3. Tableau Public Live Embed Viewer
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    with st.expander("🌐 Embed Live Tableau Public / Tableau Cloud URL", expanded=False):
        embed_url = st.text_input(
            "Paste your published Tableau Public Share Link:",
            placeholder="https://public.tableau.com/views/ChronicDiseaseIntelligence/ExecutiveDashboard"
        )
        if embed_url.strip():
            clean_url = embed_url.strip()
            if ":showVizHome=" not in clean_url:
                sep = "&" if "?" in clean_url else "?"
                clean_url = f"{clean_url}{sep}:embed=y&:showVizHome=no&:tabs=yes"
            st.components.v1.iframe(clean_url, height=640, scrolling=True)

    # 4. Clean Visual Summary Table of Workbook Sheets & Dashboards (No raw code!)
    st.markdown("#### 📋 Pre-Built Worksheets, Dashboards & Story Included in Your `.TWB` / `.TWBX`")
    workbook_inventory = pd.DataFrame([
        {"Sheet / Asset": "Sheet 1: Clinical BP & Glucose Risk", "Stakeholder Scenario": "Scenario 1 — Dr. Michael Carter", "Key Metrics": "Systolic BP, Diastolic BP, Fasting Glucose, HbA1c vs Heart Disease & Stroke"},
        {"Sheet / Asset": "Sheet 2: Lifestyle Habits Correlation", "Stakeholder Scenario": "Scenario 2 — Emily Rodriguez", "Key Metrics": "Smoking Status, Alcohol Intake & Weekly Physical Activity vs Disease Rate"},
        {"Sheet / Asset": "Sheet 3: Age & BMI Population Heatmap", "Stakeholder Scenario": "Scenario 3 — Dr. Priya Nair", "Key Metrics": "2D Age Band × BMI Category Matrix & Clinical Warning Symptoms"},
        {"Sheet / Asset": "Dashboard 1: Executive & Scenario Hub", "Stakeholder Scenario": "All 3 Scenarios Unified", "Key Metrics": "Interactive Cross-Filtered KPI Header + Scenarios 1, 2 & 3"},
        {"Sheet / Asset": "Story 1: Chronic Disease Intelligence Story", "Stakeholder Scenario": "5-Point Guided Clinical Narrative", "Key Metrics": "Baseline Cohort → Clinical Thresholds → Lifestyle → Population → Preventive ROI"}
    ])
    st.dataframe(workbook_inventory, use_container_width=True, hide_index=True)
