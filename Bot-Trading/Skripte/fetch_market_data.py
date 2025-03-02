import requests
import feedparser
import websocket
import json
import sqlite3
import threading
import time
import random
from datetime import datetime
from pytrends.request import TrendReq

# 🌍 Datenbankpfad
DB_PATH = r"Z:\Bot-Trading\Datenbanken\trading_data.db"

# 💰 1️⃣ Binance WebSocket für Live-Daten
def on_message(ws, message):
    try:
        data = json.loads(message)
        if isinstance(data, list):
            for item in data:
                save_binance_data(item["s"], float(item["c"]))
        else:
            save_binance_data(data["s"], float(data["c"]))
    except Exception as e:
        print(f"[ERROR] Fehler im Binance WebSocket: {e}")

def save_binance_data(symbol, price):
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
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/!ticker@arr", on_message=on_message)
    ws.run_forever()

# 📊 2️⃣ CoinGecko API für Marktupdates
def fetch_market_data():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("[WARNUNG] Fehler beim Abrufen der Marktdaten!")
        return None

def save_market_data(data):
    if data:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS market_data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp TEXT,
                            symbol TEXT,
                            price REAL)''')
        for asset, values in data.items():
            cursor.execute("INSERT INTO market_data (timestamp, symbol, price) VALUES (?, ?, ?)",
                           (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), asset.upper(), values["usd"]))
        conn.commit()
        conn.close()
        print("[INFO] Marktdaten erfolgreich gespeichert.")

# 📰 3️⃣ Krypto-Nachrichten
def fetch_crypto_news():
    rss_feeds = ["https://cointelegraph.com/rss", "https://cryptoslate.com/feed/"]
    news = []
    for feed_url in rss_feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            news.append({"title": entry.title, "link": entry.link, "published": entry.published})
    return news

def save_crypto_news(news):
    if news:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS crypto_news (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp TEXT,
                            title TEXT,
                            link TEXT)''')
        for article in news:
            cursor.execute("INSERT INTO crypto_news (timestamp, title, link) VALUES (?, ?, ?)",
                           (article["published"], article["title"], article["link"]))
        conn.commit()
        conn.close()
        print("[INFO] Krypto-Nachrichten gespeichert.")

# 🔍 4️⃣ Google Trends
def fetch_google_trends():
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        keywords = ["Bitcoin", "Ethereum"]
        pytrends.build_payload(keywords, cat=0, timeframe='now 1-H')
        trends = pytrends.interest_over_time()
        return trends.tail(1).to_dict() if not trends.empty else None
    except Exception as e:
        print(f"[WARNUNG] Google Trends Anfrage fehlgeschlagen: {e}")
        return None

def save_google_trends(trends):
    if trends:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS google_trends (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp TEXT,
                            keyword TEXT,
                            trend_value INTEGER)''')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for keyword, trend_value in trends.items():
            cursor.execute("INSERT INTO google_trends (timestamp, keyword, trend_value) VALUES (?, ?, ?)",
                           (timestamp, keyword, trend_value[list(trend_value.keys())[0]]))
        conn.commit()
        conn.close()
        print("[INFO] Google Trends gespeichert.")

# ⏳ 5️⃣ Automatische Updates
def scheduled_updates():
    last_google_trends_time = 0
    while True:
        print("[INFO] Abrufen der Marktdaten & News...")
        save_market_data(fetch_market_data())
        save_crypto_news(fetch_crypto_news())
        if time.time() - last_google_trends_time > 600:
            save_google_trends(fetch_google_trends())
            last_google_trends_time = time.time()
        print("[INFO] Alle Daten wurden aktualisiert!")
        time.sleep(random.randint(30, 90))

# 🚀 Start
if __name__ == "__main__":
    threading.Thread(target=start_binance_websocket, daemon=True).start()
    threading.Thread(target=scheduled_updates, daemon=True).start()
    while True:
        time.sleep(1)
