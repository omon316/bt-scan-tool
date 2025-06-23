import bluetooth


def scan_devices():
    """Scan for nearby Bluetooth devices."""
    try:
        devices = bluetooth.discover_devices(duration=8, lookup_names=True)
        return [{'address': addr, 'name': name} for addr, name in devices]
    except bluetooth.BluetoothError:
        return []
