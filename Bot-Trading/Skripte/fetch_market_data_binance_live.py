import websocket
import sqlite3
import json
import time
from datetime import datetime
import threading

# 🌍 Datenbankpfad
DB_PATH = r"Z:/Bot-Trading/Datenbanken/trading_data_binance_live.db"

# WebSocket Callbacks
def on_error(ws, error):
    print(f"[ERROR] WebSocket-Fehler: {error}")
    reconnect_websocket()

def on_close(ws, close_status_code, close_msg):
    print("[INFO] WebSocket-Verbindung geschlossen.")
    reconnect_websocket()

def reconnect_websocket():
    print("[INFO] Starte WebSocket neu...")
    time.sleep(5)
    start_binance_websocket()

def on_message(ws, message):
    try:
        data = json.loads(message)
        if isinstance(data, list):
            for item in data:
                save_to_database(item["s"], float(item["c"]))
        else:
            save_to_database(data["s"], float(data["c"]))
    except Exception as e:
        print(f"[ERROR] Fehler beim Verarbeiten der Binance-Daten: {e}")
        reconnect_websocket()

def save_to_database(symbol, price):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS binance_live_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        symbol TEXT,
                        price REAL)''')
    cursor.execute("INSERT INTO binance_live_data (timestamp, symbol, price) VALUES (?, ?, ?)",
                   (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, price))
    conn.commit()
    conn.close()
    print(f"[LIVE] {symbol}: {price} USD gespeichert!")

def start_binance_websocket():
    print("[INFO] Starte Binance WebSocket für Live-Daten...")
    try:
        ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/!ticker@arr", 
                                    on_message=on_message, on_error=on_error, on_close=on_close)
        ws.run_forever()
    except Exception as e:
        print(f"[ERROR] Fehler beim Starten des WebSockets: {e}")
        reconnect_websocket()

# Start
if __name__ == "__main__":
    threading.Thread(target=start_binance_websocket, daemon=True).start()
    while True:
        time.sleep(1)
