BT-scan-tool

Overview
BT Scan Web is a web application for scanning Bluetooth devices. It provides functionalities such as real-time Bluetooth scanning, GPT-based data analysis, Telegram notifications, and a live dashboard to display discovered devices.

Features
Live Bluetooth Scan: Displays all discovered Bluetooth devices in real-time.
Statistics: Visualizes Bluetooth activity over time through charts.
GPT Integration: Analyzes scanned data using the OpenAI GPT API.
Telegram Notifications: Sends updates regarding new devices or scan results.
Installation
Clone the Repository:

bash
Code kopieren
git clone https://github.com/<your-username>/bt-scan-web.git
cd bt-scan-web
Install Python Dependencies:

bash
Code kopieren
pip install -r requirements.txt
Create Configuration File: Create a config.json file with your Telegram API token:

json
Code kopieren
{
  "telegram": {
    "api_token": "YOUR_API_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  }
}
Usage
Start the Web Server:

bash
Code kopieren
python3 app.py
Access through the Browser: Open http://localhost:5000 or http://<your-ip>:5000.

Project Structure
graphql
Code kopieren
bt-scan-web/
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
│   │   ├── main.js             # JavaScript for dynamic content loading
│   │   └── charts.js           # JS for rendering charts (Chart.js)
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
License
This project is licensed under the MIT License - see the LICENSE file for details.

