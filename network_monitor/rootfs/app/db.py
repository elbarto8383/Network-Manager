import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path("/data/network.db")

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _conn()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac_address TEXT UNIQUE NOT NULL,
            ip_address TEXT,
            custom_name TEXT,
            hostname TEXT,
            manufacturer TEXT,
            first_seen TEXT,
            last_seen TEXT,
            online INTEGER DEFAULT 1
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS ip_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac_address TEXT NOT NULL,
            old_ip TEXT,
            new_ip TEXT,
            changed_at TEXT,
            FOREIGN KEY(mac_address) REFERENCES devices(mac_address)
        )
    ''')

    conn.commit()
    conn.close()
    print("[network-monitor] DB initialized.")

def add_or_update_device(mac, ip, hostname=None, manufacturer=None):
    """
    Inserisce o aggiorna un device.
    Ritorna (is_new, ip_changed, old_ip).
    """
    conn = _conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()

    c.execute('SELECT ip_address, online FROM devices WHERE mac_address = ?', (mac,))
    row = c.fetchone()

    ip_changed = False
    is_new = False
    old_ip = None

    if row:
        old_ip = row['ip_address']
        if old_ip and old_ip != ip:
            ip_changed = True
            c.execute('''
                INSERT INTO ip_history (mac_address, old_ip, new_ip, changed_at)
                VALUES (?, ?, ?, ?)
            ''', (mac, old_ip, ip, now))

        update_fields = ['ip_address = ?', 'last_seen = ?', 'online = 1']
        params = [ip, now]
        if hostname:
            update_fields.append('hostname = ?')
            params.append(hostname)
        if manufacturer and not row['ip_address']:  # non sovrascrivere se già noto
            update_fields.append('manufacturer = ?')
            params.append(manufacturer)
        params.append(mac)

        c.execute(f'UPDATE devices SET {", ".join(update_fields)} WHERE mac_address = ?', params)
    else:
        is_new = True
        c.execute('''
            INSERT INTO devices (mac_address, ip_address, hostname, manufacturer, first_seen, last_seen, online)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (mac, ip, hostname, manufacturer, now, now))

    conn.commit()
    conn.close()
    return is_new, ip_changed, old_ip

def mark_offline(mac):
    conn = _conn()
    conn.execute('UPDATE devices SET online = 0 WHERE mac_address = ?', (mac,))
    conn.commit()
    conn.close()

def get_all_devices():
    conn = _conn()
    rows = conn.execute('''
        SELECT mac_address, ip_address, custom_name, hostname, manufacturer,
               first_seen, last_seen, online
        FROM devices ORDER BY online DESC, last_seen DESC
    ''').fetchall()
    conn.close()
    return [_device_row(r) for r in rows]

def get_device_by_mac(mac):
    conn = _conn()
    row = conn.execute('SELECT * FROM devices WHERE mac_address = ?', (mac,)).fetchone()
    conn.close()
    return _device_row(row) if row else None

def set_custom_name(mac, name):
    conn = _conn()
    conn.execute('UPDATE devices SET custom_name = ? WHERE mac_address = ?', (name, mac))
    conn.commit()
    conn.close()

def get_ip_changes(mac, limit=20):
    conn = _conn()
    rows = conn.execute('''
        SELECT old_ip, new_ip, changed_at FROM ip_history
        WHERE mac_address = ? ORDER BY changed_at DESC LIMIT ?
    ''', (mac, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_ip_changes(hours=24):
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    conn = _conn()
    rows = conn.execute('''
        SELECT h.mac_address, d.custom_name, d.hostname, d.manufacturer,
               h.old_ip, h.new_ip, h.changed_at
        FROM ip_history h
        LEFT JOIN devices d ON h.mac_address = d.mac_address
        WHERE h.changed_at >= ? ORDER BY h.changed_at DESC
    ''', (since,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_devices_offline_since(hours):
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    conn = _conn()
    rows = conn.execute('''
        SELECT mac_address, custom_name, hostname, manufacturer, last_seen
        FROM devices WHERE online = 0 AND last_seen <= ?
    ''', (since,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def _device_row(r):
    if r is None:
        return None
    d = dict(r)
    # Nome visualizzato: custom_name > hostname > mac abbreviato
    d['display_name'] = d.get('custom_name') or d.get('hostname') or f"Device-{d['mac_address'][-5:].upper()}"
    d['online'] = bool(d.get('online', 0))
    return d
