import json
import os
import requests

CONFIG_FILE = "config.json"

# Load or save the configuration
def load_config():
    """Load the configuration from a JSON file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return None

def save_config(config):
    """Save the configuration to a JSON file."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def prompt_for_telegram_credentials():
    """Prompt the user for Telegram API Token and Chat ID."""
    api_token = input("Enter your Telegram API Token: ").strip()
    chat_id = input("Enter your Telegram Chat ID: ").strip()
    return {"api_token": api_token, "chat_id": chat_id}

# Use the config values for the API token and Chat ID.
config = load_config()

if config:
    API_TOKEN = config['api_token']
    CHAT_ID = config['chat_id']
    API_URL = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
else:
    print("Telegram API Token and Chat ID not configured.")
    API_TOKEN = None
    CHAT_ID = None

# Function to send a message via Telegram
def send_telegram_message(message):
    """Send a message via Telegram."""
    if not API_TOKEN or not CHAT_ID:
        print("Telegram API Token or Chat ID not available.")
        return False
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(API_URL, data=payload)
    
    if response.status_code != 200:
        print(f"Telegram API Error: {response.status_code}")
        print(f"Response: {response.text}")
    else:
        print("Message sent successfully!")
    
    return response.status_code == 200

# Function to send an initial notification when the program starts
def send_initial_notification():
    """Send an initial notification when the program starts."""
    message = "Bluetooth scanning program has started."
    return send_telegram_message(message)

# Function to send a report with the list of detected Bluetooth devices
def send_report(devices):
    """Send a report of detected devices via Telegram."""
    if devices:
        message = "Detected Bluetooth devices:\n" + "\n".join(devices)
        return send_telegram_message(message)
    else:
        return send_telegram_message("No new Bluetooth devices detected.")
