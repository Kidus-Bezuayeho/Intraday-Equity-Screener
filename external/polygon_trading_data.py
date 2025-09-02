from polygon import RESTClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PolygonTradingDataService:
    """Polygon.io service for comprehensive trading data and market analysis"""
    
    def __init__(self):
        api_key = os.getenv('POLYGON_API_KEY')
        if not api_key:
            raise ValueError("POLYGON_API_KEY not found in .env file")
        
        self.client = RESTClient(api_key=api_key)
    
    def get_trade_volume_data(self, ticker="AAPL"):
        # Get trade volume data from Trades API (tick-level)
        try:
            trades = []
            for trade in self.client.list_trades(ticker=ticker, timestamp="2024-12-27"):
                trades.append(trade)
            
            if trades:
                total_volume = sum(trade.size for trade in trades)
                avg_trade_price = sum(trade.price * trade.size for trade in trades) / total_volume
                
                return {
                    'ticker': ticker,
                    'total_volume': total_volume,
                    'avg_trade_price': avg_trade_price,
                    'trade_count': len(trades),
                    'latest_trade': trades[-1].price if trades else None
                }
            return None
        except Exception as e:
            print(f"Error getting trade volume data: {e}")
            return None
    
    def get_bid_ask_spread(self, ticker="AAPL"):
        # Get bid/ask spread from Quotes API (NBBO)
        try:
            quote = self.client.get_last_quote(ticker=ticker)
            
            spread = quote.ask_price - quote.bid_price
            spread_percentage = (spread / quote.bid_price) * 100
            
            return {
                'ticker': ticker,
                'bid_price': quote.bid_price,
                'ask_price': quote.ask_price,
                'bid_size': quote.bid_size,
                'ask_size': quote.ask_size,
                'spread': spread,
                'spread_percentage': spread_percentage
            }
        except Exception as e:
            print(f"Error getting bid/ask spread: {e}")
            return None
    
    def get_order_imbalance(self, ticker="AAPL"):
        # Get order imbalance from Quotes API (size of bid vs ask)
        try:
            quote = self.client.get_last_quote(ticker=ticker)
            
            bid_volume = quote.bid_size
            ask_volume = quote.ask_size
            imbalance = bid_volume - ask_volume
            imbalance_ratio = bid_volume / ask_volume if ask_volume > 0 else float('inf')
            
            return {
                'ticker': ticker,
                'bid_volume': bid_volume,
                'ask_volume': ask_volume,
                'imbalance': imbalance,
                'imbalance_ratio': imbalance_ratio,
                'excess_demand': imbalance > 0
            }
        except Exception as e:
            print(f"Error getting order imbalance: {e}")
            return None
    
    def get_ohlc_momentum(self, ticker="AAPL"):
        # Get OHLC momentum from Aggregates API
        try:
            aggs = []
            for agg in self.client.list_aggs(ticker=ticker, multiplier=1, timespan="minute", from_="2024-12-20", to="2024-12-27"):
                aggs.append(agg)
            
            if len(aggs) >= 2:
                current = aggs[-1]
                previous = aggs[-2]
                
                momentum = current.close - previous.close
                momentum_percentage = (momentum / previous.close) * 100
                
                return {
                    'ticker': ticker,
                    'current_close': current.close,
                    'previous_close': previous.close,
                    'momentum': momentum,
                    'momentum_percentage': momentum_percentage,
                    'trend': 'up' if momentum > 0 else 'down' if momentum < 0 else 'flat'
                }
            return None
        except Exception as e:
            print(f"Error getting OHLC momentum: {e}")
            return None
    
    def get_snapshot_mover_data(self, ticker="AAPL"):
        # Get snapshot data to identify market movers
        try:
            snapshot = self.client.get_snapshot(ticker=ticker)
            
            return {
                'ticker': ticker,
                'last_quote': snapshot.last_quote.ask_price if snapshot.last_quote else None,
                'last_trade': snapshot.last_trade.price if snapshot.last_trade else None,
                'min_av': snapshot.min.av if snapshot.min else None,
                'prev_day_volume': snapshot.prev_day.volume if snapshot.prev_day else None,
                'prev_day_change': snapshot.prev_day.change if snapshot.prev_day else None
            }
        except Exception as e:
            print(f"Error getting snapshot data: {e}")
            return None
    
    def get_corporate_actions(self, ticker="AAPL"):
        # Get corporate actions like dividends and splits
        try:
            dividends = []
            for div in self.client.list_dividends(ticker=ticker):
                dividends.append(div)
            
            return {
                'ticker': ticker,
                'dividend_count': len(dividends),
                'recent_dividends': [{'amount': d.cash_amount, 'date': d.pay_date} for d in dividends[:5]]
            }
        except Exception as e:
            print(f"Error getting corporate actions: {e}")
            return None

def main():
    # Test the comprehensive trading data service
    try:
        service = PolygonTradingDataService()
        
        print("📊 Testing Comprehensive Trading Data Service...")
        print("=" * 60)
        
        ticker = "AAPL"
        
        # Test all data functions
        trade_data = service.get_trade_volume_data(ticker)
        spread_data = service.get_bid_ask_spread(ticker)
        imbalance_data = service.get_order_imbalance(ticker)
        momentum_data = service.get_ohlc_momentum(ticker)
        snapshot_data = service.get_snapshot_mover_data(ticker)
        corporate_data = service.get_corporate_actions(ticker)
        
        # Display results
        if trade_data:
            print(f"📈 Trade Volume Data: {trade_data}")
        if spread_data:
            print(f"💹 Bid/Ask Spread: {spread_data}")
        if imbalance_data:
            print(f"⚖️ Order Imbalance: {imbalance_data}")
        if momentum_data:
            print(f"🚀 OHLC Momentum: {momentum_data}")
        if snapshot_data:
            print(f"📸 Snapshot Data: {snapshot_data}")
        if corporate_data:
            print(f"📄 Corporate Actions: {corporate_data}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 