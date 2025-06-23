"""Simple Telegram API helper functions."""

import json
import requests

CONFIG_FILE = 'config.json'


def _load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def send_message(text: str) -> None:
    """Send a text message via Telegram if configured."""
    cfg = _load_config().get('telegram', {})
    token = cfg.get('api_token')
    chat_id = cfg.get('chat_id')
    if not token or not chat_id:
        return
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    try:
        requests.post(url, data=payload, timeout=10)
    except requests.RequestException:
        # Ignore network errors for now
        pass
