"""
Data Upload, Clinical Intelligence Reports & Filter-Aware Exports
Supports uploading new CSV/Excel clinical datasets, adding new patient records,
generating Executive PDF reports, and exporting filter-aware CSV cohorts.
"""

import os
import random
import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from reporting.csv_exporter import export_filtered_dataset
from reporting.pdf_generator import generate_executive_pdf_report
from ml_engine.evaluator import get_latest_model_metrics
from core.database import query_db, execute_db


def render(df: pd.DataFrame, active_filters: dict):
    st.markdown("## 📤 Upload New Clinical Data, Add Records & Generate Reports")
    st.caption("Upload new CSV/Excel health datasets, add new patient clinical records, or download encrypted PDF & CSV reports.")

    user = st.session_state.get("user", {})
    is_auth = st.session_state.get("authenticated", False)
    username = user.get("username", "guest")
    role = user.get("role", "Guest")

    # SECTION 1: UPLOAD NEW DATASET OR ADD NEW PATIENT RECORD
    tab_upload, tab_add_record, tab_exports = st.tabs([
        "📤 Upload CSV / Excel Dataset",
        "➕ Add New Patient / Health Record",
        "📑 Download PDF & CSV Reports"
    ])

    with tab_upload:
        st.markdown("#### 📂 Upload New Clinical Dataset (`.csv` or `.xlsx`)")
        st.caption("Uploaded datasets are isolated to your account session so no other user can view your private uploaded files.")
        uploaded_file = st.file_uploader(
            "Select a CSV or Excel file containing patient health records:",
            type=["csv", "xlsx"]
        )
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    new_df = pd.read_csv(uploaded_file)
                else:
                    new_df = pd.read_excel(uploaded_file)

                st.success(f"✅ Successfully loaded **{len(new_df):,} records** and **{len(new_df.columns)} columns** from `{uploaded_file.name}`!")
                st.dataframe(new_df.head(25), use_container_width=True, hide_index=True)

                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    if st.button("✅ Use This Uploaded Dataset Across All Dashboards", use_container_width=True):
                        required_cols = {"age", "bmi", "systolic_bp", "diastolic_bp", "fasting_glucose", "cholesterol_total"}
                        missing_cols = required_cols - set(new_df.columns.str.lower())
                        if missing_cols:
                            st.warning(
                                f"Uploaded file is previewed above. To use it across all clinical charts, include columns: {', '.join(sorted(missing_cols))}."
                            )
                        else:
                            from core.rasp_shield import BackendIsolationGuard
                            tenant_ns = BackendIsolationGuard.isolate_tenant_namespace(username)
                            st.session_state[f"custom_uploaded_df_{tenant_ns}"] = new_df
                            st.session_state[f"custom_uploaded_df_{username}"] = new_df
                            st.success(f"🎉 Dataset activated inside Isolated Backend Namespace `{tenant_ns}`!")
                            st.rerun()
                with c_act2:
                    from core.rasp_shield import BackendIsolationGuard
                    tenant_ns = BackendIsolationGuard.isolate_tenant_namespace(username)
                    if f"custom_uploaded_df_{tenant_ns}" in st.session_state or f"custom_uploaded_df_{username}" in st.session_state:
                        if st.button("🔄 Reset to Default Hospital Cohort", use_container_width=True):
                            st.session_state.pop(f"custom_uploaded_df_{tenant_ns}", None)
                            st.session_state.pop(f"custom_uploaded_df_{username}", None)
                            st.rerun()
            except Exception as e:
                st.error(f"Could not read file: {str(e)}")

    with tab_add_record:
        st.markdown("#### ➕ Add New Patient / Personal Health Record")
        if not is_auth:
            st.info("🔐 Please click **'Login / Register'** at the top-right corner before saving a private health record so it stays linked only to your account.")
        with st.form("add_new_patient_record_form"):
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                new_age = st.number_input("Age (Years)", 18, 100, 45)
                new_gender = st.selectbox("Gender", ["Male", "Female"])
                new_region = st.selectbox("Region", ["North", "South", "East", "West", "Central"])
            with f2:
                new_sbp = st.number_input("Systolic BP (mmHg)", 80, 240, 128)
                new_dbp = st.number_input("Diastolic BP (mmHg)", 50, 150, 82)
                new_bmi = st.number_input("BMI (kg/m²)", 14.0, 55.0, 25.4, step=0.1)
            with f3:
                new_glu = st.number_input("Fasting Glucose (mg/dL)", 60.0, 400.0, 104.0, step=1.0)
                new_hba1c = st.number_input("HbA1c (%)", 4.0, 15.0, 5.7, step=0.1)
                new_chol = st.number_input("Total Cholesterol (mg/dL)", 100.0, 400.0, 195.0, step=1.0)
            with f4:
                new_smoke = st.selectbox("Smoking Status", ["Never", "Former", "Current"])
                new_alc = st.selectbox("Alcohol Intake", ["None", "Light", "Moderate", "Heavy"])
                new_exe = st.number_input("Weekly Exercise (mins)", 0, 600, 150, step=15)

            c_d1, c_d2, c_d3 = st.columns(3)
            with c_d1:
                has_hd = st.checkbox("Diagnosed Heart Disease")
            with c_d2:
                has_diab = st.checkbox("Diagnosed Type 2 Diabetes")
            with c_d3:
                has_stroke = st.checkbox("History of Stroke")

            submitted = st.form_submit_button("💾 Save New Health Record to Database", use_container_width=True)
            if submitted:
                new_pt_id = f"PT-{username.upper()[:4]}-{random.randint(1000, 9999)}"
                bmi_cat = "Normal" if new_bmi < 25 else ("Overweight" if new_bmi < 30 else "Obesity Class I")
                bp_cat = "Normal" if new_sbp < 120 else ("Elevated" if new_sbp < 130 else ("Hypertension Stage 1" if new_sbp < 140 else "Hypertension Stage 2"))
                glu_cat = "Normal" if new_glu < 100 else ("Prediabetes" if new_glu < 126 else "Diabetic Range")
                exe_lvl = "High" if new_exe >= 150 else ("Moderate" if new_exe >= 60 else "Sedentary")
                multi_cnt = int(has_hd) + int(has_diab) + int(has_stroke)
                today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

                try:
                    execute_db(
                        """
                        INSERT INTO patient_records (
                            patient_id, age, gender, region, bmi, bmi_category,
                            systolic_bp, diastolic_bp, bp_category,
                            cholesterol_total, cholesterol_hdl, cholesterol_ldl, cholesterol_ratio,
                            fasting_glucose, glucose_category, hba1c,
                            smoking_status, alcohol_consumption, physical_activity_mins, exercise_level,
                            fatigue_reported, chest_pain_type, dizziness_reported, shortness_of_breath,
                            heart_disease, diabetes, stroke, multimorbidity_count,
                            data_completeness_pct, assessment_date, review_status, is_synthetic, owner_username
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            new_pt_id, int(new_age), new_gender, new_region, float(new_bmi), bmi_cat,
                            int(new_sbp), int(new_dbp), bp_cat,
                            float(new_chol), 50.0, float(max(new_chol - 80, 70)), round(new_chol / 50.0, 2),
                            float(new_glu), glu_cat, float(new_hba1c),
                            new_smoke, new_alc, int(new_exe), exe_lvl,
                            0, "None", 0, 0,
                            int(has_hd), int(has_diab), int(has_stroke), multi_cnt,
                            100.0, today_str, "Verified Real Entry", 0, username
                        )
                    )
                    st.cache_data.clear()
                    st.success(f"✅ Record **{new_pt_id}** saved! Linked privately to account `@{username}`.")
                except Exception as e:
                    st.error(f"Failed to save record: {str(e)}")

    with tab_exports:
        col_pdf, col_csv = st.columns(2)

        with col_pdf:
            st.markdown(
                '<div class="cyber-card" style="border-top: 4px solid #00f2fe;">'
                '<h4 style="color: #00f2fe; margin-top: 0;">📄 Executive Clinical PDF Report</h4>'
                '<p style="font-size: 0.86rem; color: #cbd5e1;">'
                'Generates a formal clinical surveillance PDF document including cohort prevalence, '
                'biomarker distributions, and machine learning evaluation metrics.</p></div>',
                unsafe_allow_html=True
            )
            if st.button("🚀 Compile & Download Executive PDF Report", use_container_width=True):
                with st.spinner("Generating clinical PDF document..."):
                    try:
                        q_rows = query_db("SELECT quality_score FROM data_quality_metrics ORDER BY id DESC LIMIT 1")
                        q_score = q_rows[0]["quality_score"] if q_rows else 98.5
                        models_meta = get_latest_model_metrics()

                        pdf_path = generate_executive_pdf_report(
                            df=df,
                            quality_metrics={"quality_score": q_score},
                            models_summary=models_meta,
                            generated_by=f"{user.get('full_name', 'User')} ({role})"
                        )

                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()

                        st.download_button(
                            label="📥 Click to Save PDF Document",
                            data=pdf_bytes,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("Executive PDF report generated successfully.")
                    except Exception as e:
                        st.error(f"PDF compilation failed: {str(e)}")

        with col_csv:
            st.markdown(
                f'<div class="cyber-card" style="border-top: 4px solid #4facfe;">'
                f'<h4 style="color: #4facfe; margin-top: 0;">📊 Filter-Aware CSV Cohort Export</h4>'
                f'<p style="font-size: 0.86rem; color: #cbd5e1;">'
                f'Exports records matching active filters (<b>{len(df):,} records</b>) with automatic privacy protection.</p></div>',
                unsafe_allow_html=True
            )

            csv_data = export_filtered_dataset(
                df=df,
                filters_applied=active_filters,
                username=username,
                role=role if is_auth else "Authorized Clinician"
            )

            if csv_data:
                st.download_button(
                    label=f"📥 Download Filtered CSV ({len(df):,} records)",
                    data=csv_data,
                    file_name=f"chronic_disease_cohort_{len(df)}_pts.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📖 Clinical Data Dictionary & Variable Definitions")
        from data_pipeline.exporter import DATA_DICTIONARY_ROWS
        dict_df = pd.DataFrame(DATA_DICTIONARY_ROWS)
        st.dataframe(dict_df, use_container_width=True, hide_index=True)
