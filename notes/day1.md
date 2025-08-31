## Key Learnings
- Bitcoin vs Ethereum vs USDT (stablecoin)
- Why log market data: backtesting and analysis
- Pipeline: ccxt → fetch ticker → timestamp → append CSV

## Plain-English Script Summary
Fetch BTC/ETH prices from Binance via ccxt every 30s and append
(timestamp, BTC_USDT, ETH_USDT) to crypto_prices.csv.

## Next
- Day 2: load CSV with pandas and plot price over time.
