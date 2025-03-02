import sqlite3
import json
import time
from datetime import datetime

# 📂 Datei-Pfade
BINANCE_RULES_PATH = "Z:/Bot-Trading/Backups/binance_trading_rules.json"
SIGNALS_PATH = "Z:/Bot-Trading/Signale/signals.json"
DB_PATH = "Z:/Bot-Trading/Datenbanken/trading_data_binance_live.db"

# 📥 Binance-Handelsregeln laden (UTF-8 BOM fix)
def load_binance_rules():
    """ Lädt Binance-Handelsregeln aus der JSON-Datei und entfernt ggf. UTF-8 BOM. """
    try:
        with open(BINANCE_RULES_PATH, "r", encoding="utf-8-sig") as file:  # <- Ändere utf-8 zu utf-8-sig
            rules = json.load(file)
            return {rule["Symbol"]: rule for rule in rules} if rules else {}
    except json.JSONDecodeError:
        print("[ERROR] ❌ JSON-Fehler! Datei ist beschädigt oder hat falsches Format.")
    except FileNotFoundError:
        print("[ERROR] ❌ Binance-Regeln-Datei nicht gefunden.")
    except Exception as e:
        print(f"[ERROR] ❌ Fehler beim Laden der Binance-Regeln: {e}")
    return {}

# 📥 Neueste Trading-Daten abrufen
def get_latest_trading_data():
    """ Holt die neuesten 200 Einträge aus der SQLite-Datenbank. """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, symbol, price FROM binance_live_data ORDER BY timestamp DESC LIMIT 200")
        data = cursor.fetchall()
        conn.close()
        return [{"timestamp": row[0], "symbol": row[1], "price": row[2]} for row in data]
    except Exception as e:
        print(f"[ERROR] ❌ Fehler beim Laden der Trading-Daten: {e}")
        return []

# 📊 Signale optimieren & anpassen
def optimize_signals():
    """ Erstellt optimierte Signale basierend auf Binance-Regeln & Trading-Daten. """
    print("[INFO] 🔍 Prüfe und optimiere Signale...")
    
    rules = load_binance_rules()
    if not rules:
        print("[ERROR] ❌ Keine Binance-Regeln gefunden. Breche ab.")
        return

    trading_data = get_latest_trading_data()
    if not trading_data:
        print("[ERROR] ❌ Keine Trading-Daten gefunden. Breche ab.")
        return

    # 🔎 Berechne die Coins mit der größten Preisänderung
    symbol_changes = {}
    for row in trading_data:
        symbol = row["symbol"]
        if symbol not in symbol_changes:
            symbol_changes[symbol] = []
        symbol_changes[symbol].append(row["price"])

    # Sortiere nach prozentualer Preisänderung
    sorted_symbols = sorted(symbol_changes.items(), key=lambda x: (x[1][-1] - x[1][0]) / x[1][0], reverse=True)
    top_10 = sorted_symbols[:10]

    signals = []
    
    for symbol, prices in top_10:
        if symbol not in rules:
            print(f"[WARNING] ⚠️ Kein Symbol-Info für {symbol} gefunden, überspringe.")
            continue

        price = prices[-1]  # Letzter Preis
        rule = rules[symbol]

        min_qty = float(rule["LOT_SIZE"])
        min_notional = float(rule["NOTIONAL"])
        
        quantity = round(min_notional / price, 8)  # Berechnung der Menge

        # Falls die Menge zu klein ist, auf Mindestmenge setzen
        if quantity < min_qty:
            quantity = min_qty
        
        signal = {
            "symbol": symbol,
            "action": "BUY",
            "price": price,
            "quantity": quantity
        }
        signals.append(signal)
        print(f"[TRADE] 🔹 Optimiertes Signal: {signal}")

    # Speichere die Signale
    with open(SIGNALS_PATH, "w", encoding="utf-8") as file:
        json.dump(signals, file, indent=4)
    
    print(f"[INFO] 📄 {len(signals)} gültige Signale gespeichert.")

# 🔄 Dauerschleife für den Bot
def run_continuously():
    """ Führt die Strategie kontinuierlich aus. """
    print("[INFO] 🏁 Starte den kontinuierlichen Modus...\n")
    while True:
        optimize_signals()
        print("[INFO] ⏳ Warte 10 Sekunden auf neue Daten...\n")
        time.sleep(10)

if __name__ == "__main__":
    run_continuously()
