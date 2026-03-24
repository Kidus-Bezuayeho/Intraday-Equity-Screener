# external/

This folder contains code that talks to outside data sources — specifically the Polygon.io market data API.

## What's here

### `polygon_trading_data.py`

A single class, `PolygonTradingDataService`, that wraps the Polygon.io REST API. You create one instance and call its methods to pull different types of market data.

**Setup:** The class reads your API key from a `.env` file in the project root. Make sure `POLYGON_API_KEY=your_key_here` is in that file before using it.

```python
from external.polygon_trading_data import PolygonTradingDataService

service = PolygonTradingDataService()
```

---

## Methods

### `get_hourly_ohlcv(ticker, from_date, to_date)`
The main method used by the ML pipeline. Fetches hourly price bars (Open, High, Low, Close, Volume) for a stock over a date range.

```python
df = service.get_hourly_ohlcv("AAPL", "2024-12-01", "2024-12-31")
# Returns a DataFrame with columns: timestamp, open, high, low, close, volume
# Rows are sorted oldest-first. Timestamps are in UTC.
```

Returns an empty DataFrame (not an error) if no data is available for the range.

---

### `get_trade_volume_data(ticker)`
Fetches tick-level trade data for a single day and summarises it: total shares traded, average price, number of trades, and the most recent trade price.

### `get_bid_ask_spread(ticker)`
Returns the current best bid and ask prices, their sizes, the dollar spread, and spread as a percentage of the bid.

### `get_order_imbalance(ticker)`
Compares current bid size vs ask size. A positive imbalance means more buyers than sellers at the quoted prices.

### `get_ohlc_momentum(ticker)`
Fetches minute-level bars and compares the last two closes to measure short-term momentum (up, down, or flat).

### `get_snapshot_mover_data(ticker)`
Returns a snapshot of the stock right now: last quote, last trade, and previous day's volume and price change.

### `get_corporate_actions(ticker)`
Lists recent dividend payments for a stock (amount and pay date).

---

## Notes

- All methods return `None` (or an empty DataFrame for `get_hourly_ohlcv`) if the API call fails, rather than raising an exception — errors are printed to the console.
- This folder only handles *fetching* data. All calculations and ML feature work happen in `services/`.
