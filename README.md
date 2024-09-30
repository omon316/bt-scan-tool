# bt-scan-tool
Scan and report BT-classic and BT-LE devices in your vicinity.

bt-scan-web/
├── app.py                      # Hauptdatei für die Flask-Anwendung
├── bluetooth_scan.py           # Bluetooth-Scan-Funktionen
├── gpt_integration.py          # GPT API-Integration
├── telegram_integration.py     # Telegram-Benachrichtigungsfunktionen
├── config.json                 # Konfigurationsdatei für API-Tokens (Optional)
├── flaskapp.wsgi               # WSGI-Datei für Apache (falls benötigt)
├── requirements.txt            # Abhängigkeiten der Python-Pakete
├── README.md                   # Projektbeschreibung
├── static/                     # Statische Dateien (CSS, JS, Bilder)
│   ├── css/
│   │   └── styles.css          # Custom CSS für Layout
│   ├── js/
│   │   ├── main.js             # JavaScript für dynamisches Laden
│   │   └── charts.js           # JS-Datei für Diagramme (Chart.js)
├── templates/                  # HTML-Vorlagen
│   ├── base.html               # Hauptlayout
│   └── partials/               # Teilansichten für dynamische Anzeige
│       ├── dashboard.html      # Dashboard-Inhalt
│       ├── live.html           # Live-Ansicht der erkannten Geräte
│       ├── stats.html          # Statistiken
│       ├── map.html            # Karte (OpenStreetMap)
│       ├── logs.html           # Logs-Ansicht
│       └── settings.html       # Einstellungen (API-Konfiguration)
└── logs/                       # Verzeichnis für Log-Dateien
    └── bluetooth_scan.log      # Log-Datei für Bluetooth-Scan
