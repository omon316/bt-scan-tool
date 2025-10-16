````markdown
# 🛰️ BT-SCAN-TOOL DASHBOARD

Ein interaktives **Web-Dashboard** für das [BT-Scan-Tool](https://github.com/omon316/bt-scan-tool).  
Es kombiniert alle Funktionen des CLI in einer modernen Oberfläche, mit direkter Steuerung von Bluetooth-Scans, Telegram-Anbindung und Log-Analyse.

---

## 🚀 Installation

### 1. Voraussetzungen

- Python 3.10 oder neuer  
- Bluetooth-Adapter (z. B. Raspberry Pi integriert oder USB-Dongle)  
- Optional: GPS-Modul (z. B. u-blox)

### 2. Repository klonen

```bash
git clone https://github.com/omon316/bt-scan-tool.git
cd bt-scan-tool
````

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

Oder manuell:

```bash
pip install streamlit bleak pybluez requests folium streamlit-folium
```

---

## 🧭 Start des Dashboards

```bash
streamlit run bt_scan_dashboard_full.py
```

Danach öffnet sich die Weboberfläche im Browser unter:

👉 [http://localhost:8501](http://localhost:8501)

---

## 🧩 Dashboard-Funktionen

| Bereich              | Beschreibung                                                                                    |
| -------------------- | ----------------------------------------------------------------------------------------------- |
| **Scanner**          | Startet einen einmaligen Bluetooth-Scan (Classic + BLE) und zeigt die gefundenen Geräte live an |
| **Dauerhafter Scan** | Aktiviert einen Hintergrund-Task, der regelmäßig scannt (Standard: alle 15 Minuten)             |
| **Scan stoppen**     | Beendet laufende Scans                                                                          |
| **Logs anzeigen**    | Zeigt die Datei `logs/bluetooth_scan.log`                                                       |
| **Statistik**        | Visualisiert die häufigsten Geräte und Scan-Zeitpunkte                                          |
| **Karte**            | Zeigt Gerätepositionen (wenn GPS aktiviert ist)                                                 |
| **Telegram senden**  | Sendet aktuelle Ergebnisse oder die Logdatei an den Telegram-Bot                                |
| **Einstellungen**    | Speichert `telegram_api_token`, `telegram_chat_id`, Intervall und GPS-Optionen in `config.json` |

---

## ⚙️ Konfiguration

Die Datei `config.json` enthält alle wichtigen Einstellungen:

```json
{
    "telegram_api_token": "DEIN_API_TOKEN",
    "telegram_chat_id": "123456789",
    "scan_interval": 900,
    "enable_gps": false
}
```

Das Dashboard erstellt und aktualisiert diese Datei automatisch.

---

## 🧠 Tipps

* Wenn kein Token vorhanden ist, erscheint eine Warnung im Dashboard.
* Über den Button **„Telegram-Testnachricht“** kannst du prüfen, ob die Verbindung funktioniert.
* Logs findest du unter `logs/bluetooth_scan.log`.

---

## 🛠️ Systemstart (optional)

Damit das Dashboard beim Boot automatisch startet:

```bash
crontab -e
```

und füge am Ende hinzu:

```
@reboot cd /home/pi/bt-scan-tool && streamlit run bt_scan_dashboard_full.py
```

---

## 🧾 Lizenz

MIT License
© 2025 omon316

```

---

Möchtest du, dass ich diese `README.md` direkt in dein GitHub-Repo `omon316/bt-scan-tool` einfüge (per Commit in den `main`-Branch)?
```
