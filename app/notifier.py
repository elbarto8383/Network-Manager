import requests
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    """Invia un messaggio Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[-] Telegram non configurato")
        return False

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=data, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"[-] Errore Telegram: {e}")
        return False

def notify_ip_change(mac, hostname, old_ip, new_ip):
    """Notifica un cambio di IP."""
    message = f"""
🔄 **Device IP Changed**

📱 *Device:* {hostname or mac}
🆔 *MAC:* `{mac}`
📍 *Old IP:* `{old_ip}`
📍 *New IP:* `{new_ip}`
⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    return send_telegram_message(message)

def notify_device_offline(hostname, mac, last_seen):
    """Notifica quando un device va offline."""
    message = f"""
⚠️ **Device Offline**

📱 *Device:* {hostname or mac}
🆔 *MAC:* `{mac}`
⏰ *Last Seen:* {last_seen}
    """
    return send_telegram_message(message)

def send_daily_report(devices_online, devices_offline, ip_changes):
    """Invia report giornaliero."""
    message = f"""
📊 **Network Report - {datetime.now().strftime('%d/%m/%Y')}**

✅ *Online:* {devices_online} device
❌ *Offline:* {devices_offline} device
🔄 *IP Changes:* {len(ip_changes)}

Last sync: {datetime.now().strftime('%H:%M:%S')}
    """
    return send_telegram_message(message)
