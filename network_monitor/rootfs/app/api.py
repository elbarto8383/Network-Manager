from flask import Flask, jsonify, request
from functools import wraps
import os
from . import db, scanner, notifier

def create_app():
    app = Flask(__name__, static_folder="../static", static_url_path="/static")
    API_KEY = os.getenv("API_KEY", "")

    if not API_KEY:
        print("[-] WARNING: API_KEY not set! Set it in addon options.")

    def require_api_key(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = request.headers.get("X-API-Key") or request.args.get("api_key")
            if not key or key != API_KEY:
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return decorated_function

    @app.route("/")
    def index():
        return app.send_static_file("dashboard.html")

    @app.route("/api/devices", methods=["GET"])
    @require_api_key
    def get_devices():
        """Ritorna tutti i device."""
        return jsonify(db.get_all_devices())

    @app.route("/api/scan", methods=["POST"])
    @require_api_key
    def trigger_scan():
        """Esegui una scansione manuale."""
        network_range = os.getenv("NETWORK_RANGE", "192.168.1.0/24")
        if request.json:
            network_range = request.json.get("network_range", network_range)
        changes = scanner.full_scan(network_range)
        return jsonify({"status": "ok", "changes": changes})

    @app.route("/api/device/<mac>", methods=["GET"])
    @require_api_key
    def get_device_history(mac):
        """Ritorna la storia IP di un device."""
        return jsonify({
            "mac": mac,
            "history": db.get_ip_changes(mac)
        })

    @app.route("/api/stats", methods=["GET"])
    @require_api_key
    def get_stats():
        """Ritorna statistiche della rete."""
        all_devices = db.get_all_devices()
        online = sum(1 for d in all_devices if d['online'])
        offline = len(all_devices) - online
        return jsonify({
            "total": len(all_devices),
            "online": online,
            "offline": offline
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal error"}), 500

    return app
