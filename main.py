#!/usr/bin/env python3
import os
import sys
import time
import schedule
from dotenv import load_dotenv
from app import db, scanner, notifier, api

load_dotenv()

def main():
    db.init_db()
    app = api.create_app()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "scan":
            print("[*] Scansione manuale...")
            changes = scanner.full_scan()
            for change in changes:
                if change['changed']:
                    print(f"[+] {change['mac']} -> {change['ip']}")

        elif cmd == "report":
            print("[*] Generazione report...")
            devices = db.get_all_devices()
            online = sum(1 for d in devices if d['online'])
            notifier.send_daily_report(online, len(devices) - online, [])

        elif cmd == "daemon":
            print("[*] Avvio daemon con scansioni ogni ora...")
            schedule.every(int(os.getenv("SCAN_INTERVAL_HOURS", 1))).hours.do(scanner.full_scan)
            schedule.every().day.at("08:00").do(
                lambda: notifier.send_daily_report(
                    sum(1 for d in db.get_all_devices() if d['online']),
                    sum(1 for d in db.get_all_devices() if not d['online']),
                    []
                )
            )

            while True:
                schedule.run_pending()
                time.sleep(60)

    else:
        port = int(os.getenv("FLASK_PORT", 5000))
        debug = os.getenv("DEBUG", "false").lower() == "true"
        print(f"[+] Server started on http://localhost:{port}")
        app.run(host="127.0.0.1", port=port, debug=debug)

if __name__ == "__main__":
    main()
