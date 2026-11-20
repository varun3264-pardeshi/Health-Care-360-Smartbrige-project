"""
Dashboard D: Population Insights
Cohort Stratification, 2D Density Matrices, Segment Rankings & Geospatial Variance
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
        '<div class="cyber-card" style="border-left: 4px solid #a855f7; padding: 14px 20px !important;">'
        '<span class="status-pill pill-high">SCENARIO 3 • DR. PRIYA NAIR (PUBLIC HEALTH RESEARCHER)</span>'
        '<h2 style="margin: 6px 0 2px 0; color: #ffffff; font-weight: 900;">🌍 Population Cohort Stratification &amp; Vulnerability Matrix</h2>'
        '<p style="margin: 0; color: #94a3b8; font-size: 0.88rem;">2D Age × BMI intersection heatmaps, demographic vulnerability rankings, and regional chronic disease variation.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if len(df) == 0:
        st.warning("No records match active filters.")
        return

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Senior Cohort (65+)", f"{(df['age']>=65).mean()*100:.1f}%", f"{(df['age']>=65).sum():,} Senior Patients", "critical")
    with k2:
        render_kpi_card("Obesity Class I/II+", f"{(df['bmi']>=30).mean()*100:.1f}%", f"{(df['bmi']>=30).sum():,} High-BMI Patients", "high")
    with k3:
        render_kpi_card("Multimorbid Burden", f"{(df['multimorbidity_count']>=2).mean()*100:.1f}%", "2+ Co-Occurring Diseases", "critical")
    with k4:
        render_kpi_card("Regional Networks", f"{df['region'].nunique()} Zones", "Population Surveillance", "info")

    # 1. Age-by-BMI 2D Cross-Tabulation Heatmap
    st.markdown("#### 🗺️ 2D Biomarker Intersection: Age Group vs BMI Category")
    
    bmi_order = ["Underweight", "Normal", "Overweight", "Obesity Class I", "Obesity Class II+"]
    age_order = ["18-35", "36-50", "51-65", "65+"]

    # Pivot table for Multimorbidity rate (%)
    pivot_multi = df.pivot_table(
        index="bmi_category",
        columns="age_group",
        values="multimorbidity_count",
        aggfunc=lambda x: np.round((x >= 2).mean() * 100.0, 1),
        fill_value=0.0
    )
    # Reindex to standard epidemiological order
    present_bmis = [b for b in bmi_order if b in pivot_multi.index]
    present_ages = [a for a in age_order if a in pivot_multi.columns]
    pivot_multi = pivot_multi.reindex(index=present_bmis, columns=present_ages)

    fig_matrix = px.imshow(
        pivot_multi,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="Turbo",
        labels=dict(color="Multimorbidity Rate (≥2) %", x="Age Group", y="BMI Category")
    )
    apply_plotly_cyber_theme(fig_matrix)
    st.plotly_chart(fig_matrix, use_container_width=True)

    # 2. Population Segment Risk Ranking
    st.markdown("#### 🏆 Population Risk Segment Stratification & Vulnerability Ranking")
    
    # Segment by Age Group + Smoking + Exercise Level
    segment_df = df.groupby(["age_group", "smoking_status", "exercise_level"]).agg(
        Cohort_Size=("patient_id", "count"),
        Heart_Disease_Pct=("heart_disease", lambda x: np.round(x.mean() * 100.0, 1)),
        Diabetes_Pct=("diabetes", lambda x: np.round(x.mean() * 100.0, 1)),
        Stroke_Pct=("stroke", lambda x: np.round(x.mean() * 100.0, 1)),
        Multimorbidity_Pct=("multimorbidity_count", lambda x: np.round((x >= 2).mean() * 100.0, 1)),
        Avg_Systolic_BP=("systolic_bp", lambda x: np.round(x.mean(), 1)),
        Avg_Glucose=("fasting_glucose", lambda x: np.round(x.mean(), 1))
    ).reset_index()

    # Filter out very small segments (< 20) for statistical stability
    segment_df = segment_df[segment_df["Cohort_Size"] >= 20]
    segment_df = segment_df.sort_values(by="Multimorbidity_Pct", ascending=False).reset_index(drop=True)
    segment_df["Vulnerability_Rank"] = segment_df.index + 1

    # Reorder columns
    cols = ["Vulnerability_Rank", "age_group", "smoking_status", "exercise_level", "Cohort_Size", "Multimorbidity_Pct", "Heart_Disease_Pct", "Diabetes_Pct", "Stroke_Pct", "Avg_Systolic_BP"]
    segment_display = segment_df[cols].rename(columns={
        "age_group": "Age Cohort",
        "smoking_status": "Smoking",
        "exercise_level": "Activity Profile",
        "Cohort_Size": "Patients",
        "Multimorbidity_Pct": "Multimorbidity %",
        "Heart_Disease_Pct": "CAD %",
        "Diabetes_Pct": "Diab %",
        "Stroke_Pct": "Stroke %",
        "Avg_Systolic_BP": "Mean SBP"
    })

    st.dataframe(segment_display, use_container_width=True, hide_index=True)

    # 3. Regional Geographical Risk Heatmap
    st.markdown("#### 🗺️ Healthcare Administrative Network Regional Variation")
    
    reg_summary = df.groupby("region").agg(
        Total_Patients=("patient_id", "count"),
        CAD_Rate=("heart_disease", lambda x: np.round(x.mean() * 100, 1)),
        Diabetes_Rate=("diabetes", lambda x: np.round(x.mean() * 100, 1)),
        Stroke_Rate=("stroke", lambda x: np.round(x.mean() * 100, 1)),
        Mean_BMI=("bmi", lambda x: np.round(x.mean(), 1)),
        Mean_BP=("systolic_bp", lambda x: np.round(x.mean(), 1))
    ).reset_index()

    c_geo1, c_geo2 = st.columns([6, 6])
    with c_geo1:
        fig_geo = px.bar(
            reg_summary,
            x="region",
            y=["CAD_Rate", "Diabetes_Rate", "Stroke_Rate"],
            barmode="group",
            color_discrete_sequence=["#ff3366", "#ffaa00", "#4facfe"],
            labels={"value": "Prevalence (%)", "variable": "Disease Target", "region": "Geographic Region"}
        )
        apply_plotly_cyber_theme(fig_geo)
        st.plotly_chart(fig_geo, use_container_width=True)

    with c_geo2:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        st.dataframe(reg_summary, use_container_width=True, hide_index=True)
