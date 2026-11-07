"""
SQLite database management for LanScan / IP Tracker.
Persists tracked devices, custom names, notes, and scan history.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "devices.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                mac TEXT PRIMARY KEY,
                ip TEXT NOT NULL,
                hostname TEXT,
                custom_name TEXT,
                vendor TEXT,
                device_type TEXT,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                is_online INTEGER NOT NULL DEFAULT 1,
                last_latency REAL DEFAULT 0.0,
                open_ports TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                is_favorite INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                subnet TEXT NOT NULL,
                devices_found INTEGER NOT NULL,
                duration_seconds REAL NOT NULL
            )
        """)
        conn.commit()

def record_scan_result(devices_found: List[Dict[str, Any]], subnet: str, duration: float):
    """
    Updates the database with the results of a new scan.
    Marks devices as online/offline and records history.
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    found_macs = set()

    with get_connection() as conn:
        cursor = conn.cursor()
        
        for dev in devices_found:
            mac = dev.get("mac", "").upper()
            if not mac:
                continue
            found_macs.add(mac)
            
            ip = dev.get("ip", "")
            hostname = dev.get("hostname", "")
            vendor = dev.get("vendor", "")
            device_type = dev.get("device_type", "")
            latency = dev.get("latency", 0.0)
            open_ports = ",".join(str(p) for p in dev.get("open_ports", []))
            
            # Check if device already exists
            cursor.execute("SELECT first_seen, custom_name, notes FROM devices WHERE mac = ?", (mac,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE devices SET
                        ip = ?,
                        hostname = CASE WHEN ? != '' THEN ? ELSE hostname END,
                        vendor = ?,
                        device_type = ?,
                        last_seen = ?,
                        is_online = 1,
                        last_latency = ?,
                        open_ports = ?
                    WHERE mac = ?
                """, (ip, hostname, hostname, vendor, device_type, now_str, latency, open_ports, mac))
            else:
                cursor.execute("""
                    INSERT INTO devices (
                        mac, ip, hostname, custom_name, vendor, device_type,
                        first_seen, last_seen, is_online, last_latency, open_ports, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, '')
                """, (mac, ip, hostname, "", vendor, device_type, now_str, now_str, latency, open_ports))

        # Mark devices in this subnet that were NOT found as offline
        # (Only if they match the subnet prefix)
        try:
            subnet_prefix = ".".join(subnet.split("/")[0].split(".")[:3]) + "."
            cursor.execute("""
                UPDATE devices 
                SET is_online = 0 
                WHERE ip LIKE ? AND mac NOT IN ({})
            """.format(','.join(['?'] * len(found_macs)) if found_macs else "''"), 
            [f"{subnet_prefix}%"] + list(found_macs))
        except Exception:
            pass

        # Record scan history entry
        cursor.execute("""
            INSERT INTO scan_history (timestamp, subnet, devices_found, duration_seconds)
            VALUES (?, ?, ?, ?)
        """, (now_str, subnet, len(devices_found), round(duration, 2)))
        
        conn.commit()

def get_all_devices(search: str = "", filter_status: str = "all") -> List[Dict[str, Any]]:
    """Retrieves devices with optional filtering."""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM devices WHERE 1=1"
        params = []
        
        if filter_status == "online":
            query += " AND is_online = 1"
        elif filter_status == "offline":
            query += " AND is_online = 0"
        elif filter_status == "computers":
            query += " AND (device_type LIKE '%Комп''ютер%' OR device_type LIKE '%ПК%')"
        elif filter_status == "favorites":
            query += " AND is_favorite = 1"
            
        if search:
            query += " AND (ip LIKE ? OR mac LIKE ? OR hostname LIKE ? OR custom_name LIKE ? OR vendor LIKE ?)"
            s_param = f"%{search}%"
            params.extend([s_param, s_param, s_param, s_param, s_param])
            
        # Order by online status first, then by IP address
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        devices = [dict(r) for r in rows]
        
        # Sort nicely by IP address
        def ip_sort_key(d):
            try:
                parts = [int(p) for p in d['ip'].split('.')]
                return (0 if d.get('is_online') else 1, parts)
            except Exception:
                return (1, [0, 0, 0, 0])
                
        devices.sort(key=ip_sort_key)
        return devices

def update_device_details(mac: str, custom_name: Optional[str] = None, notes: Optional[str] = None, is_favorite: Optional[int] = None):
    """Updates user-editable metadata for a device."""
    with get_connection() as conn:
        cursor = conn.cursor()
        updates = []
        params = []
        
        if custom_name is not None:
            updates.append("custom_name = ?")
            params.append(custom_name.strip())
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes.strip())
        if is_favorite is not None:
            updates.append("is_favorite = ?")
            params.append(1 if is_favorite else 0)
            
        if updates:
            params.append(mac.upper())
            cursor.execute(f"UPDATE devices SET {', '.join(updates)} WHERE mac = ?", params)
            conn.commit()

def delete_device(mac: str):
    """Deletes a device from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM devices WHERE mac = ?", (mac.upper(),))
        conn.commit()

def get_stats() -> Dict[str, Any]:
    """Returns network overview statistics."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM devices")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM devices WHERE is_online = 1")
        online = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM devices WHERE is_online = 0")
        offline = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM devices WHERE device_type LIKE '%Комп''ютер%' OR device_type LIKE '%ПК%'")
        computers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM devices WHERE is_favorite = 1")
        favorites = cursor.fetchone()[0]
        
        cursor.execute("SELECT * FROM scan_history ORDER BY id DESC LIMIT 1")
        last_scan = cursor.fetchone()
        
        return {
            "total": total,
            "online": online,
            "offline": offline,
            "computers": computers,
            "favorites": favorites,
            "last_scan_time": last_scan["timestamp"] if last_scan else None,
            "last_scan_duration": last_scan["duration_seconds"] if last_scan else None,
            "last_scan_found": last_scan["devices_found"] if last_scan else None
        }

# Initialize on module import
init_db()
