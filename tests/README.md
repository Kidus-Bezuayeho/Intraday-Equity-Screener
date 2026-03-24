# tests/

This folder contains all the automated tests for the project. Run them to check that everything is working correctly after making changes.

## Running the tests

Make sure you're in the project root and the virtual environment is active:

```bash
source equity_screener_env/bin/activate

# Run all tests
pytest tests/ -v

# Run just the feature engineering tests (no API key needed)
pytest tests/test_feature_engineering.py -v

# Run just the Polygon API tests (requires POLYGON_API_KEY in .env)
pytest tests/test_polygon_service.py -v -s
pytest tests/test_polygon_ohlcv.py -v -s
```

---

## Test files

### `test_feature_engineering.py`
Tests for the indicator calculations in `services/feature_engineering.py`. These tests run entirely with made-up data — no internet connection or API key required.

**What's tested:**
- RSI values are always between 0 and 100
- MACD histogram always equals `macd_line - signal_line`
- VWAP resets at the start of each new trading day
- ATR is always zero or positive
- Bollinger upper band is always above the middle, middle always above lower
- Bollinger middle band exactly matches a 20-period rolling average
- Lagged returns produce the right number of columns with the right names
- Direction label contains only 0s and 1s (no in-between values)
- The last row of input produces NaN for the direction label (since there's no "next hour")
- `build_feature_matrix` output has zero missing values
- `build_feature_matrix` raises a clear error if you pass too little data
- `build_feature_matrix` raises a clear error if you pass an empty DataFrame

### `test_polygon_service.py`
Tests for the original methods in `PolygonTradingDataService` — things like bid/ask spread, order imbalance, and trade volume. These make real API calls, so they're automatically skipped if `POLYGON_API_KEY` is not set in your environment.

### `test_polygon_ohlcv.py`
Tests specifically for the `get_hourly_ohlcv` method added in Stage 2. Also makes real API calls and is skipped without an API key.

**What's tested:**
- The method returns a DataFrame (not None or a list)
- The DataFrame has all the expected columns
- Rows are sorted oldest-first
- Timestamps include timezone information (UTC)
- Passing a weekend date range returns an empty DataFrame without crashing
- Works correctly for multiple different tickers

---

## A note on API tests

Any test that calls the Polygon.io API is designed to **skip gracefully** if you don't have an API key — you'll see `SKIPPED` in the output rather than a failure. To run them, add your key to the `.env` file in the project root:

```
POLYGON_API_KEY=your_key_here
```
