# Intraday Equity Screener

An AI-driven backend for predicting intraday stock price movements on an hourly basis. Given OHLCV time-series data and a set of technical indicators, the system predicts both **direction** (up or down) and **magnitude** (expected % return) for the next hour.

---

## What it does

- Fetches hourly OHLCV data from [Polygon.io](https://polygon.io)
- Computes technical indicators: RSI, MACD, VWAP, ATR, Bollinger Bands, and lagged returns
- Builds a model-ready feature matrix with a labelled `direction` column
- Exposes predictions, backtesting results, and analytics via a FastAPI REST API _(in progress)_

---

## Project structure

```
Intraday-Equity-Screener/
├── external/           # Data ingestion — Polygon.io API client
├── services/           # Business logic — feature engineering, indicators
├── controllers/        # Request handlers (planned)
├── routes/             # FastAPI route definitions (planned)
├── tests/              # Automated tests
└── requirements.txt
```

- **`external/`** — wraps Polygon.io REST API. Handles all network calls; returns plain DataFrames.
- **`services/`** — pure computation. Takes DataFrames in, returns DataFrames out. No API calls here.
- **`controllers/`** and **`routes/`** — FastAPI layer (not yet implemented).

---

## Setup

**Requirements:** Python 3.11+

```bash
# 1. Clone the repo and create a virtual environment
python3.11 -m venv equity_screener_env
source equity_screener_env/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Polygon.io API key
echo "POLYGON_API_KEY=your_key_here" > .env
```

---

## Running the tests

```bash
source equity_screener_env/bin/activate

# All tests
pytest tests/ -v

# Feature engineering only (no API key needed)
pytest tests/test_feature_engineering.py -v

# Polygon API tests (requires POLYGON_API_KEY in .env)
pytest tests/test_polygon_service.py -v -s
pytest tests/test_polygon_ohlcv.py -v -s
```

Tests that call the Polygon API skip gracefully if no key is set — you'll see `SKIPPED` rather than a failure.

---

## Quick start

```python
from external.polygon_trading_data import PolygonTradingDataService
from services.feature_engineering import build_feature_matrix

# Fetch hourly OHLCV data
service = PolygonTradingDataService()
ohlcv = service.get_hourly_ohlcv("AAPL", "2024-12-01", "2024-12-31")

# Build a model-ready feature matrix
features = build_feature_matrix(ohlcv)
# features has RSI, MACD, VWAP, ATR, Bollinger Bands, lagged returns, and a 'direction' label
```

---

## Model roadmap

The system is designed to support a progression of models, from interpretable baselines to advanced sequential architectures:

| Stage | Model | Status |
|---|---|---|
| 1 | Multiple Linear Regression | Planned |
| 2 | XGBoost | Planned |
| 3 | LSTM | Planned |
| 4 | GRU | Planned |
| 5 | Transformer | Planned |

---

## Key dependencies

| Package | Purpose |
|---|---|
| `polygon-api-client` | Market data from Polygon.io |
| `pandas` / `numpy` | Data manipulation |
| `scikit-learn` | Baseline ML models |
| `fastapi` / `uvicorn` | REST API server |
| `python-dotenv` | API key management |
| `pytest` | Testing |
