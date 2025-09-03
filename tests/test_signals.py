import os
import pandas as pd
from strategy import generate_signals, backtest_long_only, save_signals_csv, plot_price_with_signals

def _toy():
    # build a simple ramp so RSI and SMA exist; 60 rows = enough for RSI
    return pd.DataFrame({
        "timestamp": pd.date_range("2025-09-03 10:00:00", periods=60, freq="min"),
        "BTC_USDT": [50000 + i*5 for i in range(60)],
        "ETH_USDT": [3000 + i for i in range(60)],
    })

def test_generate_signals_has_cols():
    df = _toy()
    out = generate_signals(df)
    for col in ["SMA_20", "RSI_14", "signal", "position"]:
        assert col in out.columns

def test_backtest_has_equity_and_ret():
    df = _toy()
    sig = generate_signals(df)
    bt = backtest_long_only(sig, fee_bps=10.0)
    assert "strategy_ret" in bt and "equity" in bt
    assert bt["equity"].iloc[0] > 0

def test_outputs_written(tmp_path):
    df = _toy()
    sig = generate_signals(df)
    bt = backtest_long_only(sig)
    p = tmp_path / "signals.csv"
    c = tmp_path / "chart.png"
    # Save and plot
    save_signals_csv(bt, path=str(p))
    plot_price_with_signals(bt, out_file=str(c))
    assert os.path.exists(p) and os.path.getsize(p) > 0
    assert os.path.exists(c) and os.path.getsize(c) > 0
