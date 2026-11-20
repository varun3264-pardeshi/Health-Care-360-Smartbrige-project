# PULSEPOINT CYBER-MEDICAL INTELLIGENCE — SECURITY SPECIFICATION

## 1. Authentication & Cryptography

### 1.1 Password Hashing Architecture
All user authentication credentials stored within PulsePoint utilize **PBKDF2-HMAC-SHA256** with:
- **Salt:** 16-byte cryptographically secure pseudorandom salt generated via `os.urandom(16).hex()` per user.
- **Iterations:** 100,000 computation cycles, rendering offline rainbow-table and dictionary attacks computationally infeasible.
- **Verification:** Constant-time hash comparison via `hmac.compare_digest()` to eliminate timing-attack vulnerabilities.

### 1.2 Session & Token Security
- Cryptographically signed HMAC-SHA256 compact tokens with header, payload, and signature components.
- Token lifetime enforced via explicit `exp` claim (default 120 minutes).
- Invalid signatures, malformed payloads, or expired sessions are rejected with HTTP 401 Unauthorized.

---

## 2. Role-Based Access Control (RBAC) Matrix

Access permissions are enforced strictly server-side with **Deny by Default** architecture:

| Role | View Dashboards | View Patient 360 | Export Patient-Level | Export Aggregates | Manage Alerts | Train Models | View Audit Logs |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Administrator** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Authorized Clinician** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Healthcare Analyst** | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Researcher** | ✅ | ❌ | ❌ | ✅ (Masked) | ❌ | ❌ | ❌ |
| **Read-only Viewer** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 3. Application & Database Hardening

### 3.1 SQL Injection Prevention
- Zero dynamic string concatenation in database operations.
- 100% of SELECT, INSERT, UPDATE, and DELETE operations execute through parameterized query interfaces (`?` parameter markers) via `core/database.py`.

### 3.2 Input Validation & Boundary Enforcement
- Pydantic v2 data models enforce strict types, valid ranges, and enumerations on all API request payloads.
- Out-of-bounds biological measurements (e.g., negative ages, SBP > 260) are rejected or clamped to physiological limits.

### 3.3 CORS & Network Exposure
- Narrow CORS middleware restricted explicitly to `localhost:8501` (Streamlit companion) and `localhost:8000` (FastAPI backend).

---

## 4. Immutable Audit Trail

Every sensitive security event is recorded in the `audit_events` table:
- User login / logout
- Authentication failure events (with IP address)
- Protected patient 360 record lookups
- Data export actions (logging filter criteria and record volume)
- Clinical alert acknowledgement and resolution notes
- Automated sanitization via `sanitize_audit_details()` strips passwords, API keys, and tokens prior to persistence.
