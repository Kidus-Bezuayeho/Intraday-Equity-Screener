import sys
import os
import pytest
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from external.polygon_trading_data import PolygonTradingDataService

_EXPECTED_COLUMNS = {"timestamp", "open", "high", "low", "close", "volume"}


class TestPolygonHourlyOHLCV:

    def setup_method(self):
        if not os.getenv("POLYGON_API_KEY"):
            pytest.skip("No real API key available")
        self.service = PolygonTradingDataService()

    def test_returns_dataframe(self):
        result = self.service.get_hourly_ohlcv("AAPL", "2024-12-16", "2024-12-20")
        assert isinstance(result, pd.DataFrame)

    def test_has_correct_columns(self):
        result = self.service.get_hourly_ohlcv("AAPL", "2024-12-16", "2024-12-20")
        assert _EXPECTED_COLUMNS.issubset(set(result.columns))

    def test_sorted_ascending(self):
        result = self.service.get_hourly_ohlcv("AAPL", "2024-12-16", "2024-12-20")
        if len(result) > 1:
            assert result["timestamp"].is_monotonic_increasing

    def test_timestamps_are_utc(self):
        result = self.service.get_hourly_ohlcv("AAPL", "2024-12-16", "2024-12-20")
        if len(result) > 0:
            assert result["timestamp"].dt.tz is not None

    def test_empty_range_returns_empty_dataframe(self):
        # A weekend range with no trading activity
        result = self.service.get_hourly_ohlcv("AAPL", "2024-12-21", "2024-12-22")
        assert isinstance(result, pd.DataFrame)
        assert _EXPECTED_COLUMNS.issubset(set(result.columns))

    def test_multiple_tickers(self):
        for ticker in ["AAPL", "MSFT", "GOOGL"]:
            result = self.service.get_hourly_ohlcv(ticker, "2024-12-16", "2024-12-20")
            assert isinstance(result, pd.DataFrame), f"Expected DataFrame for {ticker}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
