"""
Data Quality & Pipeline Auditor
Automated Validation Telemetry, Missingness Heatmaps, Duplicate Removal & Completeness Audits
"""

import json
import streamlit as st
import pandas as pd
import plotly.express as px
from core.database import query_db
from core.security import check_permission
from data_pipeline.exporter import generate_and_ingest_data
from ui.theme import apply_plotly_cyber_theme
from ui.components.kpi_card import render_kpi_card

def render(df: pd.DataFrame):
    st.markdown("## 🛡️ Data Quality & Pipeline Surveillance Auditor")
    st.caption("Automated schema validation, missingness detection, duplicate reconciliation, and physiological boundary clamping.")

    user = st.session_state.get("user", {})
    username = user.get("username", "anonymous")
    role = user.get("role", "Read-only Viewer")

    # Fetch latest quality run
    rows = query_db(
        """
        SELECT execution_timestamp, total_records, duplicate_count, missing_count,
               completeness_pct, quality_score, issues_json
        FROM data_quality_metrics
        ORDER BY id DESC LIMIT 1
        """
    )

    if not rows:
        st.warning("No data quality telemetry records found in database.")
        return

    q = rows[0]
    issues = json.loads(q["issues_json"])

    # Responsive Cyber KPI Row
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        render_kpi_card("Quality Score", f"{q['quality_score']:.1f} / 100", "Audited Rating", "normal")
    with k2:
        render_kpi_card("Total Ingested", f"{q['total_records']:,}", "Raw Rows", "info")
    with k3:
        render_kpi_card("Duplicates Dropped", f"{q['duplicate_count']:,}", "Resolved", "high")
    with k4:
        render_kpi_card("Imputed Cells", f"{q['missing_count']:,}", "Median / Mode", "info")
    with k5:
        render_kpi_card("Completeness", f"{q['completeness_pct']:.1f}%", "Cohort Score", "normal")

    st.markdown("<hr style='border-color: rgba(0,242,254,0.18); margin: 20px 0;'/>", unsafe_allow_html=True)

    # Column-by-Column Completeness
    c_chart, c_issues = st.columns([6, 6])

    with c_chart:
        st.markdown("#### 📊 Attribute Data Completeness (%)")
        comp_data = []
        for col in df.columns:
            pct = (1.0 - (df[col].isnull().sum() / len(df))) * 100.0
            comp_data.append({"Column": col, "Completeness": pct})
        
        comp_df = pd.DataFrame(comp_data).sort_values(by="Completeness", ascending=True)
        fig_comp = px.bar(
            comp_df.tail(15), # Top 15 core attributes
            x="Completeness",
            y="Column",
            orientation="h",
            color="Completeness",
            color_continuous_scale="Teal",
            range_x=[90, 100]
        )
        apply_plotly_cyber_theme(fig_comp)
        st.plotly_chart(fig_comp, use_container_width=True)

    with c_issues:
        st.markdown("#### ⚠️ Pipeline Audit Log & Issue Resolutions")
        for i, issue in enumerate(issues, 1):
            st.markdown(
                f"""
                <div style="background: rgba(16, 26, 54, 0.6); padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid #00f2fe; font-size: 0.85rem;">
                    <b>Event #{i}:</b> {issue}
                </div>
                """,
                unsafe_allow_html=True
            )

    # Re-run Pipeline Button (Admin and Analyst only)
    if check_permission(role, "train_models"):
        st.markdown("<hr style='border-color: rgba(0,242,254,0.18); margin: 20px 0;'/>", unsafe_allow_html=True)
        st.markdown("#### ⚙️ Data Pipeline Administrative Re-Ingestion")
        if st.button("🔄 Execute Fresh Ingestion, Validation & Quality Audit"):
            with st.spinner("Generating fresh cohort, enforcing clinical bounds, and updating SQLite..."):
                new_df, new_metrics = generate_and_ingest_data()
                st.success(f"Pipeline executed successfully. Fresh cohort: {len(new_df)} rows, Quality Score: {new_metrics['quality_score']}.")
                st.rerun()
