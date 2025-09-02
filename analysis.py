# analysis.py
# Hardened analysis with sanity checks, indicators, and CLI flags.

import os
import argparse
from typing import Tuple, Iterable

import pandas as pd

# Headless backend so it works in CI/terminal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Candles are optional (we'll warn if missing)
try:
    import mplfinance as mpf  # type: ignore
    HAS_MPF = True
except Exception:
    HAS_MPF = False


# --------- Core Loading & Validation ---------
def resolve_path(path: str) -> str:
    """Resolve path relative to this file if not absolute."""
    if os.path.isabs(path):
        return path
    # Use project root (folder of this file) as base
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, path)

def load_prices(csv_path: str = "crypto_prices.csv") -> pd.DataFrame:
    """Load CSV and parse timestamp."""
    path = resolve_path(csv_path)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"CSV not found at {path}. "
            f"Tip: run price_tracker.py first or pass --csv /full/path.csv"
        )
    df = pd.read_csv(path)
    if "timestamp" not in df.columns:
        raise ValueError(f"'timestamp' column missing in {path}. Columns: {list(df.columns)}")
    # Parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    # Basic required columns
    for col in ("BTC_USDT", "ETH_USDT"):
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' missing. Columns present: {list(df.columns)}")
    # Drop completely malformed rows
    df = df.dropna(subset=["timestamp", "BTC_USDT", "ETH_USDT"])
    # Sort by time just in case
    df = df.sort_values("timestamp").reset_index(drop=True)
    if len(df) == 0:
        raise ValueError("CSV loaded but after cleaning there are 0 rows. Need some data to plot.")
    return df

def basic_stats(df: pd.DataFrame) -> dict:
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


# --------- Indicators ---------
def add_sma(df: pd.DataFrame, col="BTC_USDT", windows: Iterable[int] = (5, 20)) -> pd.DataFrame:
    out = df.copy()
    for w in windows:
        out[f"SMA_{w}"] = out[col].rolling(window=w, min_periods=1).mean()
    return out

def add_rsi(df: pd.DataFrame, col="BTC_USDT", period: int = 14) -> pd.DataFrame:
    out = df.copy()
    if len(out) < 2:
        out[f"RSI_{period}"] = pd.NA
        return out
    delta = out[col].diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    # Wilder’s smoothing approximation using EMA for robustness
    avg_gain = gain.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    rs = avg_gain / (avg_loss.replace(0, 1e-12))
    out[f"RSI_{period}"] = 100 - (100 / (1 + rs))
    return out


# --------- Plotting ---------
def _ensure_dir(out_file: str) -> None:
    d = os.path.dirname(str(out_file)) or "."
    os.makedirs(d, exist_ok=True)

def _format_time_axis(ax):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%d-%b"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=8))
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

def plot_price_with_mas(df: pd.DataFrame, out_file: str = "charts/day3_price_ma.png") -> str:
    _ensure_dir(out_file)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(df["timestamp"], df["BTC_USDT"], label="BTC", linewidth=1.2)
    for w in (5, 20):
        col = f"SMA_{w}"
        if col in df.columns:
            ax.plot(df["timestamp"], df[col], label=col, linewidth=1.0)
    ax.set_title("BTC/USDT with SMA(5, 20)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price (USDT)")
    ax.legend()
    _format_time_axis(ax)
    fig.tight_layout()
    fig.savefig(out_file)
    plt.close(fig)
    return out_file

def plot_rsi(df: pd.DataFrame, out_file: str = "charts/day3_rsi.png", period: int = 14) -> str:
    _ensure_dir(out_file)
    rsi_col = f"RSI_{period}"
    if rsi_col not in df.columns:
        raise ValueError(f"{rsi_col} not found. Did you run add_rsi(period={period})?")
    fig, ax = plt.subplots(figsize=(11, 3))
    ax.plot(df["timestamp"], df[rsi_col], label=rsi_col, linewidth=1.2)
    ax.axhline(70, linestyle="--")
    ax.axhline(30, linestyle="--")
    ax.set_ylim(0, 100)
    ax.set_title(f"RSI({period})")
    ax.set_xlabel("Time")
    ax.set_ylabel("RSI")
    _format_time_axis(ax)
    fig.tight_layout()
    fig.savefig(out_file)
    plt.close(fig)
    return out_file

