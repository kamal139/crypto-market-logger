import os
from typing import Tuple
import pandas as pd

# Reuse analysis helpers
from analysis import (
    load_prices, add_sma, add_rsi,
    plot_price_with_mas,  # optional reuse
)

def prepare_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure SMA(20) and RSI(14) exist."""
    out = add_sma(df, "BTC_USDT", windows=(5, 20))
    out = add_rsi(out, "BTC_USDT", period=14)
    return out

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Simple long-only logic:
      - BUY when RSI < 30 and price > SMA_20
      - SELL when RSI > 70
      - HOLD otherwise
    Outputs a 'signal' column in { 'BUY', 'SELL', '' } and a 'position' in {0,1}.
    """
    out = df.copy()
    if "SMA_20" not in out.columns or "RSI_14" not in out.columns:
        out = prepare_indicators(out)

    out["signal"] = ""
    buy_cond  = (out["RSI_14"] < 30) & (out["BTC_USDT"] > out["SMA_20"])
    sell_cond = (out["RSI_14"] > 70)

    out.loc[buy_cond, "signal"]  = "BUY"
    out.loc[sell_cond, "signal"] = "SELL"

    # Position (long-only, flip on signals)
    position = []
    pos = 0
    for s in out["signal"]:
        if s == "BUY":
            pos = 1
        elif s == "SELL":
            pos = 0
        position.append(pos)
    out["position"] = position
    return out

def backtest_long_only(df: pd.DataFrame, fee_bps: float = 10.0) -> pd.DataFrame:
    """
    Long-only backtest using close-to-close returns when in position.
    fee_bps: per-trade fee in basis points (10 bps = 0.10% per entry/exit).
    Assumes fills at next bar's close after signal (simplification).
    """
    out = df.copy()
    if "position" not in out.columns:
        out = generate_signals(out)

    out = out.sort_values("timestamp").reset_index(drop=True)
    price = out["BTC_USDT"].astype(float)
    out["ret"] = price.pct_change().fillna(0.0)

    # Apply returns only when in position
    out["strategy_ret"] = out["position"].shift(1).fillna(0) * out["ret"]

    # Fees on position changes (entry/exit)
    pos_change = out["position"].diff().fillna(0).abs()
    fee = fee_bps / 10000.0
    out["strategy_ret"] -= pos_change * fee

    out["equity"] = (1.0 + out["strategy_ret"]).cumprod()
    return out

def save_signals_csv(df_bt: pd.DataFrame, path: str = "outputs/signals.csv") -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cols = ["timestamp", "BTC_USDT", "SMA_20", "RSI_14", "signal", "position", "strategy_ret", "equity"]
    have = [c for c in cols if c in df_bt.columns]
    df_bt[have].to_csv(path, index=False)
    return path

def plot_price_with_signals(df_bt: pd.DataFrame, out_file: str = "charts/day4_price_signals.png") -> str:
    """
    Overlay BUY/SELL markers on price with SMA(20).
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    dfp = df_bt.sort_values("timestamp")
    t = dfp["timestamp"]
    p = dfp["BTC_USDT"]
    sma = dfp["SMA_20"] if "SMA_20" in dfp.columns else None

    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(t, p, label="BTC", linewidth=1.2)
    if sma is not None:
        ax.plot(t, sma, label="SMA_20", linewidth=1.0)

    buys = dfp[dfp["signal"] == "BUY"]
    sells = dfp[dfp["signal"] == "SELL"]
    ax.scatter(buys["timestamp"], buys["BTC_USDT"], marker="^", s=70, label="BUY")
    ax.scatter(sells["timestamp"], sells["BTC_USDT"], marker="v", s=70, label="SELL")

    ax.set_title("BTC with Signals (Day 4)")
    ax.set_xlabel("Time"); ax.set_ylabel("Price (USDT)"); ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%d-%b"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=8))
    fig.tight_layout()
    fig.savefig(out_file)
    plt.close(fig)
    return out_file

def run(csv_path: str = "crypto_prices.csv") -> Tuple[str, str]:
    df = load_prices(csv_path)
    df_s = generate_signals(df)
    df_bt = backtest_long_only(df_s, fee_bps=10.0)
    sig_csv = save_signals_csv(df_bt, "outputs/signals.csv")
    chart = plot_price_with_signals(df_bt, "charts/day4_price_signals.png")
    return sig_csv, chart

if __name__ == "__main__":
    p, c = run("crypto_prices.csv")
    print("✅ Saved:", p, "and", c)
