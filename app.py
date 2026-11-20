"""
SmartBridge Chronic Disease Risk Analysis & Tableau Intelligence Web Application
Main Web Server Launcher (app.py)
Serves the Interactive Web Application, 3 Clinical Scenarios (Dr. Michael Carter,
Emily Rodriguez, Dr. Priya Nair), Tableau Dashboards, Storyboard, and REST APIs.
"""

import uvicorn
from api.main import app

if __name__ == "__main__":
    print("=" * 72)
    print("  PULSEPOINT - SMARTBRIDGE CHRONIC DISEASE TABLEAU WEB APPLICATION")
    print("  Covering Heart Disease, Diabetes & Stroke across 3 Clinical Scenarios:")
    print("    1. Dr. Michael Carter  (Clinical Risk Assessment Officer)")
    print("    2. Emily Rodriguez     (Healthcare Data Analyst)")
    print("    3. Dr. Priya Nair      (Public Health Researcher)")
    print("-" * 72)
    print("  * Open Web Application in Browser: http://127.0.0.1:8000")
    print("  * Interactive API Docs:            http://127.0.0.1:8000/docs")
    print("=" * 72, flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
