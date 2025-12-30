import sqlite3
import os
from datetime import datetime

DB_FILE = "logs/scan_data.db"

def init_db():
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    
    # Tabelle für Scan-Ergebnisse
    c.execute('''
        CREATE TABLE IF NOT EXISTS scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            mac TEXT,
            name TEXT,
            rssi INTEGER,
            vendor TEXT,
            lat REAL,
            lon REAL
        )
    ''')
    
    # Tabelle für bekannte Geräte (Whitelist/Alias)
    c.execute('''
        CREATE TABLE IF NOT EXISTS known_devices (
            mac TEXT PRIMARY KEY,
            alias TEXT,
            is_trusted INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def log_device_to_db(mac, name, rssi, vendor, lat, lon):
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute('''
            INSERT INTO scan_results (timestamp, mac, name, rssi, vendor, lat, lon)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, mac, name, rssi, vendor, lat, lon))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"DB Error: {e}")
        return False

def get_recent_logs(limit=200):
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        import pandas as pd
        df = pd.read_sql_query(f"SELECT * FROM scan_results ORDER BY id DESC LIMIT {limit}", conn)
        conn.close()
        return df
    except Exception:
        return None
