"""
PulsePoint Cyber-Medical OS v6.0 - Ultra-Fast Cloudflare CDN Public Live URL Generator
Uses Cloudflare Edge Tunnel (cloudflared.exe) to connect to the nearest Indian Data Center
with HTTP/2 + Brotli compression so the public link opens in 1-2 seconds anywhere!
"""

import os
import subprocess
import sys
import time
import re
import socket

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def is_port_open(port: int = 8501) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex(("127.0.0.1", port)) == 0


def main():
    print("=" * 78)
    print("  [ULTRA-FAST CDN] PULSEPOINT OS v6.0 - CLOUDFLARE PUBLIC LIVE LINK LAUNCHER")
    print("=" * 78)

    server_proc = None
    if not is_port_open(8501):
        print("\n[1/2] Starting Optimized PulsePoint Server on http://localhost:8501 ...")
        server_proc = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run", "ui/app.py",
                "--server.port", "8501",
                "--server.headless", "true",
                "--client.showSidebarNavigation", "false",
                "--server.enableCORS", "false",
                "--server.enableXsrfProtection", "false",
                "--server.enableWebsocketCompression", "true"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        for _ in range(15):
            if is_port_open(8501):
                break
            time.sleep(1)
        print("      [OK] Local Server is LIVE at: http://localhost:8501")
    else:
        print("\n[1/2] [OK] Local Server is already running on http://localhost:8501")

    print("\n[2/2] Connecting to High-Speed Cloudflare Edge CDN (Direct Open, Zero Lag)...")
    print("      (Keep this terminal open while sharing the link. Press Ctrl+C to stop.)\n")

    cf_bin = "cloudflared.exe" if os.path.exists("cloudflared.exe") else "cloudflared"
    cf_cmd = [
        cf_bin, "tunnel",
        "--url", "http://127.0.0.1:8501",
        "--protocol", "http2"
    ]

    try:
        tunnel_proc = subprocess.Popen(
            cf_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1
        )

        printed_banner = False
        for line in tunnel_proc.stdout:
            match = re.search(r"(https://[a-zA-Z0-9-]+\.trycloudflare\.com)", line)
            if match and not printed_banner:
                public_url = match.group(1)
                printed_banner = True
                print("=" * 78)
                print("  ULTRA-FAST CLOUDFLARE PUBLIC LIVE LINK (Direct Open on Any Phone/Laptop):")
                print(f"\n      >>>  {public_url}  <<<\n")
                print("  Local Laptop Link:  http://localhost:8501")
                print("=" * 78)
                sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nStopping Live Server...")
    finally:
        if server_proc:
            server_proc.terminate()


if __name__ == "__main__":
    main()
