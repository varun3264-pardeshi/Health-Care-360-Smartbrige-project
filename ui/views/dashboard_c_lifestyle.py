"""
Dashboard C: Lifestyle and Symptoms
Behavioral Risk Factors, Symptom Severity Clusters & Epidemiological Associations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from ui.theme import apply_plotly_cyber_theme
from ui.components.kpi_card import render_kpi_card

def render(df: pd.DataFrame, active_filters: dict):
    st.markdown(
        '<div class="cyber-card" style="border-left: 4px solid #00f5a0; padding: 14px 20px !important;">'
        '<span class="status-pill pill-normal">SCENARIO 2 • EMILY RODRIGUEZ (HEALTHCARE DATA ANALYST)</span>'
        '<h2 style="margin: 6px 0 2px 0; color: #ffffff; font-weight: 900;">🏃 Lifestyle Habits, Behavioral Multipliers &amp; Symptom Clusters</h2>'
        '<p style="margin: 0; color: #94a3b8; font-size: 0.88rem;">Surveillance of modifiable behavioral risk vectors (tobacco smoking, alcohol intake, physical activity) and clinical symptom co-occurrence.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if len(df) == 0:
        st.warning("No records match active filters.")
        return

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Current Smokers", f"{(df['smoking_status']=='Current').mean()*100:.1f}%", "2.0x Coronary Risk Multiplier", "critical")
    with k2:
        render_kpi_card("WHO Active (≥150m/wk)", f"{(df['physical_activity_mins']>=150).mean()*100:.1f}%", "-46% Diabetes Reduction", "normal")
    with k3:
        render_kpi_card("Symptomatic Angina", f"{(df['chest_pain_type']!='None').mean()*100:.1f}%", "Chest Pain Presentation", "high")
    with k4:
        render_kpi_card("Chronic Fatigue", f"{df['fatigue_reported'].mean()*100:.1f}%", "Metabolic & Cardiac Marker", "info")

    # 1. Behavioral Lifestyle Risk Factors Row 1
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🚬 Tobacco Smoking Status vs Disease Prevalence")
        smk_agg = df.groupby("smoking_status")[["heart_disease", "stroke", "diabetes"]].mean() * 100.0
        smk_agg = smk_agg.reset_index()

        fig_smk = px.bar(
            smk_agg,
            x="smoking_status",
            y=["heart_disease", "stroke", "diabetes"],
            barmode="group",
            color_discrete_sequence=["#ff3366", "#4facfe", "#ffaa00"],
            labels={"value": "Prevalence (%)", "variable": "Condition", "smoking_status": "Smoking History"}
        )
        apply_plotly_cyber_theme(fig_smk)
        st.plotly_chart(fig_smk, use_container_width=True)

    with c2:
        st.markdown("#### 🍷 Alcohol Consumption Intensity vs Multimorbidity")
        alc_agg = df.groupby("alcohol_consumption").agg(
            patients=("patient_id", "count"),
            multi_pct=("multimorbidity_count", lambda x: (x >= 2).mean() * 100.0),
            avg_sbp=("systolic_bp", "mean")
        ).reset_index()

        fig_alc = px.bar(
            alc_agg,
            x="alcohol_consumption",
            y="multi_pct",
            color="avg_sbp",
            color_continuous_scale="Viridis",
            labels={"multi_pct": "Multimorbidity Rate (≥2 Conditions) %", "alcohol_consumption": "Intake Level", "avg_sbp": "Avg SBP mmHg"}
        )
        apply_plotly_cyber_theme(fig_alc)
        st.plotly_chart(fig_alc, use_container_width=True)

    # 2. Row 2: Physical Activity & Chest Pain Angina
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### 🏃 Physical Activity Levels (WHO Guideline Adherence)")
        exe_agg = df.groupby("exercise_level")[["heart_disease", "diabetes"]].mean() * 100.0
        exe_agg = exe_agg.reset_index()

        fig_exe = px.bar(
            exe_agg,
            x="exercise_level",
            y=["heart_disease", "diabetes"],
            barmode="group",
            color_discrete_sequence=["#ff3366", "#ffaa00"],
            labels={"value": "Prevalence (%)", "exercise_level": "Activity Cohort"}
        )
        apply_plotly_cyber_theme(fig_exe)
        st.plotly_chart(fig_exe, use_container_width=True)

    with c4:
        st.markdown("#### 💔 Angina Chest Pain Classification vs CAD Odds")
        cp_agg = df.groupby("chest_pain_type").agg(
            patients=("patient_id", "count"),
            hd_pct=("heart_disease", lambda x: x.mean() * 100.0)
        ).reset_index()

        fig_cp = px.bar(
            cp_agg,
            x="chest_pain_type",
            y="hd_pct",
            text="hd_pct",
            color="hd_pct",
            color_continuous_scale="Reds",
            labels={"hd_pct": "Heart Disease %", "chest_pain_type": "Chest Pain Presentation"}
        )
        fig_cp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        apply_plotly_cyber_theme(fig_cp)
        st.plotly_chart(fig_cp, use_container_width=True)

    # 3. Symptom Co-Occurrence Heatmap
    st.markdown("#### 🩺 Clinical Symptom Prevalence & Co-Occurrence Matrix")
    
    # Calculate cross-symptom co-occurrence
    symptom_cols = ["fatigue_reported", "dizziness_reported", "shortness_of_breath"]
    symptom_names = ["Clinical Fatigue", "Dizziness / Vertigo", "Exertional Dyspnea"]
    
    matrix_data = []
    for s1 in symptom_cols:
        row = []
        for s2 in symptom_cols:
            if s1 == s2:
                row.append(float(round(df[s1].mean() * 100.0, 1)))
            else:
                # Co-occurrence percentage: both present
                co_pct = float(round(((df[s1] == 1) & (df[s2] == 1)).mean() * 100.0, 1))
                row.append(co_pct)
        matrix_data.append(row)

    fig_symp = px.imshow(
        matrix_data,
        x=symptom_names,
        y=symptom_names,
        text_auto=True,
        color_continuous_scale="Plasma",
        labels=dict(color="Co-Occurrence (%)")
    )
    apply_plotly_cyber_theme(fig_symp)
    st.plotly_chart(fig_symp, use_container_width=True)
