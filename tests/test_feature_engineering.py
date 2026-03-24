import sys
import os
import pytest
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.feature_engineering import (
    build_feature_matrix,
    compute_rsi,
    compute_macd,
    compute_vwap,
    compute_atr,
    compute_bollinger_bands,
    compute_lagged_returns,
    compute_direction_label,
)


@pytest.fixture
def synthetic_ohlcv():
    """100 hourly bars of synthetic OHLCV data spanning 5 calendar days."""
    np.random.seed(42)
    n = 100
    # Build timestamps: 20 bars per day across 5 days
    timestamps = pd.date_range("2024-01-02 09:00", periods=n, freq="h", tz="UTC")
    close = 150.0 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.abs(np.random.randn(n) * 0.3)
    low = close - np.abs(np.random.randn(n) * 0.3)
    open_ = close + np.random.randn(n) * 0.2
    volume = np.random.randint(1_000, 100_000, size=n).astype(float)
    return pd.DataFrame({
        "timestamp": timestamps,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


# ── RSI ────────────────────────────────────────────────────────────────────────

def test_rsi_range(synthetic_ohlcv):
    rsi = compute_rsi(synthetic_ohlcv["close"])
    valid = rsi.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()


def test_rsi_warm_up_nans(synthetic_ohlcv):
    period = 14
    rsi = compute_rsi(synthetic_ohlcv["close"], period=period)
    assert rsi.iloc[:period - 1].isna().all()


# ── MACD ───────────────────────────────────────────────────────────────────────

def test_macd_columns_present(synthetic_ohlcv):
    macd = compute_macd(synthetic_ohlcv["close"])
    assert set(macd.columns) == {"macd_line", "signal_line", "histogram"}


def test_macd_histogram_math(synthetic_ohlcv):
    macd = compute_macd(synthetic_ohlcv["close"])
    diff = (macd["histogram"] - (macd["macd_line"] - macd["signal_line"])).abs()
    assert (diff < 1e-10).all()


# ── VWAP ───────────────────────────────────────────────────────────────────────

def test_vwap_resets_daily(synthetic_ohlcv):
    df = synthetic_ohlcv
    vwap = compute_vwap(df["close"], df["high"], df["low"], df["volume"], df["timestamp"])
    # First bar of day 2 should not equal the last bar of day 1
    day_starts = df[df["timestamp"].dt.hour == df["timestamp"].iloc[0].hour].index
    if len(day_starts) >= 2:
        d1_end = day_starts[1] - 1
        d2_start = day_starts[1]
        assert vwap.iloc[d2_start] != vwap.iloc[d1_end]


def test_vwap_no_nans_normal_data(synthetic_ohlcv):
    df = synthetic_ohlcv
    vwap = compute_vwap(df["close"], df["high"], df["low"], df["volume"], df["timestamp"])
    assert vwap.notna().all()


# ── ATR ────────────────────────────────────────────────────────────────────────

def test_atr_nonnegative(synthetic_ohlcv):
    df = synthetic_ohlcv
    atr = compute_atr(df["high"], df["low"], df["close"])
    assert (atr.dropna() >= 0).all()


# ── Bollinger Bands ────────────────────────────────────────────────────────────

def test_bollinger_middle_is_sma(synthetic_ohlcv):
    close = synthetic_ohlcv["close"]
    period = 20
    bb = compute_bollinger_bands(close, period=period)
    expected_middle = close.rolling(period).mean()
    pd.testing.assert_series_equal(bb["bb_middle"], expected_middle, check_names=False)


def test_bollinger_band_ordering(synthetic_ohlcv):
    bb = compute_bollinger_bands(synthetic_ohlcv["close"]).dropna()
    assert (bb["bb_upper"] >= bb["bb_middle"]).all()
    assert (bb["bb_middle"] >= bb["bb_lower"]).all()


def test_bollinger_columns_present(synthetic_ohlcv):
    bb = compute_bollinger_bands(synthetic_ohlcv["close"])
    assert set(bb.columns) == {"bb_upper", "bb_middle", "bb_lower"}


# ── Lagged Returns ─────────────────────────────────────────────────────────────

def test_lagged_returns_column_count(synthetic_ohlcv):
    lr = compute_lagged_returns(synthetic_ohlcv["close"])
    assert len(lr.columns) == 5


def test_lagged_returns_column_names(synthetic_ohlcv):
    lr = compute_lagged_returns(synthetic_ohlcv["close"], lags=[1, 2, 3, 4, 5])
    assert set(lr.columns) == {f"return_lag_{i}" for i in range(1, 6)}


def test_lagged_returns_math(synthetic_ohlcv):
    close = synthetic_ohlcv["close"]
    lr = compute_lagged_returns(close, lags=[1])
    expected = close.pct_change(1)
    pd.testing.assert_series_equal(lr["return_lag_1"], expected, check_names=False)


# ── Direction Label ────────────────────────────────────────────────────────────

def test_direction_label_binary(synthetic_ohlcv):
    label = compute_direction_label(synthetic_ohlcv["close"]).dropna()
    assert set(label.unique()).issubset({0.0, 1.0})


def test_direction_label_last_row_is_nan(synthetic_ohlcv):
    label = compute_direction_label(synthetic_ohlcv["close"])
    assert pd.isna(label.iloc[-1])


# ── build_feature_matrix ───────────────────────────────────────────────────────

def test_build_feature_matrix_no_nans(synthetic_ohlcv):
    result = build_feature_matrix(synthetic_ohlcv)
    assert result.isnull().sum().sum() == 0


def test_build_feature_matrix_expected_columns(synthetic_ohlcv):
    result = build_feature_matrix(synthetic_ohlcv)
    expected = {
        "open", "high", "low", "close", "volume",
        "rsi", "macd_line", "signal_line", "histogram",
        "vwap", "atr",
        "bb_upper", "bb_middle", "bb_lower",
        "return_lag_1", "return_lag_2", "return_lag_3", "return_lag_4", "return_lag_5",
        "direction",
    }
    assert expected.issubset(set(result.columns))


def test_build_feature_matrix_direction_is_int(synthetic_ohlcv):
    result = build_feature_matrix(synthetic_ohlcv)
    assert result["direction"].dtype in (int, np.int64, np.int32)
    assert set(result["direction"].unique()).issubset({0, 1})


def test_build_feature_matrix_row_count(synthetic_ohlcv):
    result = build_feature_matrix(synthetic_ohlcv)
    # Must have dropped at least 1 row (the final label look-ahead)
    assert len(result) < len(synthetic_ohlcv)
    assert len(result) > 0


def test_build_feature_matrix_raises_on_empty():
    empty = pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])
    with pytest.raises(ValueError, match="empty"):
        build_feature_matrix(empty)


def test_build_feature_matrix_raises_on_insufficient_data():
    # 10 rows is well below the warm-up minimum (26 + 9 + 5 = 40)
    np.random.seed(0)
    n = 10
    timestamps = pd.date_range("2024-01-02", periods=n, freq="h", tz="UTC")
    close = 150.0 + np.cumsum(np.random.randn(n))
    df = pd.DataFrame({
        "timestamp": timestamps,
        "open": close,
        "high": close + 0.1,
        "low": close - 0.1,
        "close": close,
        "volume": np.ones(n) * 1000,
    })
    with pytest.raises(ValueError, match="Insufficient"):
        build_feature_matrix(df)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
