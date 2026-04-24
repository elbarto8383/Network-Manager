import subprocess
import re
import json
import os
from pathlib import Path
from urllib.request import urlopen
from . import db, notifier

MAC_OUI_DB = Path("/data/mac_oui.json")
_oui_cache = None

def load_mac_oui():
    global _oui_cache
    if _oui_cache:
        return _oui_cache
    if not MAC_OUI_DB.exists():
        _download_mac_oui()
    try:
        with open(MAC_OUI_DB) as f:
            _oui_cache = json.load(f)
    except Exception:
        _oui_cache = {}
    return _oui_cache

def _download_mac_oui():
    try:
        print("[network-monitor] Downloading MAC OUI database...")
        # Database OUI pubblico in formato semplice JSON
        url = "https://raw.githubusercontent.com/wireshark/wireshark/master/manuf"
        # Fallback: usiamo un DB minimo integrato se il download fallisce
        response = urlopen(
            "https://raw.githubusercontent.com/nicowillis/mac-vendor-lookup/main/oui.json",
            timeout=15
        )
        data = json.loads(response.read())
        with open(MAC_OUI_DB, 'w') as f:
            json.dump(data, f)
        print(f"[network-monitor] MAC OUI DB downloaded ({MAC_OUI_DB})")
    except Exception as e:
        print(f"[network-monitor] MAC OUI download failed: {e} — using empty DB")
        with open(MAC_OUI_DB, 'w') as f:
            json.dump({}, f)

def get_manufacturer(mac):
    """Ritorna il produttore dal prefisso MAC (OUI)."""
    try:
        oui = load_mac_oui()
        # Prova prefisso 8 chars (XX:XX:XX)
        prefix8 = mac[:8].upper().replace(':', '')
        prefix6 = mac[:6].upper().replace(':', '')
        return (
            oui.get(prefix8) or
            oui.get(prefix6) or
            oui.get(mac[:8].upper()) or
            oui.get(mac[:8].lower()) or
            None
        )
    except Exception:
        return None

def _ping(ip, timeout=1):
    """Ping a un IP. Ritorna True se risponde."""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), str(ip)],
            capture_output=True, timeout=timeout + 1
        )
        return result.returncode == 0
    except Exception:
        return False

def _get_mac_from_arp(ip):
    """Legge il MAC dall'ARP cache dopo il ping."""
    try:
        result = subprocess.run(
            ["arp", "-n", str(ip)],
            capture_output=True, text=True, timeout=2
        )
        match = re.search(
            r'([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5})',
            result.stdout
        )
        if match:
            return match.group(1).lower()
    except Exception:
        pass
    return None

def _nmap_scan(network_range):
    """
    Scan con nmap -sn (ping scan, no port scan).
    Più veloce e affidabile del ping singolo per subnet.
    """
    found = {}
    try:
        result = subprocess.run(
            ["nmap", "-sn", "--host-timeout", "2s", network_range],
            capture_output=True, text=True, timeout=300
        )
        # Parsing output nmap
        current_ip = None
        for line in result.stdout.splitlines():
            ip_match = re.search(r'Nmap scan report for (?:[\w.-]+ \()?(\d+\.\d+\.\d+\.\d+)', line)
            if ip_match:
                current_ip = ip_match.group(1)

            mac_match = re.search(r'MAC Address: ([0-9A-F:]{17}) \(([^)]*)\)', line)
            if mac_match and current_ip:
                mac = mac_match.group(1).lower()
                vendor_nmap = mac_match.group(2)
                manufacturer = get_manufacturer(mac) or vendor_nmap or None
                found[mac] = {'ip': current_ip, 'manufacturer': manufacturer}
                current_ip = None

        # Il gateway/host locale non ha MAC nel nmap output — prova ARP
        for line in result.stdout.splitlines():
            ip_match = re.search(r'Nmap scan report for (?:[\w.-]+ \()?(\d+\.\d+\.\d+\.\d+)', line)
            if ip_match:
                ip = ip_match.group(1)
                if not any(v['ip'] == ip for v in found.values()):
                    mac = _get_mac_from_arp(ip)
                    if mac and mac not in found:
                        found[mac] = {'ip': ip, 'manufacturer': get_manufacturer(mac)}

    except Exception as e:
        print(f"[network-monitor] nmap error: {e}")

    return found

def full_scan(network_range, offline_threshold_hours=2):
    """
    Scansione completa:
    1. Trova device attivi
    2. Aggiorna DB
    3. Marca offline i device non visti
    4. Manda notifiche Telegram
    """
    print(f"[network-monitor] Scanning {network_range}...")
    active = _nmap_scan(network_range)
    print(f"[network-monitor] Found {len(active)} active devices.")

    results = []

    for mac, info in active.items():
        is_new, ip_changed, old_ip = db.add_or_update_device(
            mac, info['ip'], manufacturer=info.get('manufacturer')
        )

        if is_new:
            device = db.get_device_by_mac(mac)
            print(f"[network-monitor] NEW device: {mac} @ {info['ip']} ({info.get('manufacturer', 'Unknown')})")
            notifier.notify_new_device(
                mac, info['ip'],
                device['display_name'],
                info.get('manufacturer')
            )

        elif ip_changed:
            device = db.get_device_by_mac(mac)
            print(f"[network-monitor] IP CHANGE: {mac} {old_ip} -> {info['ip']}")
            notifier.notify_ip_change(mac, device['display_name'], old_ip, info['ip'])

        results.append({
            'mac': mac,
            'ip': info['ip'],
            'manufacturer': info.get('manufacturer'),
            'is_new': is_new,
            'ip_changed': ip_changed,
        })

    # Marca offline i device non trovati in questo scan
    all_devices = db.get_all_devices()
    active_macs = set(active.keys())
    for device in all_devices:
        if device['online'] and device['mac_address'] not in active_macs:
            db.mark_offline(device['mac_address'])
            print(f"[network-monitor] OFFLINE: {device['display_name']} ({device['mac_address']})")

    # Notifica device offline da X ore
    offline_devices = db.get_devices_offline_since(offline_threshold_hours)
    for d in offline_devices:
        notifier.notify_device_offline(
            d.get('custom_name') or d.get('hostname') or d['mac_address'],
            d['mac_address'],
            d['last_seen']
        )

    return results
