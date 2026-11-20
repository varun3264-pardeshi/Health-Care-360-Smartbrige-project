# PULSEPOINT CYBER-MEDICAL INTELLIGENCE — DEPLOYMENT GUIDE

## 1. Local Development Launch

### Quickstart (Single Command)
Execute the unified orchestrator to launch both the FastAPI REST backend and Streamlit dashboard companion:
```bash
python run_system.py --mode all
```

### Verified Local Endpoints
- **Cyber-Medical Command Center:** `http://localhost:8501`
- **FastAPI OpenAPI Documentation:** `http://localhost:8000/docs`
- **Health Verification Probe:** `http://localhost:8000/api/health`

---

## 2. Independent Service Execution

### Launching Streamlit Alone
```bash
streamlit run ui/app.py --server.port 8501
```

### Launching FastAPI Backend Alone
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 3. Production Deployment Hardening

1. **Environment Variables:**
   - Copy `.env.example` to `.env`.
   - Set `APP_ENV=production` and `DEBUG=false`.
   - Generate a high-entropy secret key:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Set `SECRET_KEY=<generated_value>`.

2. **Reverse Proxy Configuration (Nginx / Caddy):**
   - Terminate TLS/HTTPS at the reverse proxy with valid certificates.
   - Proxy `/api` traffic to `127.0.0.1:8000` and root traffic to `127.0.0.1:8501`.
   - Enable WebSocket upgrade headers (`Upgrade $http_upgrade`, `Connection "upgrade"`) for Streamlit's real-time communication socket.

3. **Database Migration to PostgreSQL:**
   - Change `DATABASE_URL` in `.env` to your PostgreSQL connection string:
     `postgresql://user:password@db-host:5432/healthcare_intelligence`
