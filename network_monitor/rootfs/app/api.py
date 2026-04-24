from flask import Flask, jsonify, request, redirect
from functools import wraps
import os
from . import db, scanner, notifier

def create_app(ingress_path=""):
    app = Flask(__name__, static_folder="../static", static_url_path="/static")
    API_KEY = os.getenv("API_KEY", "")

    if not API_KEY:
        print("[network-monitor] WARNING: API_KEY not set!")

    # --- Auth decorator ---
    def require_api_key(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            key = request.headers.get("X-API-Key") or request.args.get("api_key")
            if not key or key != API_KEY:
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return decorated

    # --- Root & dashboard ---
    @app.route("/")
    def index():
        return app.send_static_file("dashboard.html")

    # Se ingress path attivo, gestisci redirect
    if ingress_path:
        @app.route(ingress_path)
        def ingress_root():
            return app.send_static_file("dashboard.html")

        @app.route(ingress_path + "/")
        def ingress_root_slash():
            return app.send_static_file("dashboard.html")

    # --- API devices ---
    @app.route("/api/devices", methods=["GET"])
    @require_api_key
    def get_devices():
        devices = db.get_all_devices()
        return jsonify(devices)

    @app.route("/api/device/<mac>", methods=["GET"])
    @require_api_key
    def get_device(mac):
        history = db.get_ip_changes(mac)
        device = db.get_device_by_mac(mac)
        return jsonify({"device": device, "ip_history": history})

    @app.route("/api/device/<mac>", methods=["PATCH"])
    @require_api_key
    def rename_device(mac):
        data = request.get_json()
        name = data.get("custom_name", "").strip()
        if not name:
            return jsonify({"error": "custom_name required"}), 400
        db.set_custom_name(mac, name)
        return jsonify({"ok": True, "mac": mac, "custom_name": name})

    # --- API scan ---
    @app.route("/api/scan", methods=["POST"])
    @require_api_key
    def trigger_scan():
        network_range = os.getenv("NETWORK_RANGE", "192.168.1.0/24")
        offline_threshold = int(os.getenv("OFFLINE_THRESHOLD_HOURS", 2))
        changes = scanner.full_scan(network_range, offline_threshold)
        return jsonify({"status": "ok", "changes": changes})

    # --- API stats ---
    @app.route("/api/stats", methods=["GET"])
    @require_api_key
    def get_stats():
        devices = db.get_all_devices()
        online = sum(1 for d in devices if d['online'])
        offline = len(devices) - online
        ip_changes_24h = db.get_recent_ip_changes(hours=24)
        return jsonify({
            "total": len(devices),
            "online": online,
            "offline": offline,
            "ip_changes_24h": len(ip_changes_24h)
        })

    # --- API ip history recente ---
    @app.route("/api/ip-changes", methods=["GET"])
    @require_api_key
    def get_ip_changes():
        hours = int(request.args.get("hours", 24))
        changes = db.get_recent_ip_changes(hours=hours)
        return jsonify(changes)

    # --- Error handlers ---
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal error"}), 500

    return app
