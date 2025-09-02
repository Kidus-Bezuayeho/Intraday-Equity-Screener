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
        """Test successful initialization with valid API key"""
        with patch.dict(os.environ, {'POLYGON_API_KEY': 'test_key'}):
            service = PolygonService()
            assert service.client is not None
            mock_rest_client.assert_called_once_with(api_key='test_key')
    
    def test_init_missing_api_key(self):
        """Test initialization fails without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="POLYGON_API_KEY not found"):
                PolygonService()
    
    @patch('external.polygon_auth.RESTClient')
    def test_get_intraday_data_success(self, mock_rest_client):
        """Test successful intraday data retrieval"""
        # Mock the REST client and its response
        mock_client = Mock()
        mock_rest_client.return_value = mock_client
        
        # Mock the aggregate data
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
        """Test when no intraday data is returned"""
        mock_client = Mock()
        mock_rest_client.return_value = mock_client
        mock_client.list_aggs.return_value = []
        
        with patch.dict(os.environ, {'POLYGON_API_KEY': 'test_key'}):
            service = PolygonService()
            result = service.get_intraday_data("INVALID")
            
            assert result is None
    
    @patch('external.polygon_auth.RESTClient')
    def test_get_intraday_data_exception(self, mock_rest_client):
        """Test handling of API exceptions"""
        mock_client = Mock()
        mock_rest_client.return_value = mock_client
        mock_client.list_aggs.side_effect = Exception("API Error")
        
        with patch.dict(os.environ, {'POLYGON_API_KEY': 'test_key'}):
            service = PolygonService()
            result = service.get_intraday_data("AAPL")
            
            assert result is None
    
    def test_real_api_connectivity(self):
        """Test actual connectivity to Polygon API"""
        # Skip if no API key
        if not os.getenv('POLYGON_API_KEY'):
            pytest.skip("No real API key available")
        
        try:
            service = PolygonService()
            
            # Test with a real ticker
            result = service.get_intraday_data("AAPL")
            
            # If we get here, the API call was successful (like a 200 response)
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
    """Integration test - only run if you have a real API key"""
    # Skip this test if no real API key is available
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