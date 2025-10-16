from bleak import BleakScanner
import asyncio

# Existing imports and variables
import time
from datetime import datetime
import bluetooth
import os
#import gpsd ##GPS  Funktion

##def get_gps_position():
    # Connect to the local gpsd
##    gpsd.connect()

    # Get GPS position
##    packet = gpsd.get_current()

##   if packet.mode >= 2:  # 2D fix, will return latitude and longitude
##        lat = packet.lat
##       lon = packet.lon
##      return lat, lon
## else:
##     return None, None  # GPS data not available


# Dictionary to keep track of devices and their report times
devices_seen = {}
mac_to_index = {}  # Mapping MAC addresses to their unique index
global_index_counter = 1

# Path to the log file
log_file_path = "logs/bluetooth_scan.log"

def ensure_log_directory():
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

def log_device(device_info):
    # Write the device info to the log file
    with open(log_file_path, "a") as log_file:
        log_file.write(device_info + "\n")

def scan_bluetooth_devices():
    # Perform a Bluetooth inquiry using pybluez
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True, lookup_class=False)
    return nearby_devices

def get_device_index(device_mac):
    global global_index_counter
    if device_mac not in mac_to_index:
        mac_to_index[device_mac] = global_index_counter
        global_index_counter += 1
    return mac_to_index[device_mac]

def store_device(device_mac, device_name):
    global devices_seen
    current_time = datetime.now()
    if device_mac not in devices_seen or (current_time - devices_seen[device_mac]).total_seconds() > 900:
        devices_seen[device_mac] = current_time
        return True
    return False

def format_device_info(index, device_mac, device_name):
    current_time = datetime.now()
    date_str = current_time.strftime("%d")
    time_str = current_time.strftime("%H%M")
    month_str = current_time.strftime("%b").upper()
    return f"{index:03d} {date_str} {time_str} {month_str} {device_mac} {device_name}"

async def scan_ble_devices():
    devices = await BleakScanner.discover()
    ble_devices = []
    for device in devices:
        ble_devices.append((device.address, device.name))
    return ble_devices

def scan_and_store():
    ensure_log_directory()  # Ensure log directory exists
    
    # Combine results from both classic and BLE scans
    devices = scan_bluetooth_devices()
    
    # Await the BLE scan results
    ble_devices = asyncio.run(scan_ble_devices())
    devices.extend(ble_devices)
    
    results = []
    for addr, name in devices:
        if store_device(addr, name):
            device_index = get_device_index(addr)  # Get the unique index for this MAC address
            device_info = format_device_info(device_index, addr, name)
            results.append(device_info)
            log_device(device_info)  # Log the device info
    return results

# bluetooth_scan.py

def manual_scan_and_send():
    devices = scan_and_store()
    from telegram_report import send_report
    send_report(devices)
