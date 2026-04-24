#!/usr/bin/env python3
"""
Punto di ingresso principale — avvia Flask + scheduler in background.
Stesso pattern di CompitAPP (wsgi.py).
"""
import os
import sys
import time
import threading
import schedule
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app import db, scanner, notifier
from app.api import create_app

NETWORK_RANGE = os.getenv("NETWORK_RANGE", "192.168.1.0/24")
SCAN_INTERVAL = int(os.getenv("SCAN_INTERVAL_HOURS", 1))
OFFLINE_THRESHOLD = int(os.getenv("OFFLINE_THRESHOLD_HOURS", 2))
FLASK_PORT = int(os.getenv("FLASK_PORT", 5004))
INGRESS_PATH = os.getenv("INGRESS_PATH", "")

def do_scan():
    print(f"[network-monitor] Scheduled scan at {time.strftime('%H:%M:%S')}")
    scanner.full_scan(NETWORK_RANGE, OFFLINE_THRESHOLD)

def do_daily_report():
    print(f"[network-monitor] Daily report at {time.strftime('%H:%M:%S')}")
    devices = db.get_all_devices()
    online = sum(1 for d in devices if d['online'])
    offline = len(devices) - online
    ip_changes = db.get_recent_ip_changes(hours=24)
    notifier.send_daily_report(online, offline, ip_changes)

def scheduler_loop():
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    print("=" * 50)
    print("[network-monitor] Network Monitor v1.0.0")
    print("=" * 50)
    print(f"[network-monitor] Network: {NETWORK_RANGE}")
    print(f"[network-monitor] Scan interval: every {SCAN_INTERVAL}h")
    print(f"[network-monitor] Offline threshold: {OFFLINE_THRESHOLD}h")
    print(f"[network-monitor] Ingress path: {INGRESS_PATH or '/'}")
    print(f"[network-monitor] Telegram: {'ON' if notifier.is_enabled() else 'OFF'}")
    print(f"[network-monitor] API Key: {'SET' if os.getenv('API_KEY') else 'NOT SET (insecure!)'}")
    print("=" * 50)

    db.init_db()

    # Scan iniziale
    print("[network-monitor] Running initial scan...")
    do_scan()

    # Scheduler in background
    schedule.every(SCAN_INTERVAL).hours.do(do_scan)
    schedule.every().day.at("08:00").do(do_daily_report)

    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()
    print("[network-monitor] Scheduler started.")

    # Flask
    app = create_app(ingress_path=INGRESS_PATH)
    print(f"[network-monitor] Web server on http://0.0.0.0:{FLASK_PORT}")
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()
