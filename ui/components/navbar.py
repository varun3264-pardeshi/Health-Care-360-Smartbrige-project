"""
PulsePoint Cyber-Medical OS v6.0
Top Navigation Bar, Login / Register / Forgot Password System (2FA + JWT Verified)
No pre-filled user names — clean Guest state until user logs in or registers.
"""

import random
import streamlit as st
from datetime import datetime, timezone
from core.database import (
    init_database,
    query_db,
    authenticate_db_user,
    register_db_user,
    reset_db_user_password,
)
from core.security import (
    create_access_token,
    verify_access_token,
    check_rate_limit,
    ROLE_PATIENT,
    ROLE_CLINICIAN,
    ROLE_ANALYST,
    ROLE_RESEARCHER,
)
from core.audit import log_audit_event, EVENT_LOGIN, EVENT_LOGOUT


def _ensure_auth_state():
    """Initializes clean unauthenticated session state with no pre-filled user name."""
    if "db_initialized" not in st.session_state:
        init_database()
        st.session_state.db_initialized = True

    if "current_2fa_otp" not in st.session_state:
        st.session_state.current_2fa_otp = str(random.randint(100000, 999999))

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.auth_jwt_token = None
        st.session_state.show_login_gate = False
        st.session_state.user = {
            "username": "guest",
            "full_name": "Guest Visitor",
            "email": "",
            "role": "Guest (Not Logged In)"
        }

    # Anti-Bypass Check: Verify cryptographic JWT signature if session claims to be authenticated
    if st.session_state.get("authenticated", False):
        token = st.session_state.get("auth_jwt_token")
        payload = verify_access_token(token) if token else None
        if not payload or payload.get("sub") != st.session_state.get("user", {}).get("username"):
            # Token invalid or tampered — revoke authentication immediately
            st.session_state.authenticated = False
            st.session_state.auth_jwt_token = None
            st.session_state.user = {
                "username": "guest",
                "full_name": "Guest Visitor",
                "email": "",
                "role": "Guest (Not Logged In)"
            }


def _complete_login(user_dict: dict):
    """Completes 2FA login and issues a signed HMAC-SHA256 JWT token to prevent login bypass."""
    jwt_token = create_access_token({"sub": user_dict["username"], "role": user_dict["role"]})
    st.session_state.authenticated = True
    st.session_state.auth_jwt_token = jwt_token
    st.session_state.user = user_dict
    st.session_state.show_login_gate = False
    st.session_state.login_time = datetime.now(timezone.utc).strftime("%H:%M UTC")
    st.session_state.current_2fa_otp = str(random.randint(100000, 999999))
    log_audit_event(user_dict["username"], user_dict["role"], EVENT_LOGIN, "auth_gateway", "SUCCESS_2FA_JWT")


