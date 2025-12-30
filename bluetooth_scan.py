import asyncio
import bluetooth  # PyBluez für Classic
from bleak import BleakScanner  # Für BLE & RSSI
import requests
import json
import os
from database import log_device_to_db, init_db

# --- GPS Setup ---
try:
    import gpsd
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False

# Cache für Vendor Lookup, um API-Limits zu sparen
VENDOR_CACHE_FILE = "logs/vendor_cache.json"
vendor_cache = {}

def load_vendor_cache():
    global vendor_cache
    if os.path.exists(VENDOR_CACHE_FILE):
        with open(VENDOR_CACHE_FILE, 'r') as f:
            vendor_cache = json.load(f)

def save_vendor_cache():
    with open(VENDOR_CACHE_FILE, 'w') as f:
        json.dump(vendor_cache, f)

def get_gps_position():
    """Holt GPS Daten falls verfügbar, sonst None."""
    if not GPS_AVAILABLE:
        return None, None
    try:
        gpsd.connect()
        packet = gpsd.get_current()
        if packet.mode >= 2:
            return packet.lat, packet.lon
    except Exception:
        pass
    return None, None

def get_vendor(mac):
    """Ermittelt den Hersteller anhand der MAC-Adresse."""
    prefix = mac[:8].upper()
    
    if prefix in vendor_cache:
        return vendor_cache[prefix]
    
    try:
        # Einfache API Abfrage (MacVendors)
        url = f"https://api.macvendors.com/{mac}"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            vendor = response.text.strip()
            vendor_cache[prefix] = vendor
            save_vendor_cache()
            return vendor
    except Exception:
        pass
    
    return "Unknown"

async def scan_ble_devices():
    """Scannt BLE Geräte inkl. RSSI."""
    devices_found = []
    try:
        scanned = await BleakScanner.discover(timeout=5.0, return_adv=True)
        for device, adv in scanned.values():
            devices_found.append({
                "mac": device.address,
                "name": device.name or "Unknown BLE",
                "rssi": adv.rssi,
                "type": "BLE"
            })
    except Exception as e:
        print(f"BLE Scan Error: {e}")
    return devices_found

def scan_classic_devices():
    """Scannt Classic Bluetooth Geräte (ohne RSSI in Standard PyBluez)."""
    devices_found = []
    try:
        # duration=4 ist schneller
        results = bluetooth.discover_devices(duration=4, lookup_names=True, flush_cache=True)
        for mac, name in results:
            devices_found.append({
                "mac": mac,
                "name": name,
                "rssi": -100,  # Platzhalter, da PyBluez kein RSSI liefert
                "type": "Classic"
            })
    except Exception as e:
        print(f"Classic Scan Error: {e}")
    return devices_found

def scan_and_store():
    """Hauptfunktion: Scannt, reichert Daten an (GPS, Vendor) und speichert in DB."""
    init_db()
    load_vendor_cache()
    
    lat, lon = get_gps_position()
    
    # Parallelisierung simulieren (BLE ist async, Classic ist sync)
    ble_results = asyncio.run(scan_ble_devices())
    classic_results = scan_classic_devices()
    
    all_devices = ble_results + classic_results
    newly_logged = []
    
    for dev in all_devices:
        vendor = get_vendor(dev['mac'])
        
        # In DB speichern
        log_device_to_db(
            mac=dev['mac'],
            name=dev['name'],
            rssi=dev['rssi'],
            vendor=vendor,
            lat=lat,
            lon=lon
        )
        
        # Formatierung für Telegram/Output
        info_str = f"{dev['mac']} | {dev['name']} | RSSI: {dev['rssi']} | {vendor}"
        newly_logged.append(info_str)
        
    return newly_logged
