import json
import os
import requests

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

config = load_config()
API_TOKEN = config.get('api_token') if config else None
CHAT_ID = config.get('chat_id') if config else None

def send_telegram_message(message):
    if not API_TOKEN or not CHAT_ID:
        print("Telegram nicht konfiguriert.")
        return False
    
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    
    try:
        response = requests.post(url, data=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram Sende-Fehler: {e}")
        return False

def send_report(devices_list):
    """Sendet eine formatierte Liste."""
    if not devices_list:
        return False
    # Nachricht splitten falls zu lang für Telegram (4096 Zeichen Limit)
    msg = "📡 Scan Report:\n" + "\n".join(devices_list[:20]) # Limit auf 20 Zeilen für Übersicht
    if len(devices_list) > 20:
        msg += f"\n... und {len(devices_list)-20} weitere."
    return send_telegram_message(msg)