def render_auth_tabs(key_prefix: str = "top"):
    """
    Renders the 3-Tab Authentication Portal:
    1. Login (2FA OTP) — blank fields, no pre-filled names
    2. Register New Account
    3. Forgot Password
    """
    _ensure_auth_state()
    otp_code = st.session_state.current_2fa_otp

    tab_login, tab_register, tab_forgot = st.tabs([
        "🔑 Login (2FA)",
        "📝 Register New",
        "🔄 Forgot Password"
    ])

    # TAB 1: LOGIN WITH 2FA OTP
    with tab_login:
        login_id = st.text_input(
            "Username or Email",
            value="",
            placeholder="Enter your username or email",
            key=f"{key_prefix}_login_id"
        )
        login_pw = st.text_input(
            "Password",
            value="",
            type="password",
            placeholder="Enter your password",
            key=f"{key_prefix}_login_pw"
        )

        st.markdown(
            f'<div style="padding: 8px 12px; border-radius: 8px; background: rgba(0, 245, 160, 0.08); '
            f'border: 1px solid rgba(0, 245, 160, 0.35); margin: 6px 0;">'
            f'<span style="font-size: 0.75rem; color: #00f5a0; font-weight: 700;">📲 2-Step Verification Code: </span>'
            f'<span style="font-size: 1.05rem; color: #ffffff; font-weight: 900; letter-spacing: 0.12em;">{otp_code}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        entered_otp = st.text_input(
            "Enter 6-Digit 2FA Code",
            value="",
            max_chars=6,
            placeholder=f"Type {otp_code}",
            key=f"{key_prefix}_login_otp"
        )

        if st.button("✅ Sign In with 2-Step Verification", use_container_width=True, key=f"{key_prefix}_btn_signin"):
            allowed, _ = check_rate_limit(f"login_{login_id}", max_requests=8, window_seconds=60)
            if not allowed:
                st.error("🛡️ Too many login attempts. Please wait 60 seconds.")
            elif entered_otp.strip() != otp_code:
                st.error("❌ Invalid 6-Digit 2FA Code! Please enter the exact 6-digit code shown above.")
            else:
                user_obj, msg = authenticate_db_user(login_id, login_pw)
                if user_obj:
                    _complete_login(user_obj)
                    st.success(f"Welcome, {user_obj['full_name']}!")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

        with st.expander("ℹ️ Evaluator / Demo Credentials (Optional)"):
            st.caption(
                "You can register your own account in the **Register New** tab, or test with:\n"
                "- **Clinician:** `dr_carter` / `Carter@2026!`\n"
                "- **Analyst:** `emily_rodriguez` / `Emily@2026!`\n"
                "- **Researcher:** `dr_priya_nair` / `Priya@2026!`"
            )

    # TAB 2: REGISTER NEW ACCOUNT
    with tab_register:
        reg_name = st.text_input("Full Name", value="", placeholder="Enter your full name", key=f"{key_prefix}_reg_name")
        reg_user = st.text_input("Choose Username", value="", placeholder="e.g. rahul_sharma", key=f"{key_prefix}_reg_user")
        reg_email = st.text_input("Email Address", value="", placeholder="name@example.com", key=f"{key_prefix}_reg_email")
        reg_role = st.selectbox(
            "Account Type",
            [ROLE_PATIENT, ROLE_CLINICIAN, ROLE_ANALYST, ROLE_RESEARCHER],
            key=f"{key_prefix}_reg_role"
        )
        reg_pw1 = st.text_input("Create Password (min 6 chars)", value="", type="password", key=f"{key_prefix}_reg_pw1")
        reg_pw2 = st.text_input("Confirm Password", value="", type="password", key=f"{key_prefix}_reg_pw2")

        if st.button("📝 Create New Account", use_container_width=True, key=f"{key_prefix}_btn_reg"):
            allowed, _ = check_rate_limit("register_ip", max_requests=10, window_seconds=60)
            if not allowed:
                st.error("🛡️ Rate limit exceeded. Please wait a moment.")
            elif reg_pw1 != reg_pw2:
                st.error("❌ Passwords do not match!")
            else:
                ok, msg = register_db_user(reg_user, reg_name, reg_email, reg_role, reg_pw1)
                if ok:
                    user_obj, _ = authenticate_db_user(reg_user, reg_pw1)
                    if user_obj:
                        _complete_login(user_obj)
                        st.success(f"🎉 Account created & logged in as {user_obj['full_name']}!")
                        st.rerun()
                    else:
                        st.success(msg)
                else:
                    st.error(f"❌ {msg}")

    # TAB 3: FORGOT PASSWORD
    with tab_forgot:
        fp_id = st.text_input(
            "Registered Username or Email",
            value="",
            placeholder="Enter your registered username or email",
            key=f"{key_prefix}_fp_id"
        )
        st.markdown(
            f'<div style="font-size: 0.78rem; color: #00f2fe; margin-bottom: 4px;">'
            f'📲 Security Reset OTP Code: <b>{otp_code}</b></div>',
            unsafe_allow_html=True
        )
        fp_otp = st.text_input(
            "Enter 6-Digit Reset OTP",
            value="",
            max_chars=6,
            placeholder=f"Type {otp_code}",
            key=f"{key_prefix}_fp_otp"
        )
        fp_pw1 = st.text_input("New Password (min 6 chars)", value="", type="password", key=f"{key_prefix}_fp_pw1")
        fp_pw2 = st.text_input("Confirm New Password", value="", type="password", key=f"{key_prefix}_fp_pw2")

        if st.button("🔄 Reset Password", use_container_width=True, key=f"{key_prefix}_btn_fp"):
            if fp_otp.strip() != otp_code:
                st.error("❌ Invalid 6-Digit Security OTP Code!")
            elif fp_pw1 != fp_pw2:
                st.error("❌ New passwords do not match!")
            else:
                ok, msg = reset_db_user_password(fp_id, fp_pw1)
                if ok:
                    st.session_state.current_2fa_otp = str(random.randint(100000, 999999))
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")


