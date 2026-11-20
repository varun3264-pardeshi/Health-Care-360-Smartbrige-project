"""
Dashboard B: Clinical Risk Assessment
Physiological Biomarker Surveillance, Hemodynamics, Glycemic & Lipid Profiling
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
        '<div class="cyber-card" style="border-left: 4px solid #ff3366; padding: 14px 20px !important;">'
        '<span class="status-pill pill-critical">SCENARIO 1 • DR. MICHAEL CARTER (CLINICAL RISK ASSESSMENT OFFICER)</span>'
        '<h2 style="margin: 6px 0 2px 0; color: #ffffff; font-weight: 900;">🩺 Clinical Risk Assessment &amp; Biomarker Surveillance</h2>'
        '<p style="margin: 0; color: #94a3b8; font-size: 0.88rem;">Deep-dive hemodynamic (BP), serum lipid (LDL/HDL), glycemic (Fasting Glucose/HbA1c), and 3D risk space stratification.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if len(df) == 0:
        st.warning("No records match active filters.")
        return

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Mean Systolic BP", f"{df['systolic_bp'].mean():.1f} mmHg", f"Stage 2+ HTN: {((df['systolic_bp']>=140)|(df['diastolic_bp']>=90)).mean()*100:.1f}%", "critical")
    with k2:
        render_kpi_card("Mean Fasting Glucose", f"{df['fasting_glucose'].mean():.1f} mg/dL", f"Diabetic FPG (≥126): {(df['fasting_glucose']>=126).mean()*100:.1f}%", "high")
    with k3:
        render_kpi_card("Mean Total / LDL Chol", f"{df['cholesterol_total'].mean():.0f} / {df['cholesterol_ldl'].mean():.0f}", "mg/dL Serum Profile", "info")
    with k4:
        render_kpi_card("Mean Cohort BMI", f"{df['bmi'].mean():.1f} kg/m²", f"Obesity (≥30): {(df['bmi']>=30).mean()*100:.1f}%", "normal")

    # 1. Clinical Biomarker Distributions Row 1
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🩸 Blood Pressure Stages (Systolic vs Diastolic BP)")
        sample_df = df.sample(min(len(df), 450), random_state=42)

        fig_bp = px.scatter(
            sample_df,
            x="systolic_bp",
            y="diastolic_bp",
            color="bp_category",
            color_discrete_map={
                "Normal": "#00f5a0",
                "Elevated": "#4facfe",
                "Hypertension Stage 1": "#ffaa00",
                "Hypertension Stage 2": "#ff6b6b",
                "Hypertensive Crisis": "#ff0055"
            },
            hover_data=["patient_id", "age", "heart_disease", "stroke"],
            labels={"systolic_bp": "Systolic BP (mmHg)", "diastolic_bp": "Diastolic BP (mmHg)"}
        )
        fig_bp.add_vline(x=130, line_dash="dash", line_color="rgba(255, 170, 0, 0.5)", annotation_text="Stage 1 SBP")
        fig_bp.add_vline(x=140, line_dash="dash", line_color="rgba(255, 51, 102, 0.5)", annotation_text="Stage 2 SBP")
        fig_bp.add_hline(y=90, line_dash="dash", line_color="rgba(255, 51, 102, 0.5)", annotation_text="Stage 2 DBP")
        apply_plotly_cyber_theme(fig_bp)
        st.plotly_chart(fig_bp, use_container_width=True)

    with c2:
        st.markdown("#### 🧪 Blood Sugar Control (Fasting Glucose vs HbA1c)")
        fig_gluc = px.scatter(
            sample_df,
            x="fasting_glucose",
            y="hba1c",
            color="glucose_category",
            color_discrete_map={
                "Normal": "#00f5a0",
                "Prediabetes": "#ffaa00",
                "Diabetes": "#ff3366"
            },
            hover_data=["patient_id", "bmi", "diabetes"],
            labels={"fasting_glucose": "Fasting Glucose (mg/dL)", "hba1c": "HbA1c (3-Month Sugar %)"}
        )
        fig_gluc.add_vline(x=126, line_dash="dash", line_color="#ff3366", annotation_text="Diabetic (126)")
        fig_gluc.add_hline(y=6.5, line_dash="dash", line_color="#ff3366", annotation_text="Diabetic (6.5%)")
        apply_plotly_cyber_theme(fig_gluc)
        st.plotly_chart(fig_gluc, use_container_width=True)

    # 2. Row 2: Cholesterol Profiles & BMI Distribution
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("#### 🧬 Good vs Bad Cholesterol (LDL vs HDL Profile)")
        fig_chol = px.scatter(
            sample_df,
            x="cholesterol_ldl",
            y="cholesterol_hdl",
            color="heart_disease",
            color_continuous_scale=["#4facfe", "#ff3366"],
            labels={"cholesterol_ldl": "LDL (Bad) Cholesterol mg/dL", "cholesterol_hdl": "HDL (Good) Cholesterol mg/dL"},
            hover_data=["patient_id", "cholesterol_ratio"]
        )
        fig_chol.update_layout(coloraxis_colorbar=dict(title="Heart Disease"))
        apply_plotly_cyber_theme(fig_chol)
        st.plotly_chart(fig_chol, use_container_width=True)

    with c4:
        st.markdown("#### ⚖️ Body Mass Index (BMI) Distribution by Gender")
        fig_bmi_v = px.violin(
            sample_df,
            x="gender",
            y="bmi",
            color="diabetes",
            box=True,
            points=False,
            color_discrete_map={0: "#00f2fe", 1: "#ffaa00"},
            labels={"diabetes": "Diabetes Status (0=No, 1=Yes)"}
        )
        apply_plotly_cyber_theme(fig_bmi_v)
        st.plotly_chart(fig_bmi_v, use_container_width=True)

    # 3. Interactive 3D Chronic Risk Galaxy Space
    st.markdown("#### 🌌 Interactive 3D Clinical Risk Map (BP × Blood Sugar × Age)")
    sample_3d = df.sample(min(len(df), 320), random_state=42)
    fig_3d = px.scatter_3d(
        sample_3d,
        x="systolic_bp",
        y="fasting_glucose",
        z="age",
        color="multimorbidity_count",
        size="bmi",
        color_continuous_scale="Plasma",
        hover_data=["patient_id", "bp_category", "glucose_category", "heart_disease", "stroke"],
        labels={"systolic_bp": "Systolic BP (mmHg)", "fasting_glucose": "Glucose (mg/dL)", "age": "Age (Yrs)", "multimorbidity_count": "Conditions"}
    )
    fig_3d.update_layout(
        scene=dict(
            xaxis=dict(backgroundcolor="rgba(8, 16, 36, 0.9)", gridcolor="rgba(0, 242, 254, 0.15)", title="Systolic BP (mmHg)"),
            yaxis=dict(backgroundcolor="rgba(8, 16, 36, 0.9)", gridcolor="rgba(0, 242, 254, 0.15)", title="Glucose (mg/dL)"),
            zaxis=dict(backgroundcolor="rgba(8, 16, 36, 0.9)", gridcolor="rgba(0, 242, 254, 0.15)", title="Age (Years)"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        height=460
    )
    st.plotly_chart(fig_3d, use_container_width=True)

    # 4. Disease Positive vs Disease Negative Comparison Table (Immutable Read-Only)
    st.markdown("#### 📊 Comparative Biomarker Summary (Immutable Read-Only Ledger)")
    summary_data = []
    for cond_name, col in [("Heart Disease", "heart_disease"), ("Type 2 Diabetes", "diabetes"), ("Stroke", "stroke")]:
        pos = df[df[col] == 1]
        neg = df[df[col] == 0]
        summary_data.append({
            "Target Condition": cond_name,
            "Positive Cases": f"{len(pos):,}",
            "Healthy Cases": f"{len(neg):,}",
            "Avg Age (Disease vs Healthy)": f"{pos['age'].mean():.1f} vs {neg['age'].mean():.1f} yrs",
            "Avg SBP (Disease vs Healthy)": f"{pos['systolic_bp'].mean():.1f} vs {neg['systolic_bp'].mean():.1f} mmHg",
            "Avg Sugar (Disease vs Healthy)": f"{pos['fasting_glucose'].mean():.1f} vs {neg['fasting_glucose'].mean():.1f} mg/dL",
            "Avg BMI (Disease vs Healthy)": f"{pos['bmi'].mean():.1f} vs {neg['bmi'].mean():.1f}"
        })
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
