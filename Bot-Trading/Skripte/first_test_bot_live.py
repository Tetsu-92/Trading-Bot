from binance.client import Client
import json
import time
import os

# API-Schlüssel laden
def load_api_keys():
    with open("Z:/Bot-Trading/API_Keys/binance_bot_api.json", "r") as file:
        data = json.load(file)
    return data["api_key"], data["api_secret"]

api_key, api_secret = load_api_keys()
client = Client(api_key, api_secret)

# Lade validierte Signale
def load_validated_signals():
    with open("Z:/Bot-Trading/Signale/validated_signals.json", "r") as file:
        return json.load(file)

# Order ausführen
def execute_trade(signal):
    symbol = signal["symbol"]
    action = signal["action"]
    quantity = signal["quantity"]
    price = signal["price"]

    try:
        if action == "BUY":
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
        elif action == "SELL":
            order = client.order_market_sell(symbol=symbol, quantity=quantity)
        else:
            print(f"[ERROR] ❌ Ungültige Aktion: {action}")
            return
        
        print(f"[SUCCESS] ✅ Order {action} {quantity} {symbol} erfolgreich!")
        log_trade(action, symbol, quantity, price)

    except Exception as e:
        print(f"[ERROR] ❌ Fehler bei Order {action} {symbol}: {e}")

# Handelslog speichern
def log_trade(action, symbol, quantity, price):
    log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {action} {quantity} {symbol} @ {price}\n"
    with open("Z:/Bot-Trading/Backups/trading_log.txt", "a") as file:
        file.write(log_entry)

# Hauptfunktion
def run_trading_bot():
    print("[INFO] 🏁 Starte den Trading-Bot...")
    while True:
        signals = load_validated_signals()
        for signal in signals:
            execute_trade(signal)
        print("[INFO] 📊 Warte 10 Sekunden auf nächste Signale...")
        time.sleep(10)

if __name__ == "__main__":
    run_trading_bot()
