import ipaddress
import subprocess
import re
import json
import os
from pathlib import Path
from urllib.request import urlopen
from . import db

MAC_OUI_DB = Path("/data/mac_oui.json")

def load_mac_oui():
    """Carica il database dei MAC OUI."""
    if not MAC_OUI_DB.exists():
        download_mac_oui()

    try:
        with open(MAC_OUI_DB) as f:
            return json.load(f)
    except:
        return {}

def download_mac_oui():
    """Scarica il database dei MAC OUI (prima volta)."""
    try:
        print("[*] Downloading MAC OUI database...")
        url = "https://raw.githubusercontent.com/manishrawat05/MAC-OUI/main/mac_oui.json"
        response = urlopen(url, timeout=10)
        oui_data = json.loads(response.read())
        with open(MAC_OUI_DB, 'w') as f:
            json.dump(oui_data, f)
        print(f"[+] MAC OUI database downloaded: {MAC_OUI_DB}")
    except Exception as e:
        print(f"[-] Error downloading MAC OUI: {e}")

def get_manufacturer(mac):
    """Ritorna il produttore dal MAC address."""
    try:
        oui = load_mac_oui()
        prefix = mac[:8].upper()
        if prefix in oui:
            return oui[prefix].get("name", "Unknown")
    except:
        pass
    return None

def scan_network(network_range="192.168.1.0/24"):
    """Scansiona la rete e ritorna i device trovati."""
    devices = {}
    found = 0

    try:
        network = ipaddress.IPv4Network(network_range, strict=False)
        print(f"[*] Scanning {network_range}...")

        for ip in network.hosts():
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", "-W", "1", str(ip)],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    mac = get_mac_from_arp(str(ip))
                    if mac:
                        manufacturer = get_manufacturer(mac)
                        devices[mac] = {
                            'ip': str(ip),
                            'manufacturer': manufacturer
                        }
                        found += 1
                        print(f"[+] Found: {ip} ({mac}) - {manufacturer or 'Unknown'}")
            except:
                continue

        print(f"[+] Scan complete: {found} devices found")
    except Exception as e:
        print(f"[-] Scan error: {e}")

    return devices

def get_mac_from_arp(ip):
    """Ritorna il MAC address di un IP usando ARP."""
    try:
        result = subprocess.run(
            ["arp", "-n", ip],
            capture_output=True,
            text=True,
            timeout=2
        )
        match = re.search(r'([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})', result.stdout, re.I)
        if match:
            return match.group(1).lower()
    except:
        pass
    return None

def full_scan(network_range="192.168.1.0/24"):
    """Scansiona la rete e aggiorna il database."""
    devices = scan_network(network_range)

    ip_changes = []
    for mac, info in devices.items():
        was_update = db.add_or_update_device(
            mac,
            info['ip'],
            manufacturer=info['manufacturer']
        )
        ip_changes.append({
            'mac': mac,
            'ip': info['ip'],
            'manufacturer': info['manufacturer'],
            'changed': was_update
        })

    return ip_changes