# Day-2 compatibility wrappers (so old tests still pass)
def plot_prices(df: pd.DataFrame, output_file: str = "charts/day2_line.png") -> str:
    _ensure_dir(output_file)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["timestamp"], df["BTC_USDT"], label="BTC", linewidth=1.2)
    ax.plot(df["timestamp"], df["ETH_USDT"], label="ETH", linewidth=1.2)
    ax.set_xlabel("Time")
    ax.set_ylabel("Price (USDT)")
    ax.set_title("BTC vs ETH over time")
    ax.legend()
    _format_time_axis(ax)
    fig.tight_layout()
    fig.savefig(output_file)
    plt.close(fig)
    return output_file

def plot_candles(df: pd.DataFrame, output_file: str = "charts/day2_btc_candles.png") -> str:
    if not HAS_MPF:
        raise RuntimeError("mplfinance is required for plot_candles; install with: pip install mplfinance")
    _ensure_dir(output_file)
    ohlc = df[["timestamp", "BTC_USDT"]].copy()
    ohlc = ohlc.rename(columns={"BTC_USDT": "Close"})
    # Mock OHLC from close-only stream
    ohlc["Open"] = ohlc["Close"]
    ohlc["High"] = ohlc["Close"]
    ohlc["Low"]  = ohlc["Close"]
    ohlc = ohlc.set_index("timestamp")
    mpf.plot(ohlc, type="candle", style="charles", savefig=output_file)
    return output_file


# --------- CLI & Self-Check ---------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze crypto CSV with indicators and charts")
    p.add_argument("--csv", default="crypto_prices.csv", help="Path to CSV (default: crypto_prices.csv)")
    p.add_argument("--outdir", default="charts", help="Output directory for charts")
    p.add_argument("--sma", default="5,20", help="SMA windows, comma-separated (default: 5,20)")
    p.add_argument("--rsi", type=int, default=14, help="RSI period (default: 14)")
    p.add_argument("--limit", type=int, default=0, help="Use only last N rows (0 = all)")
    p.add_argument("--no-candles", action="store_true", help="Skip candlestick chart")
    p.add_argument("--selfcheck", action="store_true", help="Run environment/CSV checks and exit")
    return p.parse_args()

def selfcheck(csv: str) -> None:
    path = resolve_path(csv)
    print("🔎 Self-check")
    print("  CWD:", os.getcwd())
    print("  Script dir:", os.path.dirname(os.path.abspath(__file__)))
    print("  CSV path:", path, "| exists:", os.path.exists(path))
    if os.path.exists(path):
        try:
            df = load_prices(csv)
            print("  Rows:", len(df), "| Columns:", list(df.columns))
            print("  Head:\n", df.head(3))
            print("  Dtypes:\n", df.dtypes)
        except Exception as e:
            print("  Failed to load CSV:", e)
    print("  mplfinance installed:", HAS_MPF)

def main():
    args = parse_args()
    if args.selfcheck:
        selfcheck(args.csv)
        return

    df = load_prices(args.csv)
    if args.limit and args.limit > 0:
        df = df.tail(args.limit).reset_index(drop=True)

    # Indicators
    windows = tuple(int(w.strip()) for w in args.sma.split(",") if w.strip())
    df = add_sma(df, "BTC_USDT", windows=windows)
    df = add_rsi(df, "BTC_USDT", period=args.rsi)

    # Plots
    out_price = os.path.join(args.outdir, "day3_price_ma.png")
    out_rsi   = os.path.join(args.outdir, "day3_rsi.png")
    plot_price_with_mas(df, out_price)
    plot_rsi(df, out_rsi, period=args.rsi)

    if not args.no_candles:
        try:
            plot_candles(df, os.path.join(args.outdir, "day2_btc_candles.png"))
        except Exception as e:
            print("⚠️ Skipping candles:", e)

    print("📊 Stats:", basic_stats(df))
    print(f"✅ Saved: {out_price} and {out_rsi}")
    if not args.no_candles:
        print(f"🕯️ Candles: {os.path.join(args.outdir, 'day2_btc_candles.png')}")

if __name__ == "__main__":
    main()
