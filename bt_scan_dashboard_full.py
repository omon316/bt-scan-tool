import streamlit as st
import pandas as pd
import threading
import time
import os
from bluetooth_scan import scan_and_store
from database import get_recent_logs, init_db
import telegram_report

# Setup
st.set_page_config(page_title="BT-Scan Ultimate", layout="wide", page_icon="📡")
init_db()

# Session State Initialisierung
if "scan_running" not in st.session_state:
    st.session_state.scan_running = False
if "stop_event" not in st.session_state:
    st.session_state.stop_event = threading.Event()

# --- Hintergrund Thread ---
def scan_thread_func(stop_event, interval):
    while not stop_event.is_set():
        try:
            devices = scan_and_store()
            if telegram_report.config: # Wenn Config geladen
                 # Nur senden wenn Geräte gefunden (optional Logik anpassbar)
                if devices and len(devices) > 0:
                     # Sende Zusammenfassung statt alle Devices um Spam zu vermeiden
                    telegram_report.send_telegram_message(f"📡 Scan Update: {len(devices)} Geräte gefunden.")
        except Exception as e:
            print(f"Thread Error: {e}")
        
        # Wartezeit in kleinen Häppchen, um Stop schneller zu erkennen
        for _ in range(interval):
            if stop_event.is_set(): break
            time.sleep(1)

# --- UI ---
st.title("📡 BT-Scan Ultimate Dashboard")

# Sidebar
with st.sidebar:
    st.header("⚙️ Steuerung")
    scan_interval = st.number_input("Scan-Intervall (Sek)", min_value=10, value=300)
    
    if not st.session_state.scan_running:
        if st.button("▶️ Auto-Scan Starten", type="primary"):
            st.session_state.scan_running = True
            st.session_state.stop_event.clear()
            t = threading.Thread(target=scan_thread_func, args=(st.session_state.stop_event, scan_interval), daemon=True)
            t.start()
            st.rerun()
    else:
        if st.button("⏹️ Auto-Scan Stoppen", type="secondary"):
            st.session_state.scan_running = False
            st.session_state.stop_event.set()
            st.rerun()
            
    st.markdown("---")
    st.subheader("Telegram Config")
    # Hier könnte man Inputs für API Token einfügen und speichern

# Status Anzeige
status_color = "green" if st.session_state.scan_running else "red"
st.markdown(f"Status: **:{status_color}[{'LÄUFT' if st.session_state.scan_running else 'GESTOPPT'}]**")

# Manueller Scan Button
if st.button("🔍 Sofort-Scan (Einmalig)"):
    with st.spinner("Scanne Umgebung..."):
        results = scan_and_store()
        st.success(f"{len(results)} Geräte gefunden und gespeichert.")

# --- Daten Visualisierung ---
df = get_recent_logs(limit=1000)

if df is not None and not df.empty:
    # Datenaufbereitung
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Tabelle & Filter", "📈 RSSI & Stats", "🗺️ GPS Map"])
    
    with tab1:
        st.subheader("Live Log (Letzte 1000 Einträge)")
        search_term = st.text_input("Suche (MAC, Name, Vendor)")
        
        if search_term:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
            display_df = df[mask]
        else:
            display_df = df
            
        st.dataframe(display_df, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.write("Top Hersteller")
            st.bar_chart(df['vendor'].value_counts())
        with col2:
            st.write("Signalstärke Verlauf (Durchschnitt)")
            # Resample auf Minuten für sauberen Graphen
            rssi_chart = df[df['rssi'] < 0].set_index('timestamp')['rssi'].resample('5min').mean()
            st.line_chart(rssi_chart)

    with tab3:
        st.subheader("Geräte Standorte")
        # Filtern nach Einträgen die GPS Daten haben (nicht None)
        gps_df = df.dropna(subset=['lat', 'lon'])
        gps_df = gps_df[(gps_df['lat'] != 0) & (gps_df['lon'] != 0)] # Leere Nullen filtern
        
        if not gps_df.empty:
            st.map(gps_df, latitude='lat', longitude='lon')
        else:
            st.info("Keine GPS Daten verfügbar. Stelle sicher, dass GPSD läuft.")

else:
    st.warning("Noch keine Daten in der Datenbank.")
