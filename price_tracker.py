import ccxt
import pandas as pd
from datetime import datetime
import time
import os

# Initialize exchange
exchange = ccxt.binance()

# Ensure file exists with headers
filename = "crypto_prices.csv"
if not os.path.exists(filename):
    df = pd.DataFrame(columns=["timestamp", "BTC_USDT", "ETH_USDT"])
    df.to_csv(filename, index=False)

while True:
    try:
        # Fetch BTC & ETH prices
        btc = exchange.fetch_ticker('BTC/USDT')
        eth = exchange.fetch_ticker('ETH/USDT')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare data row
        data = {
            "timestamp": [timestamp],
            "BTC_USDT": [btc['last']],
            "ETH_USDT": [eth['last']]
        }

        df = pd.DataFrame(data)
        df.to_csv(filename, mode='a', header=False, index=False)

        print(f"✅ {timestamp} | BTC: {btc['last']} | ETH: {eth['last']} saved")
        time.sleep(30)  # fetch every 30 sec

    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(10)