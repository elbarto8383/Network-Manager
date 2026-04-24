import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "network.db"

def init_db():
    """Inizializza il database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY,
            mac_address TEXT UNIQUE NOT NULL,
            ip_address TEXT,
            hostname TEXT,
            manufacturer TEXT,
            last_seen TIMESTAMP,
            first_seen TIMESTAMP,
            online BOOLEAN DEFAULT 1
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS ip_history (
            id INTEGER PRIMARY KEY,
            mac_address TEXT NOT NULL,
            old_ip TEXT,
            new_ip TEXT,
            changed_at TIMESTAMP,
            FOREIGN KEY(mac_address) REFERENCES devices(mac_address)
        )
    ''')

    conn.commit()
    conn.close()

def add_or_update_device(mac, ip, hostname=None, manufacturer=None):
    """Aggiorna o aggiunge un device."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT ip_address, online FROM devices WHERE mac_address = ?', (mac,))
    existing = c.fetchone()

    now = datetime.utcnow().isoformat()

    if existing:
        old_ip, was_online = existing
        if old_ip != ip and old_ip:
            c.execute('''
                INSERT INTO ip_history (mac_address, old_ip, new_ip, changed_at)
                VALUES (?, ?, ?, ?)
            ''', (mac, old_ip, ip, now))

        c.execute('''
            UPDATE devices
            SET ip_address = ?, last_seen = ?, online = 1
            WHERE mac_address = ?
        ''', (ip, now, mac))
    else:
        c.execute('''
            INSERT INTO devices (mac_address, ip_address, hostname, manufacturer, first_seen, last_seen, online)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (mac, ip, hostname, manufacturer, now, now))

    conn.commit()
    conn.close()

    return existing is not None

def get_all_devices():
    """Ritorna tutti i device."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT mac_address, ip_address, hostname, manufacturer, last_seen, online
        FROM devices
        ORDER BY last_seen DESC
    ''')
    devices = c.fetchall()
    conn.close()

    return [
        {
            'mac': d[0],
            'ip': d[1],
            'hostname': d[2],
            'manufacturer': d[3],
            'last_seen': d[4],
            'online': bool(d[5])
        }
        for d in devices
    ]

def get_ip_changes(mac):
    """Ritorna la storia IP di un device."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT old_ip, new_ip, changed_at FROM ip_history
        WHERE mac_address = ?
        ORDER BY changed_at DESC
        LIMIT 20
    ''', (mac,))
    history = c.fetchall()
    conn.close()
    return history

def set_device_offline(mac):
    """Marca un device come offline."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE devices SET online = 0 WHERE mac_address = ?', (mac,))
    conn.commit()
    conn.close()

def get_offline_devices():
    """Ritorna i device che non sono online."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT mac_address, hostname, last_seen FROM devices WHERE online = 0')
    devices = c.fetchall()
    conn.close()
    return devices
