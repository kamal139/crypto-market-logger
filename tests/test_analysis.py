import os
import pandas as pd
from analysis import load_prices, basic_stats, plot_prices, plot_candles

def test_load_prices_from_temp_csv(tmp_path):
    # Make a tiny CSV in a temp dir
    csv_path = tmp_path / "prices.csv"
    df_in = pd.DataFrame({
        "timestamp": pd.date_range("2025-08-31 12:00:00", periods=3, freq="min"),
        "BTC_USDT": [50000.0, 50100.0, 50200.0],
        "ETH_USDT": [3000.0, 3010.0, 3020.0],
    })
    df_in.to_csv(csv_path, index=False)

    # load_prices should parse the timestamp to datetime
    df_out = load_prices(str(csv_path))
    assert list(df_out.columns) == ["timestamp", "BTC_USDT", "ETH_USDT"]
    assert pd.api.types.is_datetime64_ns_dtype(df_out["timestamp"])
    assert len(df_out) == 3

def test_basic_stats_returns_expected_numbers():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-08-31 12:00:00", periods=3, freq="min"),
        "BTC_USDT": [50000.0, 50100.0, 50200.0],
        "ETH_USDT": [3000.0, 3010.0, 3020.0],
    })
    stats = basic_stats(df)
    assert stats["BTC_USDT"]["min"] == 50000.0
    assert stats["BTC_USDT"]["max"] == 50200.0
    assert stats["BTC_USDT"]["mean"] == 50100.0
    assert stats["ETH_USDT"]["min"] == 3000.0
    assert stats["ETH_USDT"]["max"] == 3020.0
    assert stats["ETH_USDT"]["mean"] == 3010.0

def test_plot_prices_creates_png(tmp_path):
    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-08-31 12:00:00", periods=5, freq="min"),
        "BTC_USDT": [50000, 50100, 50200, 50300, 50400],
        "ETH_USDT": [3000, 3010, 3020, 3030, 3040],
    })
    out = tmp_path / "line.png"
    path = plot_prices(df, output_file=str(out))
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0

def test_plot_candles_creates_png(tmp_path):
    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-08-31 12:00:00", periods=5, freq="min"),
        "BTC_USDT": [50000, 50100, 50200, 50300, 50400],
        "ETH_USDT": [3000, 3010, 3020, 3030, 3040],
    })
    out = tmp_path / "candle.png"
    path = plot_candles(df, output_file=str(out))
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0
