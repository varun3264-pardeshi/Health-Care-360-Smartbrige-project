"""
Clinical Alert Center
Evidence-Based Threshold Flags, Follow-Up Tracking, Acknowledgement & Resolution Workflow
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from core.database import query_db, execute_db
from core.audit import log_audit_event, EVENT_ALERT_RESOLVED
from core.security import check_permission
from ui.components.kpi_card import render_kpi_card

def render():
    st.markdown("## 🚨 Clinical Alert Center & Automated Patient Surveillance")
    st.caption("Real-time automated surveillance flags detecting hypertensive crises, acute glycemic excursions, and multimorbidity clusters.")

    user = st.session_state.get("user", {})
    username = user.get("username", "anonymous")
    role = user.get("role", "Read-only Viewer")

    # 1. Alert Summary KPIs
    try:
        active_cnt = query_db("SELECT COUNT(*) as c FROM clinical_alerts WHERE status = 'ACTIVE'")[0]["c"]
        crit_cnt = query_db("SELECT COUNT(*) as c FROM clinical_alerts WHERE severity = 'CRITICAL' AND status = 'ACTIVE'")[0]["c"]
        high_cnt = query_db("SELECT COUNT(*) as c FROM clinical_alerts WHERE severity = 'HIGH' AND status = 'ACTIVE'")[0]["c"]
        ack_cnt = query_db("SELECT COUNT(*) as c FROM clinical_alerts WHERE status = 'ACKNOWLEDGED'")[0]["c"]
        res_cnt = query_db("SELECT COUNT(*) as c FROM clinical_alerts WHERE status = 'RESOLVED'")[0]["c"]
    except Exception:
        active_cnt, crit_cnt, high_cnt, ack_cnt, res_cnt = 0, 0, 0, 0, 0

    ak1, ak2, ak3, ak4, ak5 = st.columns(5)
    with ak1:
        render_kpi_card("Active Alerts", str(active_cnt), "Requires Surveillance", "critical" if active_cnt > 0 else "normal")
    with ak2:
        render_kpi_card("Critical Priority", str(crit_cnt), "Immediate Triage", "critical")
    with ak3:
        render_kpi_card("High Priority", str(high_cnt), "Physician Review", "high")
    with ak4:
        render_kpi_card("Acknowledged", str(ack_cnt), "Under Clinical Care", "info")
    with ak5:
        render_kpi_card("Resolved", str(res_cnt), "Closed Protocols", "normal")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. Filter & Search controls
    c_stat, c_sev, c_search = st.columns([3, 3, 4])
    with c_stat:
        status_filter = st.selectbox("Status Filter", ["ACTIVE", "ACKNOWLEDGED", "RESOLVED", "ALL"], index=0)
    with c_sev:
        severity_filter = st.selectbox("Severity Filter", ["ALL", "CRITICAL", "HIGH", "MEDIUM"], index=0)
    from core.security import sanitize_user_input
    with c_search:
        raw_search = st.text_input("🔍 Search Patient ID or Rule Code (WAF Protected)", "").strip()
        search_pt, is_safe, threat_msg = sanitize_user_input(raw_search)
        if not is_safe:
            st.error(f"🛡️ WAF Blocked Malicious Input: {threat_msg}")
            search_pt = ""

    # Query DB
    query = "SELECT * FROM clinical_alerts"
    params = []
    conditions = []

    if status_filter != "ALL":
        conditions.append("status = ?")
        params.append(status_filter)

    if severity_filter != "ALL":
        conditions.append("severity = ?")
        params.append(severity_filter)

    if search_pt:
        conditions.append("(patient_id LIKE ? OR rule_code LIKE ?)")
        params.extend([f"%{search_pt}%", f"%{search_pt}%"])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id DESC LIMIT 25"
    alerts = query_db(query, tuple(params))

    st.markdown(f"**Showing Top {len(alerts)} Clinical Alerts (Live Clinical Surveillance)**")

    if not alerts:
        st.success("No clinical alerts matching current filters.")
        return

    can_manage = check_permission(role, "manage_alerts")

    for a in alerts:
        sev = a["severity"]
        border_color = "#ff0055" if sev == "CRITICAL" else ("#ffaa00" if sev == "HIGH" else "#4facfe")
        
        with st.container():
            st.markdown(
                f"""
                <div class="cyber-card" style="border-left: 5px solid {border_color}; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="status-pill" style="border: 1px solid {border_color}; color: {border_color}; margin-right: 8px;">
                                {sev}
                            </span>
                            <span style="font-weight: 700; color: #ffffff; font-size: 1.05rem;">
                                {a['title']} — Patient {a['patient_id']}
                            </span>
                        </div>
                        <div style="font-size: 0.8rem; color: #8b949e;">
                            Protocol: <b style="color:#00f2fe;">{a['rule_code']}</b> | Triggered: {a['created_at'][:19]}
                        </div>
                    </div>
                    <div style="font-size: 0.86rem; color: #cbd5e1; margin-top: 8px;">
                        {a['description']}
                    </div>
                    {f"<div style='font-size: 0.8rem; color: #00f5a0; margin-top: 6px;'><b>Resolution:</b> {a['resolution_notes']} (by {a['resolved_by']})</div>" if a['status'] == 'RESOLVED' else ''}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Action Buttons if alert is not resolved
            if a["status"] != "RESOLVED" and can_manage:
                b_ack, b_res, _ = st.columns([2, 3, 7])
                with b_ack:
                    if st.button("👁️ Acknowledge", key=f"ack_{a['id']}"):
                        execute_db(
                            "UPDATE clinical_alerts SET status = 'ACKNOWLEDGED', resolved_by = ? WHERE id = ?",
                            (username, a["id"])
                        )
                        log_audit_event(username, role, EVENT_ALERT_RESOLVED, f"alert/{a['id']}", "ACKNOWLEDGED")
                        st.rerun()

                with b_res:
                    with st.popover("✅ Resolve Alert"):
                        notes = st.text_input("Intervention / Clinical Action Notes", "Verified with attending physician. Medication adjusted.", key=f"notes_{a['id']}")
                        if st.button("Confirm Resolution", key=f"confirm_{a['id']}"):
                            execute_db(
                                "UPDATE clinical_alerts SET status = 'RESOLVED', resolved_by = ?, resolution_notes = ? WHERE id = ?",
                                (username, notes, a["id"])
                            )
                            log_audit_event(username, role, EVENT_ALERT_RESOLVED, f"alert/{a['id']}", "RESOLVED", {"notes": notes})
                            st.rerun()
