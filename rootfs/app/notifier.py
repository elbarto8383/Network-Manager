import requests
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def is_enabled():
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

def send_telegram_message(message):
    """Invia un messaggio Telegram."""
    if not is_enabled():
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
        print(f"[-] Telegram error: {e}")
        return False

def notify_ip_change(mac, hostname, old_ip, new_ip):
    """Notifica un cambio di IP."""
    if not is_enabled():
        return False

    message = f"""
🔄 **Device IP Changed**

📱 *Device:* {hostname or mac}
🆔 *MAC:* `{mac}`
📍 *Old IP:* `{old_ip}`
📍 *New IP:* `{new_ip}`
⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    result = send_telegram_message(message)
    if result:
        print(f"[+] Telegram notification sent: {hostname or mac} IP changed")
    return result

def notify_device_offline(hostname, mac, last_seen):
    """Notifica quando un device va offline."""
    if not is_enabled():
        return False

    message = f"""
⚠️ **Device Offline**

📱 *Device:* {hostname or mac}
🆔 *MAC:* `{mac}`
⏰ *Last Seen:* {last_seen}
    """
    result = send_telegram_message(message)
    if result:
        print(f"[+] Telegram notification sent: {hostname or mac} is offline")
    return result

def send_daily_report(devices_online, devices_offline, ip_changes):
    """Invia report giornaliero."""
    if not is_enabled():
        return False

    message = f"""
📊 **Network Report - {datetime.now().strftime('%d/%m/%Y')}**

✅ *Online:* {devices_online} device
❌ *Offline:* {devices_offline} device
🔄 *IP Changes:* {len(ip_changes)}

Last sync: {datetime.now().strftime('%H:%M:%S')}
    """
    result = send_telegram_message(message)
    if result:
        print("[+] Daily report sent to Telegram")
    return result