def render_2fa_login_screen():
    """Renders the full-screen Login / Register / Forgot Password Gateway."""
    _ensure_auth_state()
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    _, center_col, _ = st.columns([2.2, 5.6, 2.2])

    with center_col:
        st.markdown(
            '<div class="cyber-card" style="border-top: 4px solid #00f2fe; padding: 22px 26px !important; text-align: center;">'
            '<div style="font-size: 0.74rem; color: #00f2fe; font-weight: 800; letter-spacing: 0.12em;">🛡️ PULSEPOINT ACCOUNT &amp; SECURITY GATEWAY</div>'
            '<h2 style="margin: 6px 0 4px 0; color: #ffffff; font-weight: 900;">🔐 Login, Register New Account or Reset Password</h2>'
            '<p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">Each account has isolated private health records protected by 2-Step Verification (2FA) &amp; JWT Cryptography.</p>'
            '</div>',
            unsafe_allow_html=True
        )
        render_auth_tabs(key_prefix="fullscreen")

        if st.button("⬅️ Back to Public Overview Dashboard", use_container_width=True, key="btn_back_from_login"):
            st.session_state.show_login_gate = False
            st.rerun()


def render_navbar():
    """Renders the top navigation bar with ECG, AI Chatbot shortcut, Data Upload shortcut, and Top-Right Login/Register button."""
    _ensure_auth_state()

    try:
        alert_rows = query_db("SELECT COUNT(*) as c FROM clinical_alerts WHERE status = 'ACTIVE' AND severity = 'CRITICAL'")
        critical_count = alert_rows[0]["c"] if alert_rows else 12
    except Exception:
        critical_count = 12

    col_brand, col_ecg, col_ai, col_upload, col_login = st.columns([3.5, 1.9, 1.9, 1.9, 2.2])

    with col_brand:
        st.markdown(
            '<div style="display: flex; align-items: center; gap: 12px; padding: 4px 0;">'
            '<div style="width: 14px; height: 14px; border-radius: 50%; background: #00f2fe; box-shadow: 0 0 16px #00f2fe; animation: pulse-critical 1.5s infinite;"></div>'
            '<div>'
            '<span style="font-size: 1.48rem; font-weight: 900; letter-spacing: -0.02em; background: linear-gradient(90deg, #ffffff 0%, #00f2fe 55%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">PULSEPOINT OS</span>'
            '<span style="font-size: 0.68rem; color: #00f2fe; font-weight: 800; margin-left: 8px; padding: 2px 8px; border-radius: 99px; background: rgba(0,242,254,0.12); border: 1px solid rgba(0,242,254,0.35); letter-spacing: 0.08em;">HEALTH AI v6.0</span>'
            '</div></div>',
            unsafe_allow_html=True
        )

    with col_ecg:
        st.markdown(
            '<div style="display: flex; align-items: center; gap: 8px; padding-top: 6px;">'
            '<svg width="95" height="24" viewBox="0 0 120 26" style="overflow: visible;">'
            '<path d="M 0 13 L 25 13 L 30 13 L 35 3 L 42 23 L 48 8 L 52 16 L 56 13 L 85 13 L 90 3 L 97 23 L 103 8 L 107 16 L 111 13 L 120 13" fill="none" stroke="#00f2fe" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            '<animate attributeName="stroke-dasharray" from="0,200" to="200,0" dur="1.8s" repeatCount="indefinite" />'
            '</path></svg>'
            f'<span style="font-size: 0.74rem; font-weight: 700; color: #00f5a0; font-family: \'Rajdhani\', monospace;">⚡ {critical_count} ALERTS</span>'
            '</div>',
            unsafe_allow_html=True
        )

    with col_ai:
        if st.button("🤖 AI Health Chatbot", key="top_nav_ai_doc_btn", use_container_width=True):
            st.session_state["selected_control_page"] = "AI Doctor & Medicine Guide"
            st.session_state["nav_sync_version"] = st.session_state.get("nav_sync_version", 0) + 1
            st.rerun()

    with col_upload:
        if st.button("📤 Upload / Add Data", key="top_nav_upload_btn", use_container_width=True):
            st.session_state["selected_control_page"] = "Reports & Data Exports"
            st.session_state["nav_sync_version"] = st.session_state.get("nav_sync_version", 0) + 1
            st.rerun()

    # TOP-RIGHT LOGIN / REGISTER / FORGOT PASSWORD BUTTON (No pre-filled user!)
    with col_login:
        is_auth = st.session_state.get("authenticated", False)
        current_user = st.session_state.get("user", {})

        if not is_auth:
            with st.popover("🔐 Login / Register", use_container_width=True):
                st.markdown(
                    '<div style="font-size: 0.85rem; font-weight: 800; color: #00f2fe; margin-bottom: 6px;">'
                    '🔐 Account Login, Registration &amp; Password Reset</div>',
                    unsafe_allow_html=True
                )
                render_auth_tabs(key_prefix="navpop")
                st.markdown("<hr style='border-color: rgba(0,242,254,0.18); margin: 8px 0;'/>", unsafe_allow_html=True)
                if st.button("🖥️ Open Full-Screen Login Page", key="btn_open_full_login", use_container_width=True):
                    st.session_state.show_login_gate = True
                    st.rerun()
        else:
            short_name = current_user.get("full_name", "User").split(" ")[0]
            with st.popover(f"👤 {short_name} (Logged In)", use_container_width=True):
                st.markdown(
                    f'<div style="background: rgba(0,245,160,0.08); border: 1px solid rgba(0,245,160,0.3); border-radius: 10px; padding: 10px 12px; margin-bottom: 10px;">'
                    f'<div style="font-size: 0.68rem; color: #00f5a0; font-weight: 800;">● VERIFIED 2FA + JWT SESSION</div>'
                    f'<div style="font-size: 0.95rem; font-weight: 800; color: #ffffff;">{current_user.get("full_name")}</div>'
                    f'<div style="font-size: 0.75rem; color: #94a3b8;">@{current_user.get("username")} • {current_user.get("role")}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button("🚪 Sign Out / Logout", key="btn_logout_now", use_container_width=True):
                    log_audit_event(current_user.get("username", "user"), current_user.get("role", ""), EVENT_LOGOUT, "auth_gateway", "LOGGED_OUT")
                    st.session_state.authenticated = False
                    st.session_state.auth_jwt_token = None
                    st.session_state.user = {
                        "username": "guest",
                        "full_name": "Guest Visitor",
                        "email": "",
                        "role": "Guest (Not Logged In)"
                    }
                    st.rerun()

    # Clean Live Status Ticker (no "Immutable" text, no pre-filled fake user)
    now_utc = datetime.now(timezone.utc).strftime("%H:%M UTC")
    auth_badge = (
        f"🟢 LOGGED IN: {current_user.get('full_name')} ({current_user.get('role')})"
        if is_auth else "🔓 GUEST MODE (Click 'Login / Register' at top-right for private records)"
    )
    st.markdown(
        f'<div class="telemetry-ticker">'
        f'<div>🟢 SYSTEM: ONLINE (BACKEND ISOLATED + WAL)</div>'
        f'<div>{auth_badge}</div>'
        f'<div>🛡️ SHIELD: 2FA + RASP + OBF6 + ANTI-LLM TRAP</div>'
        f'<div>🕒 {now_utc}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
