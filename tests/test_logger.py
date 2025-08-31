import os
import pandas as pd
from datetime import datetime

def test_log_csv_tmp(tmp_path):
    # create a tiny row and write to a temp file
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = pd.DataFrame([{"timestamp": ts, "BTC_USDT": 1.23, "ETH_USDT": 4.56}])
    csv_path = tmp_path / "test_prices.csv"
    row.to_csv(csv_path, mode="a", header=True, index=False)

    # append a second row
    ts2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row2 = pd.DataFrame([{"timestamp": ts2, "BTC_USDT": 2.34, "ETH_USDT": 5.67}])
    row2.to_csv(csv_path, mode="a", header=False, index=False)

    assert os.path.exists(csv_path)
    lines = csv_path.read_text().strip().splitlines()
    assert len(lines) == 3
    assert lines[0] == "timestamp,BTC_USDT,ETH_USDT"
