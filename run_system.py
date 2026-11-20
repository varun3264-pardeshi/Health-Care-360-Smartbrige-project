"""
PulsePoint Cyber-Medical Intelligence System
Unified Service Orchestrator & Launcher
"""

import sys
import os
import subprocess
import time
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run_api(host: str = "127.0.0.1", port: int = 8000):
    """Launches the FastAPI backend server."""
    cmd = [
        sys.executable, "-m", "uvicorn", "api.main:app",
        "--host", host,
        "--port", str(port),
        "--log-level", "info"
    ]
    print(f"\n[PulsePoint API] Launching FastAPI server on http://{host}:{port} ...")
    return subprocess.Popen(cmd, cwd=str(BASE_DIR))


def run_ui(port: int = 8501):
    """Launches the Streamlit cyber-medical dashboard companion."""
    cmd = [
        sys.executable, "-m", "streamlit", "run", "ui/app.py",
        "--server.port", str(port),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    print(f"\n[PulsePoint UI] Launching Cyber-Medical Dashboard on http://localhost:{port} ...")
    return subprocess.Popen(cmd, cwd=str(BASE_DIR))


def main():
    parser = argparse.ArgumentParser(description="PulsePoint Healthcare Intelligence Orchestrator")
    parser.add_argument("--mode", choices=["all", "ui", "api"], default="all", help="Service execution mode")
    parser.add_argument("--api-port", type=int, default=8000, help="Port for FastAPI backend")
    parser.add_argument("--ui-port", type=int, default=8501, help="Port for Streamlit UI")
    args = parser.parse_args()

    processes = []
    print("=" * 70)
    print("  PULSEPOINT CYBER-MEDICAL INTELLIGENCE SYSTEM")
    print("  Multi-Condition Chronic Disease Surveillance & Decision Support")
    print("=" * 70)

    try:
        if args.mode in ["all", "api"]:
            p_api = run_api(port=args.api_port)
            processes.append(p_api)
            time.sleep(2) # Give API a moment to bind

        if args.mode in ["all", "ui"]:
            p_ui = run_ui(port=args.ui_port)
            processes.append(p_ui)

        print("\n" + "=" * 70)
        print("  SERVICES RUNNING:")
        if args.mode in ["all", "ui"]:
            print(f"  * Cyber-Medical Dashboard:  http://localhost:{args.ui_port}")
        if args.mode in ["all", "api"]:
            print(f"  * REST API Documentation:   http://localhost:{args.api_port}/docs")
            print(f"  * Health Probe:             http://localhost:{args.api_port}/api/health")
        print("=" * 70)
        print("  Default Demo Credentials:")
        print("  - Clinician:     dr_chen        / Clinician@2026!")
        print("  - Administrator: admin          / Admin@2026!")
        print("  - Analyst:       analyst_sarah  / Analyst@2026!")
        print("  - Researcher:    researcher_alex/ Research@2026!")
        print("  - Viewer:        viewer_guest   / Viewer@2026!")
        print("=" * 70)
        print("  Press Ctrl+C to terminate all services.\n", flush=True)

        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\nShutting down PulsePoint services gracefully...")
        for p in processes:
            p.terminate()
            p.wait()
        print("All services stopped.")


if __name__ == "__main__":
    main()
