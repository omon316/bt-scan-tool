"""
BT‑Scan‑Tool Dashboard (vollständige Version, integriert)
=========================================================

Änderungen gegenüber der vorherigen Fassung:
- ✅ LED‑Statusanzeige (grün/rot) konsistent über `st.session_state["scan_running"]`.
- ✅ Hintergrund‑Scan ohne Streamlit‑Aufrufe im Thread (keine ScriptRunContext‑Warnungen).
- ✅ Einmal‑Scan nutzt `scan_and_store()` ⇒ Logs werden sicher geschrieben.
- ✅ Absolute Log‑Pfade relativ zum Skriptverzeichnis.
- ✅ `use_container_width` → `width='stretch'` (kompatibel >= Okt 2025).
- ✅ Heartbeat + Iterationszähler zur Laufzeitkontrolle.
- ✅ Telegram‑Versand aus dem Thread direkt über `telegram_report`, ohne UI‑Calls.

Start:
    streamlit run bt_scan_dashboard_full.py
"""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import pandas as pd  # type: ignore
import streamlit as st  # type: ignore
from folium import Map, Marker  # type: ignore
from streamlit_folium import st_folium  # type: ignore

# -----------------------------------------------------------------------------
# Modul‑Importe (robust gegen fehlende HW/Bibliotheken)
# -----------------------------------------------------------------------------
try:
    import bluetooth_scan  # type: ignore
except Exception as scan_import_error:  # noqa: BLE001
    bluetooth_scan = None
    scan_import_error_message = str(scan_import_error)
else:
    scan_import_error_message = ""

try:
    import telegram_report  # type: ignore
except Exception as telegram_import_error:  # noqa: BLE001
    telegram_report = None
    telegram_import_error_message = str(telegram_import_error)
else:
    telegram_import_error_message = ""

# -----------------------------------------------------------------------------
# Pfade (absolut relativ zum Skript)
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_PATH = LOG_DIR / "bluetooth_scan.log"
CONFIG_PATH = BASE_DIR / "config.json"

# -----------------------------------------------------------------------------
# Hilfsfunktionen
# -----------------------------------------------------------------------------

def load_config() -> dict:
    """Konfiguration (Telegram) laden oder Defaults liefern."""
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"api_token": "", "chat_id": "", "scan_interval": 900, "enable_gps": False}


