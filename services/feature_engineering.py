import pandas as pd
import numpy as np


def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.ewm(com=period - 1, min_periods=period, adjust=False).mean()
    avg_loss = losses.ewm(com=period - 1, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).rename("rsi")


def compute_macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    fast_ema = close.ewm(span=fast, adjust=False).mean()
    slow_ema = close.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({
        "macd_line": macd_line,
        "signal_line": signal_line,
        "histogram": histogram,
    })


def compute_vwap(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
    volume: pd.Series,
    timestamp: pd.Series,
) -> pd.Series:
    typical_price = (high + low + close) / 3
    tp_vol = typical_price * volume

    dates = timestamp.dt.date if hasattr(timestamp.dt, "date") else pd.Series(
        [t.date() for t in timestamp], index=timestamp.index
    )

    cumvol = volume.groupby(dates).cumsum()
    cumtpvol = tp_vol.groupby(dates).cumsum()

    vwap = cumtpvol / cumvol.replace(0, np.nan)
    return vwap.rename("vwap")


def compute_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(com=period - 1, min_periods=period, adjust=False).mean().rename("atr")


def compute_bollinger_bands(
    close: pd.Series,
    period: int = 20,
    num_std: float = 2.0,
) -> pd.DataFrame:
    middle = close.rolling(period).mean()
    std = close.rolling(period).std(ddof=0)
    return pd.DataFrame({
        "bb_upper": middle + num_std * std,
        "bb_middle": middle,
        "bb_lower": middle - num_std * std,
    })


def compute_lagged_returns(
    close: pd.Series,
    lags: list = None,
) -> pd.DataFrame:
    if lags is None:
        lags = [1, 2, 3, 4, 5]
    return pd.DataFrame({f"return_lag_{lag}": close.pct_change(lag) for lag in lags})


def compute_direction_label(close: pd.Series) -> pd.Series:
    shifted = close.shift(-1)
    label = (shifted > close).astype(float)
    label[shifted.isna()] = np.nan
    return label.rename("direction")


def build_feature_matrix(
    ohlcv: pd.DataFrame,
    rsi_period: int = 14,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    atr_period: int = 14,
    bb_period: int = 20,
    bb_std: float = 2.0,
    lag_periods: list = None,
) -> pd.DataFrame:
    """Transform a raw OHLCV DataFrame into an ML-ready feature matrix.

    Args:
        ohlcv: DataFrame with columns [timestamp, open, high, low, close, volume].
               Must have at least enough rows for indicator warm-up.
        rsi_period: RSI lookback period.
        macd_fast: MACD fast EMA span.
        macd_slow: MACD slow EMA span.
        macd_signal: MACD signal EMA span.
        atr_period: ATR lookback period.
        bb_period: Bollinger Bands rolling window.
        bb_std: Bollinger Bands standard deviation multiplier.
        lag_periods: List of lag periods for lagged returns. Defaults to [1,2,3,4,5].

    Returns:
        DataFrame with all feature columns and a binary 'direction' label (1=up, 0=down).
        Warm-up NaN rows and the final look-ahead row are dropped.

    Raises:
        ValueError: If ohlcv is empty or has insufficient rows for warm-up.
    """
    if lag_periods is None:
        lag_periods = [1, 2, 3, 4, 5]

    if ohlcv is None or len(ohlcv) == 0:
        raise ValueError("ohlcv DataFrame is empty.")

    min_rows = macd_slow + macd_signal + max(lag_periods)
    if len(ohlcv) < min_rows:
        raise ValueError(
            f"Insufficient data: {len(ohlcv)} rows provided, "
            f"need at least {min_rows} for indicator warm-up."
        )

    close = ohlcv["close"]
    high = ohlcv["high"]
    low = ohlcv["low"]
    volume = ohlcv["volume"]
    timestamp = ohlcv["timestamp"]

    parts = [
        ohlcv[["open", "high", "low", "close", "volume"]].copy(),
        compute_rsi(close, rsi_period),
        compute_macd(close, macd_fast, macd_slow, macd_signal),
        compute_vwap(close, high, low, volume, timestamp),
        compute_atr(high, low, close, atr_period),
        compute_bollinger_bands(close, bb_period, bb_std),
        compute_lagged_returns(close, lag_periods),
        compute_direction_label(close),
    ]

    df = pd.concat(parts, axis=1)
    df = df.dropna()
    df["direction"] = df["direction"].astype(int)
    return df.reset_index(drop=True)
