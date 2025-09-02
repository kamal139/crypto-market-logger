import os
import time
from datetime import datetime

import ccxt
import pandas as pd

# Always resolve CSV path relative to this script's folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "crypto_prices.csv")


def fetch_prices(exchange):
    """Fetch the latest BTC and ETH prices in USDT from Binance."""
    btc_price = exchange.fetch_ticker("BTC/USDT")["last"]
    eth_price = exchange.fetch_ticker("ETH/USDT")["last"]
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "BTC_USDT": btc_price,
        "ETH_USDT": eth_price,
    }


def append_row(row: dict):
    """Append one row of prices to crypto_prices.csv inside project root."""
    df = pd.DataFrame([row], columns=["timestamp", "BTC_USDT", "ETH_USDT"])
    df.to_csv(
        CSV_PATH,
        mode="a",
        header=not os.path.exists(CSV_PATH),
        index=False,
    )


def log_prices(interval_sec: int = 30):
    """Continuously log prices every N seconds."""
    exchange = ccxt.binance()
    print(f"📈 Logging to {CSV_PATH} (Ctrl+C to stop)")

    while True:
        try:
            row = fetch_prices(exchange)
            append_row(row)
            print(f"✅ {row['timestamp']} | BTC: {row['BTC_USDT']} | ETH: {row['ETH_USDT']}")
            time.sleep(interval_sec)
        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(10)  # backoff before retrying


if __name__ == "__main__":
    log_prices()
