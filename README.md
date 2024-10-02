# BT-Scan-Tool

## Overview
This Python-based tool runs on a Raspberry Pi and continuously scans for nearby Bluetooth devices. It can also capture GPS coordinates using a u-blox NEO-6M GPS module (WIP) and logs the detected devices. Additionally, the tool can send the logged data to a Telegram chat.

## Features
- Bluetooth Classic and BLE scanning
- GPS integration with MGRS format logging
- CLI for easy control and interaction
- Periodic and manual Telegram reporting

## Installation
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/<your-username>/bt-scan-web.git
    cd bt-scan-web
    ```

2. **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Create Configuration File**:
    Create a `config.json` file with your Telegram API token:
    ```json
    {
      "telegram": {
        "api_token": "YOUR_API_TOKEN",
        "chat_id": "YOUR_CHAT_ID"
      }
    }
    ```

## Usage
1. **Telegram API-Token and ChatID**:
   Edit `config.json` and fill in your Telegram API and ChatID.
2. **Start bt-scan-tool**:
   run `python3 main.py`
3. **Choose your BT-Device**:
   One or more MAC-Adresses will be displayed. Choose your prefered BT-Device.
4. **Access through the Browser**:
   Open `http://localhost:5000` or `http://<your-ip>:5000`.
    

## Project Structure
```bash
bt-scan-tool/
├── app.py                      # Main Flask application file
├── bluetooth_scan.py           # Bluetooth scanning functions
├── gpt_integration.py          # GPT API integration for log analysis
├── telegram_integration.py     # Telegram notification functions
├── config.json                 # Configuration file for API tokens (Optional)
├── flaskapp.wsgi               # WSGI file for Apache (if required)
├── requirements.txt            # Python package dependencies
├── README.md                   # Project documentation
├── static/                     # Static assets (CSS, JS, images)
│   ├── css/
│   │   └── styles.css          # Custom styles for layout
│   ├── js/
│   │       ├── main.js         # JavaScript for dynamic content loading
│   │       └── charts.js       # JS for rendering charts (Chart.js)
├── templates/                  # HTML templates
│   ├── base.html               # Main layout file
│   └── partials/               # Partials for dynamic content
│       ├── dashboard.html      # Dashboard content
│       ├── live.html           # Live view for detected devices
│       ├── stats.html          # Statistics and charts
│       ├── map.html            # Map view (e.g., OpenStreetMap)
│       ├── logs.html           # Logs view
│       └── settings.html       # Settings for API configurations
└── logs/                       # Directory for log files
    └── bluetooth_scan.log      # Log file for Bluetooth scan data
```
## Current Issues
Telegram only allows messages with 4096 characters, an error occurs if your bluetooth-scan.log file exceeds 4096 characters.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For questions or issues, please open an issue on GitHub or contact me via DM.
