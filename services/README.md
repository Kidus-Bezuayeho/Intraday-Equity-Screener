# services/

This folder contains the business logic of the application — things like calculating technical indicators and building the data that machine learning models will train on.

## What's here

### `feature_engineering.py`

Takes raw price data (OHLCV bars) and turns it into a table of features that a model can learn from. It also adds a label column (`direction`) that says whether the stock went up or down in the next hour — this is what the model will try to predict.

---

## How to use it

The main function is `build_feature_matrix`. You pass it a DataFrame of hourly OHLCV data (the kind returned by `PolygonTradingDataService.get_hourly_ohlcv`) and it returns a clean, model-ready table.

```python
from services.feature_engineering import build_feature_matrix

# ohlcv is a DataFrame with columns: timestamp, open, high, low, close, volume
features = build_feature_matrix(ohlcv)

# features now has all indicators + a 'direction' column (1 = went up, 0 = went down)
```

You need at least ~40 rows of input data for the indicators to warm up. If you pass too few rows, or an empty DataFrame, it will raise a `ValueError` with a clear message.

---

## Indicators computed

Each indicator becomes one or more columns in the output table.

| Column(s) | What it measures |
|---|---|
| `rsi` | **RSI** — Is the stock overbought (above 70) or oversold (below 30)? Ranges from 0 to 100. |
| `macd_line`, `signal_line`, `histogram` | **MACD** — Are short-term and long-term price trends converging or diverging? The histogram shows the gap between them. |
| `vwap` | **VWAP** — The average price weighted by volume for the current trading day. Resets at midnight each day. |
| `atr` | **ATR** — How volatile is the stock right now? Higher = bigger swings. |
| `bb_upper`, `bb_middle`, `bb_lower` | **Bollinger Bands** — A price range based on recent average and standard deviation. Price near the upper band = extended; near lower = compressed. |
| `return_lag_1` … `return_lag_5` | **Lagged returns** — How much did the price change 1, 2, 3, 4, and 5 hours ago? Gives the model a sense of recent momentum. |
| `direction` | **Label** — 1 if the next hour's close is higher, 0 if lower. This is what the model predicts. |

---

## Individual functions

Each indicator also has its own standalone function if you need just one of them:

```python
from services.feature_engineering import compute_rsi, compute_macd, compute_vwap
# etc.
```

All functions work on plain pandas Series/DataFrames and have no dependency on Polygon or any external API.

---

## Notes

- No internet connection needed — this module only does math on data you already have.
- The last row of input is always dropped because there's no "next hour" to label it.
- Early rows are dropped too (warm-up period while indicators stabilise). The output will have fewer rows than the input — this is expected.
