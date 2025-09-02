import os
import pandas as pd
from analysis import add_sma, add_rsi, plot_price_with_mas, plot_rsi

def _df():
    return pd.DataFrame({
        "timestamp": pd.date_range("2025-09-01 10:00:00", periods=30, freq="min"),
        "BTC_USDT": [50000 + i*10 for i in range(30)],
        "ETH_USDT": [3000 + i for i in range(30)],
    })

def test_add_sma_shapes():
    df = add_sma(_df(), "BTC_USDT", windows=(5,20))
    assert "SMA_5" in df and "SMA_20" in df
    assert len(df["SMA_5"]) == len(df) and len(df["SMA_20"]) == len(df)

def test_add_rsi_range():
    df = add_rsi(_df(), "BTC_USDT", period=14)
    col = "RSI_14"
    assert col in df
    assert df[col].dropna().between(0,100).all()

def test_plot_price_and_rsi(tmp_path):
    df = _df()
    df = add_sma(df, "BTC_USDT", windows=(5,20))
    df = add_rsi(df, "BTC_USDT", period=14)
    f1 = tmp_path / "ma.png"
    f2 = tmp_path / "rsi.png"
    path1 = plot_price_with_mas(df, out_file=str(f1))
    path2 = plot_rsi(df, out_file=str(f2), period=14)
    assert os.path.exists(path1) and os.path.getsize(path1) > 0
    assert os.path.exists(path2) and os.path.getsize(path2) > 0
