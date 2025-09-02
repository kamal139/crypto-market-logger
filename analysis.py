# analysis.py
import os
import pandas as pd

# Use a backend that works in headless/CI environments
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplfinance as mpf


def load_prices(csv_path: str = "crypto_prices.csv") -> pd.DataFrame:
    """Load the CSV into a DataFrame, parsing timestamp if present."""
    df = pd.read_csv(csv_path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def basic_stats(df: pd.DataFrame) -> dict:
    """Return simple statistics for BTC and ETH columns."""
    return {
        "BTC_USDT": {
            "min": float(df["BTC_USDT"].min()),
            "max": float(df["BTC_USDT"].max()),
            "mean": float(df["BTC_USDT"].mean()),
        },
        "ETH_USDT": {
            "min": float(df["ETH_USDT"].min()),
            "max": float(df["ETH_USDT"].max()),
            "mean": float(df["ETH_USDT"].mean()),
        },
    }


def plot_prices(df: pd.DataFrame, output_file: str = "charts/day2_line.png") -> str:
    """Generate a line chart for BTC & ETH vs time."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.plot(df["timestamp"], df["BTC_USDT"], label="BTC")
    plt.plot(df["timestamp"], df["ETH_USDT"], label="ETH")
    plt.xlabel("Time")
    plt.ylabel("Price (USDT)")
    plt.title("BTC vs ETH over time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    return output_file


def plot_candles(df: pd.DataFrame, output_file: str = "charts/day2_btc_candles.png") -> str:
    """Create a simple candlestick chart for BTC (mocked OHLC from Close)."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Build OHLC from Close-only prices
    ohlc = df[["timestamp", "BTC_USDT"]].copy()
    ohlc = ohlc.rename(columns={"BTC_USDT": "Close"})
    ohlc["Open"] = ohlc["Close"]
    ohlc["High"] = ohlc["Close"]
    ohlc["Low"] = ohlc["Close"]
    ohlc = ohlc.set_index("timestamp")

    mpf.plot(ohlc, type="candle", style="charles", savefig=output_file)
    return output_file


if __name__ == "__main__":
    data = load_prices()
    print("📊 Stats:", basic_stats(data))
    plot_prices(data)
    plot_candles(data)
    print("✅ Charts saved in charts/")
