#!/usr/bin/env python3
import os
import sys
import time
import schedule
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app import db, scanner, notifier, api

def main():
    db.init_db()
    app = api.create_app()

    network_range = os.getenv("NETWORK_RANGE", "192.168.1.0/24")
    scan_interval = int(os.getenv("SCAN_INTERVAL_HOURS", 1))
    api_key = os.getenv("API_KEY", "")

    print("\n" + "="*50)
    print("🚀 Network Monitor - Home Assistant Addon")
    print("="*50)
    print(f"📍 Network range: {network_range}")
    print(f"🔄 Scan interval: every {scan_interval} hour(s)")
    print(f"🔐 API Key: {'SET' if api_key else 'NOT SET (insecure!)'}")
    print(f"📱 Telegram: {'Enabled' if notifier.is_enabled() else 'Disabled'}")
    print("="*50 + "\n")

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "scan":
            print("[*] Manual scan...")
            changes = scanner.full_scan(network_range)
            for change in changes:
                if change['changed']:
                    print(f"[+] {change['mac']} -> {change['ip']}")

        elif cmd == "report":
            print("[*] Generating report...")
            devices = db.get_all_devices()
            online = sum(1 for d in devices if d['online'])
            offline = len(devices) - online
            notifier.send_daily_report(online, offline, [])

    else:
        # Avvia lo scheduler in background
        print("[*] Starting background scheduler...")

        def do_scan():
            print(f"\n[*] Scheduled scan at {time.strftime('%H:%M:%S')}")
            changes = scanner.full_scan(network_range)
            for change in changes:
                if change['changed']:
                    print(f"[+] IP change: {change['mac']} -> {change['ip']}")

        def do_report():
            print(f"\n[*] Daily report at {time.strftime('%H:%M:%S')}")
            devices = db.get_all_devices()
            online = sum(1 for d in devices if d['online'])
            offline = len(devices) - online
            notifier.send_daily_report(online, offline, [])

        schedule.every(scan_interval).hours.do(do_scan)
        schedule.every().day.at("08:00").do(do_report)

        # Esegui una scansione iniziale
        print("[*] Initial scan...")
        do_scan()

        # Avvia Flask in un thread
        from threading import Thread
        scheduler_thread = Thread(target=lambda: (
            print("[*] Scheduler running..."),
            [schedule.run_pending() or time.sleep(60) for _ in iter(int, 1)]
        ), daemon=True)
        scheduler_thread.start()

        port = int(os.getenv("FLASK_PORT", 5000))
        debug = os.getenv("DEBUG", "false").lower() == "true"
        print(f"\n[+] Starting web server on http://0.0.0.0:{port}")
        print("[+] Use X-API-Key header for authentication\n")

        app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)

if __name__ == "__main__":
    main()
