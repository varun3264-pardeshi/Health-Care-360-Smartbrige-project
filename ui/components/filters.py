"""
PulsePoint Cyber-Medical Intelligence System
Global Multi-Parameter Cohort Filter Component
"""

import streamlit as st
import pandas as pd
from typing import Tuple, Dict, Any

def render_global_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Renders the responsive cyber-medical global filtering panel.
    Returns the filtered DataFrame and a dictionary of active filter criteria.
    """
    with st.expander("🔍 GLOBAL COHORT FILTERS & SURVEILLANCE PARAMETERS", expanded=False):
        c1, c2, c3, c4, c5 = st.columns([2.5, 2, 2, 2, 1.5])

        with c1:
            age_range = st.slider(
                "Age Cohort Interval",
                min_value=18,
                max_value=89,
                value=(18, 89),
                help="Filter patient cohort by chronological age"
            )

        with c2:
            gender_options = ["All Genders"] + sorted(df["gender"].unique().tolist())
            selected_gender = st.selectbox("Gender Identity", gender_options, index=0)

        with c3:
            region_options = ["All Regions"] + sorted(df["region"].unique().tolist())
            selected_region = st.selectbox("Geographic Network", region_options, index=0)

        with c4:
            smoking_options = ["All Statuses"] + sorted(df["smoking_status"].unique().tolist())
            selected_smoking = st.selectbox("Tobacco History", smoking_options, index=0)

        with c5:
            disease_options = [
                "All Conditions",
                "Heart Disease",
                "Type 2 Diabetes",
                "Stroke",
                "Multimorbidity (2+)"
            ]
            selected_disease = st.selectbox("Disease Focus", disease_options, index=0)

        btn_c1, btn_c2 = st.columns([8, 2])
        with btn_c2:
            reset_clicked = st.button("↺ Reset Filters", use_container_width=True)

    # If reset clicked, restore defaults
    if reset_clicked:
        st.rerun()

    # Apply filters
    filtered_df = df.copy()

    # Age
    filtered_df = filtered_df[
        (filtered_df["age"] >= age_range[0]) & (filtered_df["age"] <= age_range[1])
    ]

    # Gender
    if selected_gender != "All Genders":
        filtered_df = filtered_df[filtered_df["gender"] == selected_gender]

    # Region
    if selected_region != "All Regions":
        filtered_df = filtered_df[filtered_df["region"] == selected_region]

    # Smoking
    if selected_smoking != "All Statuses":
        filtered_df = filtered_df[filtered_df["smoking_status"] == selected_smoking]

    # Disease
    if selected_disease == "Heart Disease":
        filtered_df = filtered_df[filtered_df["heart_disease"] == 1]
    elif selected_disease == "Type 2 Diabetes":
        filtered_df = filtered_df[filtered_df["diabetes"] == 1]
    elif selected_disease == "Stroke":
        filtered_df = filtered_df[filtered_df["stroke"] == 1]
    elif selected_disease == "Multimorbidity (2+)":
        filtered_df = filtered_df[filtered_df["multimorbidity_count"] >= 2]

    active_filters = {
        "age_min": age_range[0],
        "age_max": age_range[1],
        "gender": selected_gender,
        "region": selected_region,
        "smoking": selected_smoking,
        "disease_selected": selected_disease,
        "active_records_count": len(filtered_df),
        "total_records_count": len(df)
    }

    # Dynamic filter status indicator
    if len(filtered_df) < len(df):
        st.markdown(
            f"""
            <div style="font-size: 0.8rem; color: #4facfe; margin-bottom: 12px; background: rgba(0, 242, 254, 0.08); padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(0, 242, 254, 0.2);">
                ⚡ Active Filter: Showing <b>{len(filtered_df):,}</b> of <b>{len(df):,}</b> cohort patients ({len(filtered_df)/len(df)*100:.1f}%)
            </div>
            """,
            unsafe_allow_html=True
        )

    return filtered_df, active_filters
