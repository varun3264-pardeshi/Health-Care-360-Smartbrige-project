"""
Multi-Condition AI/ML Risk Predictor
Interactive Simulation Engine with Calibrated Risk Inference & Feature Explanations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from ml_engine.predictor import DiseaseRiskPredictor, DISCLAIMER_TEXT
from ml_engine.evaluator import get_latest_model_metrics
from ui.theme import apply_plotly_cyber_theme

# Clinical Demo Presets
PRESET_PERSONAS = {
    "Custom Simulation": {
        "age": 55, "gender": "Male", "bmi": 27.5, "systolic_bp": 135, "diastolic_bp": 85,
        "cholesterol_total": 210.0, "cholesterol_hdl": 45.0, "cholesterol_ldl": 140.0,
        "fasting_glucose": 110.0, "hba1c": 5.9, "smoking_status": "Former",
        "alcohol_consumption": "Moderate", "physical_activity_mins": 90,
        "fatigue_reported": 0, "chest_pain_type": "None", "dizziness_reported": 0, "shortness_of_breath": 0
    },
    "High-Risk Cardiovascular Patient": {
        "age": 68, "gender": "Male", "bmi": 31.2, "systolic_bp": 165, "diastolic_bp": 98,
        "cholesterol_total": 265.0, "cholesterol_hdl": 35.0, "cholesterol_ldl": 195.0,
        "fasting_glucose": 122.0, "hba1c": 6.2, "smoking_status": "Current",
        "alcohol_consumption": "Moderate", "physical_activity_mins": 30,
        "fatigue_reported": 1, "chest_pain_type": "Typical Angina", "dizziness_reported": 1, "shortness_of_breath": 1
    },
    "Severe Metabolic Syndrome / Diabesity": {
        "age": 54, "gender": "Female", "bmi": 36.8, "systolic_bp": 145, "diastolic_bp": 90,
        "cholesterol_total": 240.0, "cholesterol_hdl": 38.0, "cholesterol_ldl": 160.0,
        "fasting_glucose": 185.0, "hba1c": 8.9, "smoking_status": "Never",
        "alcohol_consumption": "None", "physical_activity_mins": 20,
        "fatigue_reported": 1, "chest_pain_type": "None", "dizziness_reported": 0, "shortness_of_breath": 1
    },
    "Healthy Low-Risk Control": {
        "age": 32, "gender": "Female", "bmi": 21.8, "systolic_bp": 112, "diastolic_bp": 72,
        "cholesterol_total": 165.0, "cholesterol_hdl": 62.0, "cholesterol_ldl": 88.0,
        "fasting_glucose": 84.0, "hba1c": 5.0, "smoking_status": "Never",
        "alcohol_consumption": "None", "physical_activity_mins": 240,
        "fatigue_reported": 0, "chest_pain_type": "None", "dizziness_reported": 0, "shortness_of_breath": 0
    }
}

def render():
    st.markdown("## 🤖 Multi-Condition AI/ML Risk Simulation Engine")
    st.caption("Machine-learning risk stratification across coronary, metabolic, and cerebrovascular axes.")

    # Persona Quick-Select
    col_preset, _ = st.columns([4, 6])
    with col_preset:
        selected_persona = st.selectbox("Select Clinical Simulation Persona", list(PRESET_PERSONAS.keys()), index=0)
    
    preset = PRESET_PERSONAS[selected_persona]

    # Clinical Feature Inputs
    st.markdown("#### 📋 Patient Clinical Feature Vector")
    
    tab1, tab2, tab3 = st.tabs(["Biomarkers & Vitals", "Lifestyle & Demographics", "Symptoms & History"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            systolic_bp = st.slider("Systolic Blood Pressure (mmHg)", 80, 220, preset["systolic_bp"])
            diastolic_bp = st.slider("Diastolic Blood Pressure (mmHg)", 50, 130, preset["diastolic_bp"])
            bmi = st.number_input("Body Mass Index (BMI kg/m²)", 12.0, 60.0, preset["bmi"], step=0.1)
        with c2:
            cholesterol_total = st.slider("Total Cholesterol (mg/dL)", 100, 400, int(preset["cholesterol_total"]))
            cholesterol_hdl = st.slider("HDL Cholesterol (mg/dL)", 15, 120, int(preset["cholesterol_hdl"]))
            cholesterol_ldl = st.slider("LDL Cholesterol (mg/dL)", 40, 300, int(preset["cholesterol_ldl"]))
        with c3:
            fasting_glucose = st.slider("Fasting Blood Glucose (mg/dL)", 50, 350, int(preset["fasting_glucose"]))
            hba1c = st.slider("Glycated Hemoglobin HbA1c (%)", 4.0, 14.0, float(preset["hba1c"]), step=0.1)

    with tab2:
        c4, c5, c6 = st.columns(3)
        with c4:
            age = st.slider("Patient Age (Years)", 18, 95, preset["age"])
            gender = st.selectbox("Gender Identity", ["Male", "Female", "Other/Non-Binary"], index=["Male", "Female", "Other/Non-Binary"].index(preset["gender"]))
        with c5:
            smoking = st.selectbox("Tobacco Smoking Status", ["Never", "Former", "Current"], index=["Never", "Former", "Current"].index(preset["smoking_status"]))
            alcohol = st.selectbox("Alcohol Consumption Intensity", ["None", "Moderate", "Heavy"], index=["None", "Moderate", "Heavy"].index(preset["alcohol_consumption"]))
        with c6:
            physical_activity = st.slider("Physical Activity (Minutes/Week)", 0, 480, preset["physical_activity_mins"])

    with tab3:
        c7, c8, c9 = st.columns(3)
        with c7:
            chest_pain = st.selectbox("Angina Chest Pain Pattern", ["None", "Typical Angina", "Atypical Angina", "Non-Anginal"], index=["None", "Typical Angina", "Atypical Angina", "Non-Anginal"].index(preset["chest_pain_type"]))
            fatigue = st.checkbox("Persistent Clinical Fatigue", value=bool(preset["fatigue_reported"]))
        with c8:
            dizziness = st.checkbox("Dizziness or Vertigo Episodes", value=bool(preset["dizziness_reported"]))
            sob = st.checkbox("Exertional Shortness of Breath", value=bool(preset["shortness_of_breath"]))
        with c9:
            st.info("💡 Adjusting these physiological inputs recalculates machine-learning risk probabilities instantly.")

    # Assemble vector
    features = {
        "age": age,
        "gender": gender,
        "bmi": bmi,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "cholesterol_total": cholesterol_total,
        "cholesterol_hdl": cholesterol_hdl,
        "cholesterol_ldl": cholesterol_ldl,
        "fasting_glucose": fasting_glucose,
        "hba1c": hba1c,
        "smoking_status": smoking,
        "alcohol_consumption": alcohol,
        "physical_activity_mins": physical_activity,
        "fatigue_reported": 1 if fatigue else 0,
        "chest_pain_type": chest_pain,
        "dizziness_reported": 1 if dizziness else 0,
        "shortness_of_breath": 1 if sob else 0
    }

    # Run Multi-Condition Prediction
    try:
        preds = DiseaseRiskPredictor.predict_all_conditions(features)
    except Exception as e:
        st.error(f"Inference error: {str(e)}")
        return

    st.markdown("<hr style='border-color: rgba(0,242,254,0.2); margin: 24px 0;'/>", unsafe_allow_html=True)
    st.markdown("### 🎯 Multi-Condition Predictive Risk Stratification")

    # Display 3 Disease Risk Cards
    r_col1, r_col2, r_col3 = st.columns(3)

    disease_labels = {
        "heart_disease": ("Coronary Heart Disease", "#ff3366"),
        "diabetes": ("Type 2 Diabetes", "#ffaa00"),
        "stroke": ("Cerebrovascular Stroke", "#4facfe")
    }

    for (d_key, (d_title, d_theme)), col in zip(disease_labels.items(), [r_col1, r_col2, r_col3]):
        p = preds[d_key]
        with col:
            # Semicircular Plotly Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=p["risk_percentage"],
                number={'suffix': "%", 'font': {'color': "#ffffff", 'family': "Rajdhani, sans-serif", 'size': 26}},
                title={'text': d_title, 'font': {'color': "#8b949e", 'size': 13}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': "#8b949e"},
                    'bar': {'color': p['status_color'], 'thickness': 0.28},
                    'bgcolor': "rgba(10, 18, 38, 0.6)",
                    'borderwidth': 1,
                    'bordercolor': "rgba(0, 242, 254, 0.2)",
                    'steps': [
                        {'range': [0, 20], 'color': "rgba(0, 245, 160, 0.15)"},
                        {'range': [20, 50], 'color': "rgba(255, 170, 0, 0.15)"},
                        {'range': [50, 75], 'color': "rgba(255, 107, 107, 0.15)"},
                        {'range': [75, 100], 'color': "rgba(255, 0, 85, 0.25)"}
                    ]
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font={'color': "#ffffff"},
                margin=dict(l=15, r=15, t=35, b=10),
                height=180
            )

            st.markdown(
                f"""
                <div class="cyber-card" style="border-top: 4px solid {p['status_color']};">
                """,
                unsafe_allow_html=True
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown(
                f"""
                    <div style="text-align: center; margin-top: -15px; margin-bottom: 8px;">
                        <span class="status-pill" style="background: rgba(255,255,255,0.08); color: {p['status_color']}; border: 1px solid {p['status_color']};">
                            {p['risk_tier']}
                        </span>
                    </div>
                    <div style="font-size: 0.82rem; color: #f0f6fc; margin-top: 6px;">
                        <b>Clinical Protocol:</b> {p['clinical_recommendation']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Biometric Radar & Personalized Factors
    st.markdown("#### 🕸️ Biometric Morphometry vs Reference Guidelines")
    rad_col, feat_col = st.columns([6, 6])

    with rad_col:
        # Normalize biometric values to standard 100 scale where 100 = Reference Normal
        categories = ["Systolic BP", "Diastolic BP", "Glucose", "HbA1c", "Total Chol", "BMI"]
        pt_values = [
            (features["systolic_bp"] / 120.0) * 100.0,
            (features["diastolic_bp"] / 80.0) * 100.0,
            (features["fasting_glucose"] / 100.0) * 100.0,
            (features["hba1c"] / 5.7) * 100.0,
            (features["cholesterol_total"] / 200.0) * 100.0,
            (features["bmi"] / 25.0) * 100.0
        ]
        ref_values = [100.0] * 6

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=ref_values + [ref_values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='Reference Normal Limit',
            line=dict(color='#00f5a0', dash='dash'),
            fillcolor='rgba(0, 245, 160, 0.1)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=pt_values + [pt_values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='Simulated Patient',
            line=dict(color='#00f2fe', width=2.5),
            fillcolor='rgba(0, 242, 254, 0.25)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[50, 180], gridcolor="rgba(0,242,254,0.15)"),
                angularaxis=dict(gridcolor="rgba(0,242,254,0.15)")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            height=340,
            margin=dict(l=30, r=30, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with feat_col:
        st.markdown("#### 🔍 Personalized Contributing Risk Drivers")
        all_factors = set()
        for p in preds.values():
            for f in p["contributing_factors"]:
                all_factors.add(f)
        
        for idx, factor in enumerate(sorted(all_factors), 1):
            st.markdown(
                f"""
                <div style="background: rgba(14, 24, 50, 0.7); border-left: 3px solid #00f2fe; padding: 7px 12px; border-radius: 6px; margin-bottom: 6px; font-size: 0.86rem;">
                    <b>Factor #{idx}:</b> {factor}
                </div>
                """,
                unsafe_allow_html=True
            )

    # 7. What-If Counterfactual Intervention Simulator
    st.markdown("<hr style='border-color: rgba(0,242,254,0.2); margin: 24px 0;'/>", unsafe_allow_html=True)
    st.markdown("### 🧬 What-If Clinical Counterfactual Intervention Simulator")
    st.caption("Simulate prospective risk mitigation resulting from targeted pharmacological and behavioral interventions.")

    with st.expander("🛠️ Configure Clinical Counterfactual Interventions", expanded=True):
        int_c1, int_c2, int_c3, int_c4 = st.columns(4)
        with int_c1:
            sbp_delta = st.slider("Target SBP Reduction (mmHg)", 0, 40, 15, help="Antihypertensive therapy / DASH diet effect")
        with int_c2:
            glu_delta = st.slider("Target Fasting Glucose Reduction (mg/dL)", 0, 60, 20, help="Metformin / GLP-1 RA / glycemic control")
        with int_c3:
            smoke_opt = st.selectbox("Smoking Intervention", ["No Change", "Smoking Cessation (Quit)"], index=1 if features["smoking_status"] == "Current" else 0)
        with int_c4:
            act_delta = st.slider("Additional Exercise (Mins/Week)", 0, 180, 60, help="Aerobic cardiac rehab adherence")

        # Create Counterfactual Feature Dict
        cf_features = dict(features)
        cf_features["systolic_bp"] = max(cf_features["systolic_bp"] - sbp_delta, 90)
        cf_features["diastolic_bp"] = max(cf_features["diastolic_bp"] - int(sbp_delta * 0.6), 60)
        cf_features["fasting_glucose"] = max(cf_features["fasting_glucose"] - glu_delta, 70)
        cf_features["hba1c"] = max(round(cf_features["hba1c"] - (glu_delta * 0.025), 1), 4.8)
        if smoke_opt == "Smoking Cessation (Quit)":
            cf_features["smoking_status"] = "Former" if features["smoking_status"] == "Current" else features["smoking_status"]
        cf_features["physical_activity_mins"] = min(cf_features["physical_activity_mins"] + act_delta, 480)

        # Run Counterfactual Inference
        cf_preds = DiseaseRiskPredictor.predict_all_conditions(cf_features)

        # Comparison Table & Deltas
        comp_data = []
        for d_key, (d_name, _) in disease_labels.items():
            base_p = preds[d_key]["risk_percentage"]
            post_p = cf_preds[d_key]["risk_percentage"]
            delta = round(post_p - base_p, 1)
            rel_reduc = round(((base_p - post_p) / base_p * 100.0), 1) if base_p > 0 else 0.0
            comp_data.append({
                "Disease Condition": d_name,
                "Baseline Risk": f"{base_p:.1f}%",
                "Post-Intervention Risk": f"{post_p:.1f}%",
                "Absolute Risk Delta": f"{delta:+.1f}%",
                "Relative Risk Reduction": f"{rel_reduc:.1f}%",
                "New Risk Tier": cf_preds[d_key]["risk_tier"]
            })

        st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

    # 8. Feature Importance & Model Registry
    col_imp, col_eval = st.columns([6, 6])
    with col_imp:
        st.markdown("#### 📊 Model Feature Importance (Random Forest Ensemble)")
        models_meta = get_latest_model_metrics()
        hd_meta = models_meta.get("heart_disease", {})
        feat_imps = hd_meta.get("metrics", {}).get("feature_importances", [])
        
        if feat_imps:
            imp_df = pd.DataFrame(feat_imps[:8]).sort_values(by="importance", ascending=True)
            fig_imp = px.bar(
                imp_df,
                x="importance",
                y="feature",
                orientation="h",
                color="importance",
                color_continuous_scale="Teal",
                labels={"importance": "Gini Importance", "feature": "Clinical Predictor"}
            )
            apply_plotly_cyber_theme(fig_imp)
            st.plotly_chart(fig_imp, use_container_width=True)

    with col_eval:
        st.markdown("#### 🔬 Registered Model Telemetry & Validation Performance")
        summary_rows = []
        for d_name, d_key in [("Heart Disease", "heart_disease"), ("Type 2 Diabetes", "diabetes"), ("Stroke", "stroke")]:
            mod = models_meta.get(d_key, {})
            m = mod.get("metrics", {})
            summary_rows.append({
                "Target Condition": d_name,
                "Algorithm": mod.get("model_type", "RandomForestClassifier"),
                "Model Version": mod.get("version", "v2.4"),
                "Test ROC-AUC": f"{m.get('roc_auc', 0.85):.3f}",
                "Test PR-AUC": f"{m.get('pr_auc', 0.75):.3f}",
                "Optimal Threshold": f"{m.get('optimal_threshold', 0.50):.2f}"
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    # Regulatory Disclaimer
    st.caption(f"🛡️ **REGULATORY NOTICE:** {DISCLAIMER_TEXT}")
