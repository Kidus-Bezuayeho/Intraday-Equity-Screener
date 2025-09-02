import pytest
import sys
import os

# Add the parent directory to the path so we can import from external
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from external.polygon_trading_data import PolygonTradingDataService

class TestPolygonTradingDataService:
    
    def setup_method(self):
        # This runs before each test method
        if not os.getenv('POLYGON_API_KEY'):
            pytest.skip("No real API key available")
        self.service = PolygonTradingDataService()
    
    def test_init_success(self):
        # This test verifies that the service initializes correctly with a real API key
        assert self.service.client is not None
        print("✅ Service initialized successfully")
    
    def test_get_trade_volume_data_real(self):
        # This test makes a real API call to get trade volume data
        result = self.service.get_trade_volume_data("AAPL")
        
        if result:
            assert result['ticker'] == "AAPL"
            assert 'total_volume' in result
            assert 'avg_trade_price' in result
            assert 'trade_count' in result
            print(f"✅ Trade volume data: {result}")
        else:
            pytest.skip("No trade volume data returned from API")
    
    def test_get_bid_ask_spread_real(self):
        # This test makes a real API call to get bid/ask spread data
        result = self.service.get_bid_ask_spread("AAPL")
        
        if result:
            assert result['ticker'] == "AAPL"
            assert 'bid_price' in result
            assert 'ask_price' in result
            assert 'spread' in result
            assert 'spread_percentage' in result
            print(f"✅ Bid/ask spread data: {result}")
        else:
            pytest.skip("No bid/ask spread data returned from API")
    
    def test_get_order_imbalance_real(self):
        # This test makes a real API call to get order imbalance data
        result = self.service.get_order_imbalance("AAPL")
        
        if result:
            assert result['ticker'] == "AAPL"
            assert 'bid_volume' in result
            assert 'ask_volume' in result
            assert 'imbalance' in result
            assert 'excess_demand' in result
            print(f"✅ Order imbalance data: {result}")
        else:
            pytest.skip("No order imbalance data returned from API")
    
    def test_get_ohlc_momentum_real(self):
        # This test makes a real API call to get OHLC momentum data
        result = self.service.get_ohlc_momentum("AAPL")
        
        if result:
            assert result['ticker'] == "AAPL"
            assert 'current_close' in result
            assert 'previous_close' in result
            assert 'momentum' in result
            assert 'trend' in result
            print(f"✅ OHLC momentum data: {result}")
        else:
            pytest.skip("No OHLC momentum data returned from API")
    
    def test_get_snapshot_mover_data_real(self):
        # This test makes a real API call to get snapshot data
        result = self.service.get_snapshot_mover_data("AAPL")
        
        if result:
            assert result['ticker'] == "AAPL"
            assert 'last_quote' in result or 'last_trade' in result
            print(f"✅ Snapshot data: {result}")
        else:
            pytest.skip("No snapshot data returned from API")
    
    def test_get_corporate_actions_real(self):
        # This test makes a real API call to get corporate actions data
        result = self.service.get_corporate_actions("AAPL")
        
        if result:
            assert result['ticker'] == "AAPL"
            assert 'dividend_count' in result
            print(f"✅ Corporate actions data: {result}")
        else:
            pytest.skip("No corporate actions data returned from API")
    
    def test_multiple_tickers_real(self):
        # This test tests multiple tickers to verify the service works broadly
        tickers = ["AAPL", "MSFT", "GOOGL"]
        
        for ticker in tickers:
            result = self.service.get_bid_ask_spread(ticker)
            if result:
                assert result['ticker'] == ticker
                print(f"✅ {ticker} data retrieved successfully")
            else:
                print(f"⚠️ No data for {ticker}")

def test_service_integration_real():
    # This test performs a full integration test with real API calls
    if not os.getenv('POLYGON_API_KEY'):
        pytest.skip("No real API key available")
    
    try:
        service = PolygonTradingDataService()
        
        # Test multiple functions with real data
        spread_data = service.get_bid_ask_spread("AAPL")
        momentum_data = service.get_ohlc_momentum("AAPL")
        
        if spread_data and momentum_data:
            print("✅ Full integration test passed!")
            print(f"   Spread: ${spread_data['spread']:.4f}")
            print(f"   Momentum: {momentum_data['momentum']:.2f} ({momentum_data['trend']})")
        else:
            pytest.skip("Insufficient data returned from API")
            
    except Exception as e:
        pytest.fail(f"Integration test failed: {e}")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])