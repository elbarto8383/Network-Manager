import requests
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def is_enabled():
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

def _send(message):
    if not is_enabled():
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"[network-monitor] Telegram error: {e}")
        return False

def notify_new_device(mac, ip, display_name, manufacturer=None):
    msg = (
        f"*Network Monitor* — Nuovo device\n\n"
        f"🆕 *Nome:* {display_name}\n"
        f"📍 *IP:* `{ip}`\n"
        f"🔌 *MAC:* `{mac}`\n"
        f"🏭 *Produttore:* {manufacturer or 'Sconosciuto'}\n"
        f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )
    _send(msg)

def notify_ip_change(mac, display_name, old_ip, new_ip):
    msg = (
        f"*Network Monitor* — Cambio IP\n\n"
        f"📱 *Device:* {display_name}\n"
        f"🔌 *MAC:* `{mac}`\n"
        f"📍 *Vecchio IP:* `{old_ip}`\n"
        f"📍 *Nuovo IP:* `{new_ip}`\n"
        f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )
    _send(msg)

def notify_device_offline(display_name, mac, last_seen):
    msg = (
        f"*Network Monitor* — Device offline\n\n"
        f"⚠️ *Device:* {display_name}\n"
        f"🔌 *MAC:* `{mac}`\n"
        f"📅 *Ultimo visto:* {last_seen}\n"
        f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )
    _send(msg)

def send_daily_report(devices_online, devices_offline, ip_changes):
    changes_text = ""
    if ip_changes:
        lines = []
        for c in ip_changes[:10]:
            name = c.get('custom_name') or c.get('hostname') or c['mac_address']
            lines.append(f"  • {name}: `{c['old_ip']}` → `{c['new_ip']}`")
        changes_text = "\n🔄 *Cambi IP (24h):*\n" + "\n".join(lines)

    msg = (
        f"*Network Monitor* — Report giornaliero\n\n"
        f"📊 *{datetime.now().strftime('%d/%m/%Y')}*\n\n"
        f"✅ Online: *{devices_online}*\n"
        f"❌ Offline: *{devices_offline}*\n"
        f"📦 Totale: *{devices_online + devices_offline}*"
        f"{changes_text}\n\n"
        f"⏰ {datetime.now().strftime('%H:%M')}"
    )
    _send(msg)
