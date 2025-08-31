import os
import ccxt
import pandas as pd
from datetime import datetime

def test_exchange_connection():
    exchange = ccxt.binance()
    ticker = exchange.fetch_ticker('BTC/USDT')
    assert "last" in ticker
    assert isinstance(ticker["last"], (int, float))

def test_log_csv():
    # run one logging step manually
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "timestamp": [timestamp],
        "BTC_USDT": [50000],
        "ETH_USDT": [3000]
    }
    df = pd.DataFrame(data)
    filename = "test_crypto_prices.csv"
    df.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)

    # check file was written
    assert os.path.exists(filename)
    loaded = pd.read_csv(filename)
    assert "BTC_USDT" in loaded.columns
    assert "ETH_USDT" in loaded.columns

    # cleanup
    os.remove(filename)