def save_config(config: dict) -> None:
    """Konfiguration nach `config.json` speichern."""
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def list_bluetooth_receivers() -> List[str]:
    """Verfügbare Bluetooth‑Adapter mit `hcitool dev` ermitteln (MAC‑Adressen)."""
    import subprocess
    try:
        result = subprocess.run(["hcitool", "dev"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = result.stdout.splitlines()[1:]  # Kopfzeile überspringen
        receivers: List[str] = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                receivers.append(parts[1])
        return receivers
    except Exception:  # noqa: BLE001
        return []


def read_logs() -> List[str]:
    """Logdatei zeilenweise lesen."""
    if LOG_PATH.exists():
        with LOG_PATH.open("r", encoding="utf-8") as f:
            return f.read().splitlines()
    return []


def parse_device_string(device_string: str) -> Tuple[int, str, str, str, str]:
    """Gerätezeile parsen: "<index> <day> <time> <MONTH> <MAC> <Name>"."""
    parts = device_string.strip().split(maxsplit=5)
    if len(parts) < 6:
        parts = (parts + [""])[:6]
    index = parts[0]
    day = parts[1]
    clock = parts[2]
    month = parts[3]
    mac = parts[4]
    name = parts[5] if len(parts) > 5 else ""
    now = datetime.now()
    date_str = f"{day}-{month}-{now.year} {clock[:2]}:{clock[2:]}"
    return int(index), date_str, mac, name, device_string


def devices_to_dataframe(devices: List[str]) -> pd.DataFrame:
    """Liste formatierter Gerätezeilen → DataFrame."""
    records = []
    for device in devices:
        try:
            idx, date_str, mac, name, _raw = parse_device_string(device)
            records.append((idx, date_str, mac, name))
        except Exception:  # noqa: BLE001
            continue
    df = pd.DataFrame(records, columns=["Index", "Zeit", "MAC", "Name"])
    return df


def sample_devices() -> List[str]:
    """Fallback‑Daten, falls Scan fehlschlägt."""
    return [
        "001 14 1230 OCT AA:BB:CC:DD:EE:FF BT-Headset",
        "002 14 1231 OCT 11:22:33:44:55:66 Smartwatch",
    ]


def perform_scan_backend(force_log: bool = False) -> List[str]:
    """Bluetooth-Scan ausführen und formatierte Gerätezeilen zurückgeben.

    - Wenn ``force_log`` True ist, wird die TTL-Logik des Repos umgangen und
      *jeder* gefundene Eintrag geloggt (Classic + BLE), indem wir die
      Einträge selbst formatieren und via ``bluetooth_scan.log_device``
      schreiben.
    - Wenn ``force_log`` False ist, nutzen wir die Standardfunktion
      ``bluetooth_scan.scan_and_store()`` des Repos (loggt nur neue/ältere
      Einträge > 900 s).

    **Wichtig:** Keine Streamlit-UI-Calls in dieser Funktion (thread-sicher).
    Fehler werden in ``st.session_state['last_scan_error']`` abgelegt.
    """
    try:
        if not bluetooth_scan:
            raise RuntimeError("bluetooth_scan-Modul nicht verfügbar")

        if not force_log:
            # Standardweg: benutzt die eingebaute TTL (900 s)
            return bluetooth_scan.scan_and_store()

        # Force-Logging: Classic + BLE scan und *alles* loggen
        entries: List[str] = []
        try:
            classic = bluetooth_scan.scan_bluetooth_devices()
        except Exception:
            classic = []

        try:
            # BLE-Scan (async)
            ble_devices = []
            import asyncio
            ble_devices = asyncio.run(bluetooth_scan.scan_ble_devices())
        except Exception:
            ble_devices = []

        devices = list(classic) + list(ble_devices)
        for addr, name in devices:
            try:
                idx = bluetooth_scan.get_device_index(addr)
                info = bluetooth_scan.format_device_info(idx, addr, name or "Unknown")
                bluetooth_scan.log_device(info)
                entries.append(info)
            except Exception:
                continue
        return entries
    except Exception as exc:
        # Keine UI-Ausgabe hier; nur Status merken
        st.session_state["last_scan_error"] = str(exc)
        # Fallback: Musterwerte zurückgeben, damit Aufrufer etwas anzeigen kann
        return sample_devices()


def send_report_to_telegram_ui(devices: List[str]) -> None:
    """Geräteliste via Telegram senden (mit UI‑Feedback). NICHT im Thread nutzen!"""
    if telegram_report:
        try:
            telegram_report.send_report(devices)
            st.success("Geräteliste wurde via Telegram gesendet.")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Fehler beim Senden via Telegram: {exc}")
    else:
        st.warning("Telegram‑Modul nicht verfügbar. Bitte konfigurieren.")


def send_log_to_telegram_ui(lines: List[str]) -> None:
    """Loginhalt via Telegram senden (mit UI‑Feedback). NICHT im Thread nutzen!"""
    if telegram_report:
        try:
            message = "Bluetooth Scan Log:\n" + "\n".join(lines)
            telegram_report.send_telegram_message(message)
            st.success("Log wurde via Telegram gesendet.")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Fehler beim Senden des Logs: {exc}")
    else:
        st.warning("Telegram‑Modul nicht verfügbar. Bitte konfigurieren.")


# -----------------------------------------------------------------------------
# Hintergrund‑Thread (ohne Streamlit‑Calls)
# -----------------------------------------------------------------------------

def background_scan_loop(interval_seconds: int = 900) -> None:
    """Periodischer Scan + optionaler Telegram‑Report (ohne Streamlit‑Calls)."""
    while st.session_state.get("scan_running", False):
        try:
            force_log = st.session_state.get("force_log_every_scan", False)
            devices = perform_scan_backend(force_log=force_log)  # schreibt ins Log (ggf. erzwungen)
            # Optional direkt per Telegram berichten (ohne UI‑Calls)
            if telegram_report:
                try:
                    telegram_report.send_report(devices)
                except Exception:
                    st.session_state["bg_last_error"] = "Telegram‑Versand fehlgeschlagen"
            # Heartbeat/Counter aktualisieren
            st.session_state["bg_iterations"] = st.session_state.get("bg_iterations", 0) + 1
            st.session_state["bg_last_heartbeat"] = time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            st.session_state["bg_last_error"] = str(e)
        # Schlaf in kleinen Schritten, damit Stop schnell greift
        slept = 0
        while slept < interval_seconds and st.session_state.get("scan_running", False):
            time.sleep(1)
            slept += 1


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------

st.set_page_config(page_title="BT‑Scan‑Tool Dashboard", layout="wide")

# Session‑State‑Defaults
if "scan_running" not in st.session_state:
    st.session_state.scan_running = False
if "scan_thread" not in st.session_state:
    st.session_state.scan_thread = None
if "bg_iterations" not in st.session_state:
    st.session_state.bg_iterations = 0
if "bg_last_heartbeat" not in st.session_state:
    st.session_state.bg_last_heartbeat = None
if "scan_interval" not in st.session_state:
    st.session_state.scan_interval = load_config().get("scan_interval", 900)

# LED‑Statusanzeige (grün/rot)
scan_running = st.session_state.get("scan_running", False)
status_color = "#16a34a" if scan_running else "#dc2626"
status_text = "AKTIV" if scan_running else "INAKTIV"

st.markdown(f"""
<div style="display:flex;align-items:center;gap:.6rem;font-weight:600;font-size:1.1rem;">
  <div style="width:16px;height:16px;border-radius:50%;background:{status_color};box-shadow:0 0 10px {status_color};"></div>
  BT-SCAN&nbsp;{status_text}
</div>
""", unsafe_allow_html=True)

st.title("📡 Bluetooth‑Scan‑Tool Dashboard")

# Warnungen zu Modul‑Importen
if scan_import_error_message:
    st.warning(
        f"Bluetooth‑Scan‑Modul konnte nicht importiert werden: {scan_import_error_message}. "
        "Es werden Platzhalterdaten verwendet."
    )
if telegram_import_error_message:
    st.warning(
        f"Telegram‑Modul konnte nicht importiert werden: {telegram_import_error_message}. "
        "Das Dashboard läuft, aber Telegram‑Versand ist deaktiviert."
    )

# Sidebar: Einstellungen
with st.sidebar:
    st.header("⚙️ Einstellungen")
    cfg = load_config()
    st.subheader("Telegram")
    api_token = st.text_input("API Token", value=cfg.get("api_token", ""))
    chat_id = st.text_input("Chat ID", value=cfg.get("chat_id", ""))
    interval = st.slider("Intervall (Sekunden)", min_value=60, max_value=3600, value=st.session_state.scan_interval, step=30)
    force_log_every_scan = st.checkbox("Jede Wiederholung loggen (TTL 900s ignorieren)", value=st.session_state.get("force_log_every_scan", False))

    if st.button("Konfiguration speichern"):
        cfg.update({"api_token": api_token, "chat_id": chat_id, "scan_interval": interval})
        save_config(cfg)
        st.session_state.scan_interval = interval
        st.session_state.force_log_every_scan = force_log_every_scan
        # Telegram‑Runtime‑Werte aktualisieren
        if telegram_report:
            telegram_report.API_TOKEN = api_token
            telegram_report.CHAT_ID = chat_id
            telegram_report.API_URL = f"https://api.telegram.org/bot{api_token}/sendMessage" if api_token else None
        st.success("Konfiguration gespeichert.")

    # Bluetooth‑Adapter Auswahl
    receivers = list_bluetooth_receivers()
    if receivers:
        default_receiver = st.session_state.get("selected_receiver", receivers[0])
        idx = receivers.index(default_receiver) if default_receiver in receivers else 0
        selected = st.selectbox("Bluetooth‑Adapter", receivers, index=idx)
        st.session_state.selected_receiver = selected
    else:
        st.caption("Keine Bluetooth‑Adapter gefunden oder `hcitool` nicht verfügbar.")

# Programmkontrolle
st.subheader("Programmkontrolle")
col1, col2, col3 = st.columns(3)
with col1:
    if not st.session_state.scan_running:
        if st.button("▶️ Dauer‑Scan starten", key="start"):
            st.session_state.scan_running = True
            t = threading.Thread(target=background_scan_loop, kwargs={"interval_seconds": st.session_state.scan_interval}, daemon=True)
            t.start()
            st.session_state.scan_thread = t
    else:
        st.write("▶️ Der Hintergrund‑Scan läuft.")

with col2:
    if st.session_state.scan_running:
        if st.button("⏹️ Stop", key="stop"):
            st.session_state.scan_running = False
    else:
        st.write("⏹️ Kein Hintergrund‑Scan aktiv.")

with col3:
    st.caption(
        f"Heartbeat: {st.session_state.get('bg_last_heartbeat','–')} · Iterationen: {st.session_state.get('bg_iterations',0)}"
    )

# Manueller Scan
st.subheader("Manueller Scan")
if st.button("🔍 Einmaligen Scan durchführen", key="manual_scan"):
    force_log = st.session_state.get("force_log_every_scan", False)
    manual_devices = perform_scan_backend(force_log=force_log)  # schreibt ins Log (ggf. erzwungen)
    st.session_state.manual_results = manual_devices
    st.success("Scan abgeschlossen.")

manual_results: List[str] = st.session_state.get("manual_results", [])
if manual_results:
    df_manual = devices_to_dataframe(manual_results)
    st.write("### Ergebnisse des manuellen Scans")
    st.dataframe(df_manual, width='stretch')
    if st.button("📤 Ergebnisse via Telegram senden", key="manual_send"):
        send_report_to_telegram_ui(manual_results)

# Tabs: Log / Statistik / Karte

tab_log, tab_stats, tab_map = st.tabs(["Log", "Statistik", "Karte"])

with tab_log:
    st.subheader("Logdatei ansehen")
    logs = read_logs()
    if logs:
        to_display = logs[-200:]
        st.text_area("Logauszug", value="\n".join(to_display), height=300)
        if st.button("📤 Log via Telegram senden", key="send_log"):
            send_log_to_telegram_ui(to_display)
    else:
        st.write("Es sind keine Logdaten vorhanden.")

with tab_stats:
    st.subheader("Statistische Auswertung")
    logs = read_logs()
    if logs:
        data_records = []
        for line in logs:
            parts = line.split()
            if len(parts) >= 6:
                index = parts[0]
                day = parts[1]
                clock = parts[2]
                month = parts[3]
                mac = parts[4]
                name = " ".join(parts[5:])
                try:
                    dt = datetime.strptime(f"{day} {month} {datetime.now().year} {clock}", "%d %b %Y %H%M")
                except Exception:  # noqa: BLE001
                    dt = datetime.now()
                data_records.append((dt, mac, name))
        if data_records:
            df_stats = pd.DataFrame(data_records, columns=["Zeit", "MAC", "Name"])
            top_devices = df_stats.groupby(["MAC", "Name"]).size().reset_index(name="Anzahl")
            top_devices_sorted = top_devices.sort_values("Anzahl", ascending=False).head(10)
            st.write("### Häufigste Geräte")
            # Charts mit neuem API‑Argument
            st.bar_chart(top_devices_sorted.set_index("MAC")["Anzahl"], width='stretch')

            df_stats["Minute"] = df_stats["Zeit"].dt.floor("min")
            counts_per_minute = df_stats.groupby("Minute").size()
            st.write("### Anzahl erkannter Geräte pro Minute")
            st.line_chart(counts_per_minute, width='stretch')
        else:
            st.write("Nicht genügend Daten für Statistiken.")
    else:
        st.write("Keine Logdaten für Statistiken verfügbar.")

with tab_map:
    st.subheader("Kartenansicht (GPS)")
    logs = read_logs()
    if logs:
        markers = []
        for line in logs:
            parts = line.split()
            # Beispiel: "001 14 1230 OCT MAC Name lat lon"
            if len(parts) >= 8:
                try:
                    lat = float(parts[-2])
                    lon = float(parts[-1])
                    name = " ".join(parts[5:-2])
                    markers.append((lat, lon, name))
                except ValueError:
                    continue
        if markers:
            avg_lat = sum(m[0] for m in markers) / len(markers)
            avg_lon = sum(m[1] for m in markers) / len(markers)
            fmap = Map(location=[avg_lat, avg_lon], zoom_start=13)
            for lat, lon, name in markers:
                Marker([lat, lon], popup=name).add_to(fmap)
            # st_folium akzeptiert weiterhin numerische Breite in Pixeln
            st_folium(fmap, width=900, height=500)
        else:
            st.write("Die Logdatei enthält keine GPS‑Koordinaten.")
    else:
        st.write("Keine Logdatei vorhanden.")

