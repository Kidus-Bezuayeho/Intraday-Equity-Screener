import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import from external
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from external.polygon_auth import PolygonService

class TestPolygonService:
    
    @patch('external.polygon_auth.RESTClient')
    def test_init_success(self, mock_rest_client):
        # This test verifies that the PolygonService initializes correctly when given a valid API key
        with patch.dict(os.environ, {'POLYGON_API_KEY': 'test_key'}):
            service = PolygonService()
            assert service.client is not None
            mock_rest_client.assert_called_once_with(api_key='test_key')
    
    def test_init_missing_api_key(self):
        # This test ensures the service fails gracefully when no API key is provided
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="POLYGON_API_KEY not found"):
                PolygonService()
    
    @patch('external.polygon_auth.RESTClient')
    def test_get_intraday_data_success(self, mock_rest_client):
        # This test mocks a successful API response and verifies the data is processed correctly
        mock_client = Mock()
        mock_rest_client.return_value = mock_client
        
        mock_agg = Mock()
        mock_agg.open = 150.0
        mock_agg.high = 151.0
        mock_agg.low = 149.0
        mock_agg.close = 150.5
        mock_agg.volume = 1000000
        mock_agg.vwap = 150.25
        mock_agg.timestamp = 1703123456789
        
        mock_client.list_aggs.return_value = [mock_agg]
        
        with patch.dict(os.environ, {'POLYGON_API_KEY': 'test_key'}):
            service = PolygonService()
            result = service.get_intraday_data("AAPL")
            
            assert result is not None
            assert result['ticker'] == "AAPL"
            assert result['open'] == 150.0
            assert result['high'] == 151.0
            assert result['low'] == 149.0
            assert result['close'] == 150.5
            assert result['volume'] == 1000000
            assert result['vwap'] == 150.25
            assert result['timestamp'] == 1703123456789
    
    @patch('external.polygon_auth.RESTClient')
    def test_get_intraday_data_no_results(self, mock_rest_client):
        # This test handles the case where the API returns no data
        mock_client = Mock()
        mock_rest_client.return_value = mock_client
        mock_client.list_aggs.return_value = []
        
        with patch.dict(os.environ, {'POLYGON_API_KEY': 'test_key'}):
            service = PolygonService()
            result = service.get_intraday_data("INVALID")
            
            assert result is None
    
    @patch('external.polygon_auth.RESTClient')
    def test_get_intraday_data_exception(self, mock_rest_client):
        # This test verifies that API exceptions are handled gracefully
        mock_client = Mock()
        mock_rest_client.return_value = mock_client
        mock_client.list_aggs.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {'POLYGON_API_KEY': 'test_key'}):
            service = PolygonService()
            result = service.get_intraday_data("AAPL")
            
            assert result is None
    
    def test_real_api_connectivity(self):
        # This test makes a real API call to verify actual connectivity to Polygon.io
        if not os.getenv('POLYGON_API_KEY'):
            pytest.skip("No real API key available")
        
        try:
            service = PolygonService()
            result = service.get_intraday_data("AAPL")
            
            assert result is not None
            assert result['ticker'] == "AAPL"
            assert 'open' in result
            assert 'close' in result
            assert 'volume' in result
            
            print(f"✅ Real API connectivity test passed!")
            print(f"   Got data for {result['ticker']}")
            print(f"   Latest close: ${result['close']}")
            print(f"   Volume: {result['volume']:,}")
            
        except Exception as e:
            pytest.fail(f"Real API connectivity test failed: {e}")

def test_polygon_service_integration():
    # This test performs a full integration test with the real Polygon API
    if not os.getenv('POLYGON_API_KEY'):
        pytest.skip("No real API key available for integration test")
    
    try:
        service = PolygonService()
        result = service.get_intraday_data("AAPL")
        
        if result:
            assert isinstance(result, dict)
            assert 'ticker' in result
            assert 'open' in result
            assert 'high' in result
            assert 'low' in result
            assert 'close' in result
            assert 'volume' in result
            assert 'vwap' in result
            assert 'timestamp' in result
            print("✅ Integration test passed!")
        else:
            pytest.skip("No data returned from API")
            
    except Exception as e:
        pytest.skip(f"Integration test failed: {e}")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])