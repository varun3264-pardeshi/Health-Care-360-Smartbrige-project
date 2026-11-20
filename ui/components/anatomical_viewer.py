"""
PulsePoint Cyber-Medical Intelligence System
Interactive Cyber-Medical Anatomical Organ System Visualizer
Integrates Digital Twin Holographic Scanning, Organ Nodes & Cardiorenal-Metabolic Triads
"""

import os
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from ui.theme import apply_plotly_cyber_theme

HOLOGRAM_IMG_PATH = Path(__file__).resolve().parent.parent / "assets" / "cyber_medical_hologram.jpg"

def render_anatomical_organ_viewer(df: pd.DataFrame):
    """
    Renders an interactive schematic anatomical organ network with clinical
    pathophysiological mappings, high-tech holographic digital twin asset,
    and explicit medical limitations labeling.
    """
    st.markdown("### 🫀 Cyber-Medical Anatomical Digital Twin & Organ Vulnerability System")
    st.caption("Interactive multi-organ telemetry mapping physiological biomarkers to targeted anatomical structures.")

    tab_twin, tab_wireframe, tab_triad = st.tabs([
        "🔬 Holographic Digital Twin Scanner",
        "🌐 Interactive Topological Organ Map",
        "⚡ Cardiorenal-Metabolic Syndrome Triad"
    ])

    with tab_twin:
        c_holo, c_panel = st.columns([6, 6])
        
        with c_holo:
            if HOLOGRAM_IMG_PATH.exists():
                st.image(str(HOLOGRAM_IMG_PATH), caption="PulsePoint Cyber-Medical Digital Twin Holographic Telemetry Overlay", use_container_width=True)
            else:
                st.info("Holographic Asset Loading...")

        with c_panel:
            st.markdown("#### 🎯 Organ System Live Telemetry")
            organ_options = [
                "Cardiovascular System (Heart / CAD)",
                "Cerebrovascular System (Brain / Stroke)",
                "Endocrine / Metabolic Axis (Pancreas / Diabetes)",
                "Peripheral Hemodynamics (Arterial Tree)"
            ]
            selected_organ = st.selectbox("Select Target Organ for Scanning", organ_options, index=0)

            if "Cardiovascular" in selected_organ:
                hd_rate = (df["heart_disease"].mean() * 100.0)
                angina_rate = ((df["chest_pain_type"] == "Typical Angina").mean() * 100.0)
                sbp_mean = df["systolic_bp"].mean()
                ldl_mean = df["cholesterol_ldl"].mean()

                st.markdown(
                    f"""
                    <div class="cyber-card" style="border-left: 4px solid #ff3366;">
                        <h4 style="color: #ff3366; margin: 0 0 8px 0;">Cardiovascular Organ Core</h4>
                        <p style="font-size: 0.85rem; color: #8b949e;">Myocardial perfusion and coronary artery disease surveillance.</p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
                            <div><b>CAD Prevalence:</b> {hd_rate:.1f}%</div>
                            <div><b>Typical Angina:</b> {angina_rate:.1f}%</div>
                            <div><b>Mean Systolic BP:</b> {sbp_mean:.1f} mmHg</div>
                            <div><b>Mean Serum LDL:</b> {ldl_mean:.1f} mg/dL</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif "Cerebrovascular" in selected_organ:
                stroke_rate = (df["stroke"].mean() * 100.0)
                dizzy_rate = (df["dizziness_reported"].mean() * 100.0)
                bp_crisis = ((df["systolic_bp"] >= 180) | (df["diastolic_bp"] >= 120)).sum()

                st.markdown(
                    f"""
                    <div class="cyber-card" style="border-left: 4px solid #4facfe;">
                        <h4 style="color: #4facfe; margin: 0 0 8px 0;">Cerebrovascular Organ Core</h4>
                        <p style="font-size: 0.85rem; color: #8b949e;">Cerebral ischemia, transient attack susceptibility, and stroke surveillance.</p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
                            <div><b>Stroke Prevalence:</b> {stroke_rate:.1f}%</div>
                            <div><b>Dizziness Episodes:</b> {dizzy_rate:.1f}%</div>
                            <div><b>Hypertensive Crisis:</b> {bp_crisis:,} patients</div>
                            <div><b>Active Smokers:</b> {(df['smoking_status']=='Current').sum():,} patients</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            elif "Endocrine" in selected_organ:
                diab_rate = (df["diabetes"].mean() * 100.0)
                glucose_mean = df["fasting_glucose"].mean()
                hba1c_mean = df["hba1c"].mean()
                obese_pct = ((df["bmi"] >= 30.0).mean() * 100.0)

                st.markdown(
                    f"""
                    <div class="cyber-card" style="border-left: 4px solid #ffaa00;">
                        <h4 style="color: #ffaa00; margin: 0 0 8px 0;">Endocrine & Pancreatic Axis</h4>
                        <p style="font-size: 0.85rem; color: #8b949e;">Beta-cell insulin secretion, glycemic regulation, and adiposity.</p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
                            <div><b>Diabetes Prevalence:</b> {diab_rate:.1f}%</div>
                            <div><b>Mean Fasting Glucose:</b> {glucose_mean:.1f} mg/dL</div>
                            <div><b>Mean Glycated HbA1c:</b> {hba1c_mean:.1f}%</div>
                            <div><b>Classified Obese (BMI ≥30):</b> {obese_pct:.1f}%</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            else: # Peripheral Hemodynamics
                map_mean = df["mean_arterial_pressure"].mean()
                pp_mean = df["pulse_pressure"].mean()
                multi_rate = ((df["multimorbidity_count"] >= 2).mean() * 100.0)

                st.markdown(
                    f"""
                    <div class="cyber-card" style="border-left: 4px solid #a855f7;">
                        <h4 style="color: #a855f7; margin: 0 0 8px 0;">Systemic Arterial Network</h4>
                        <p style="font-size: 0.85rem; color: #8b949e;">Total peripheral vascular resistance and arterial compliance.</p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px;">
                            <div><b>Mean Arterial Pressure:</b> {map_mean:.1f} mmHg</div>
                            <div><b>Mean Pulse Pressure:</b> {pp_mean:.1f} mmHg</div>
                            <div><b>Multimorbidity (≥2):</b> {multi_rate:.1f}%</div>
                            <div><b>Sedentary Cohort:</b> {(df['physical_activity_mins']<60).mean()*100:.1f}%</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.caption(
                "⚠️ **Scope & Clinical Limitations:** This anatomical visualizer is a schematic cyber-medical topological "
                "model grounded in epidemiological biomarkers. It does NOT represent volumetric 3D patient radiology (CT/MRI) "
                "and must not be interpreted as radiological diagnosis."
            )

    with tab_wireframe:
        # Interactive Plotly schematic anatomical model
        fig = go.Figure()

        # Anatomical silhouette wireframe lines
        body_x = [0, 0, 0.8, 1.2, 0.7, 0.6, 0.7, 0.4, 0, -0.4, -0.7, -0.6, -0.7, -1.2, -0.8, 0, 0]
        body_y = [8.5, 7.5, 7.0, 4.5, 4.2, 1.5, -3.0, -3.0, 1.0, -3.0, -3.0, 1.5, 4.2, 4.5, 7.0, 7.5, 8.5]
        
        fig.add_trace(go.Scatter(
            x=body_x, y=body_y,
            mode="lines",
            line=dict(color="rgba(0, 242, 254, 0.40)", width=2),
            hoverinfo="none",
            name="Anatomical Wireframe"
        ))

        # Organ Target Nodes
        nodes = [
            {"name": "Cerebrovascular (Brain)", "x": 0.0, "y": 8.0, "color": "#4facfe", "size": 30, "desc": "Stroke & Ischemic Risk"},
            {"name": "Cardiovascular (Heart)", "x": 0.2, "y": 5.8, "color": "#ff3366", "size": 36, "desc": "Coronary CAD & Angina"},
            {"name": "Endocrine (Pancreas)", "x": 0.0, "y": 4.2, "color": "#ffaa00", "size": 30, "desc": "Diabetes & Glycemic Axis"},
            {"name": "Vascular Left", "x": -0.7, "y": 3.0, "color": "#a855f7", "size": 22, "desc": "Arterial Hemodynamics"},
            {"name": "Vascular Right", "x": 0.7, "y": 3.0, "color": "#a855f7", "size": 22, "desc": "Arterial Hemodynamics"}
        ]

        for n in nodes:
            fig.add_trace(go.Scatter(
                x=[n["x"]], y=[n["y"]],
                mode="markers+text",
                marker=dict(
                    size=n["size"],
                    color=n["color"],
                    line=dict(color="#ffffff", width=2.5),
                    opacity=0.95
                ),
                text=[n["name"].split(" ")[0]],
                textposition="top center",
                textfont=dict(color="#f0f6fc", size=11, family="Rajdhani"),
                hovertext=f"<b>{n['name']}</b><br>{n['desc']}",
                hoverinfo="text",
                name=n["name"]
            ))

        fig.update_layout(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-2.5, 2.5]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-4.0, 10.0]),
            height=460,
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10)
        )
        apply_plotly_cyber_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

    with tab_triad:
        st.markdown("#### ⚡ The Cardiorenal-Metabolic Chronic Disease Cascade")
        st.markdown(
            """
            In population epidemiology, **Heart Disease**, **Type 2 Diabetes**, and **Stroke** do not act as isolated diseases. 
            They form an integrated **pathophysiological feedback loop**:
            """
        )

        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.markdown(
                """
                <div class="cyber-card" style="border-top: 4px solid #ffaa00;">
                    <h4 style="color:#ffaa00;">1. Metabolic Axis</h4>
                    <p style="font-size:0.85rem; color:#cbd5e1;">
                        Insulin resistance and elevated HbA1c lead to systemic microvascular endothelial dysfunction, 
                        accelerating atheroma formation in arterial vessels.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_t2:
            st.markdown(
                """
                <div class="cyber-card" style="border-top: 4px solid #ff3366;">
                    <h4 style="color:#ff3366;">2. Coronary Axis</h4>
                    <p style="font-size:0.85rem; color:#cbd5e1;">
                        Elevated LDL cholesterol and chronic shear stress cause coronary arterial plaque, 
                        resulting in myocardial ischemia, angina, and reduced cardiac output.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_t3:
            st.markdown(
                """
                <div class="cyber-card" style="border-top: 4px solid #4facfe;">
                    <h4 style="color:#4facfe;">3. Cerebrovascular Axis</h4>
                    <p style="font-size:0.85rem; color:#cbd5e1;">
                        Chronic systemic hypertension and plaque embolization propagate downstream to cerebral vessels, 
                        triggering transient ischemic episodes and ischemic stroke.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
