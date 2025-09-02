from polygon import RESTClient
import os
from dotenv import load_dotenv

load_dotenv()

class PolygonService:
    """Polygon.io API service using official Python client"""
    
    def __init__(self):
        api_key = os.getenv('POLYGON_API_KEY')
        if not api_key:
            raise ValueError("POLYGON_API_KEY not found in .env file")
        
        self.client = RESTClient(api_key=api_key)
    
    def get_intraday_data(self, ticker="AAPL"):
        """Get intraday data for day trading"""
        try:
            # Get recent aggregates (last 7 days only)
            aggs = []
            for agg in self.client.list_aggs(ticker=ticker, multiplier=1, timespan="minute", from_="2024-12-20", to="2024-12-27"):
                aggs.append(agg)
            
            if aggs:
                latest = aggs[-1]
                return {
                    'ticker': ticker,
                    'open': latest.open,
                    'high': latest.high,
                    'low': latest.low,
                    'close': latest.close,
                    'volume': latest.volume,
                    'vwap': latest.vwap,
                    'timestamp': latest.timestamp
                }
            
            return None
        except Exception as e:
            print(f"Error getting intraday data: {e}")
            return None