from datetime import datetime
from typing import Dict, Optional
from base_tracker import BaseTracker
from api_clients import CoinGeckoClient
from database import PriceDatabase
from config import TrackerConfig

class BTCDatabaseConfig(TrackerConfig):
    def __init__(self, db_path: str = "btc_prices.db"):
        super().__init__()
        self.monitoring_interval_seconds = 60  # Every minute
        self.alert_threshold_percent = 5.0
        self.db_path = db_path
        self.coin_id = "bitcoin"
        self.symbol = "BTC"

class BTCDatabaseTracker(BaseTracker):
    def __init__(self, config: BTCDatabaseConfig):
        super().__init__(config)
        self.config = config
        self.coingecko_client = CoinGeckoClient()
        self.database = PriceDatabase(config.db_path)
        self.coin_id = config.coin_id
        self.symbol = config.symbol
        
        # Initialize price history from database
        self.load_recent_price_from_db()
    
    def load_recent_price_from_db(self):
        latest_record = self.database.get_latest_price(self.coin_id)
        if latest_record:
            self.last_prices[self.coin_id] = latest_record['price_usd']
            print(f"📋 Loaded last known price from database: ${latest_record['price_usd']:,.2f}")
    
    def fetch_prices(self) -> Dict[str, Optional[float]]:
        prices = self.coingecko_client.get_prices([self.coin_id])
        return prices
    
    def get_display_name(self, identifier: str) -> str:
        return self.symbol
    
    def display_price_info(self, identifier: str, price: float, timestamp: str, **kwargs):
        alert_triggered = kwargs.get('alert_triggered', False)
        db_saved = kwargs.get('db_saved', False)
        
        price_change_info = self.format_price_change(identifier, price)
        alert_indicator = "🚨 ALERT! " if alert_triggered else ""
        db_indicator = "💾" if db_saved else "❌"
        
        print(f"{alert_indicator}[{timestamp}] {self.symbol}: ${price:,.2f} {price_change_info} {db_indicator}")
    
    def start_monitoring(self):
        self.print_startup_info()
        self.is_running = True
        
        # Show database info
        db_info = self.database.get_database_info()
        print(f"📊 Database: {db_info.get('total_records', 0)} total records")
        if 'symbol_counts' in db_info and self.symbol in db_info['symbol_counts']:
            print(f"📊 {self.symbol} records: {db_info['symbol_counts'][self.symbol]}")
        print("-" * 70)
        
        while self.is_running:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                prices = self.fetch_prices()
                
                current_price = prices.get(self.coin_id)
                if current_price is None:
                    print(f"❌ Failed to fetch BTC price at {datetime.now().strftime('%H:%M:%S')}")
                    self._sleep()
                    continue
                
                # Save to database
                db_saved = self.database.insert_price_record(
                    symbol=self.symbol,
                    coin_id=self.coin_id,
                    price_usd=current_price,
                    timestamp=timestamp
                )
                
                # Check for alerts
                alert_triggered = self.check_price_alert(self.coin_id, current_price)
                
                # Display price info
                self.display_price_info(
                    identifier=self.coin_id,
                    price=current_price,
                    timestamp=timestamp,
                    alert_triggered=alert_triggered,
                    db_saved=db_saved
                )
                
                # Handle alerts
                if alert_triggered:
                    self.handle_alert(self.coin_id, current_price)
                
                # Update last price
                self.update_last_price(self.coin_id, current_price)
                
                self._sleep()
                
            except KeyboardInterrupt:
                print("\n👋 BTC price monitoring stopped by user")
                self.show_session_summary()
                self.is_running = False
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                self._sleep()
    
    def _sleep(self):
        import time
        time.sleep(self.config.monitoring_interval_seconds)
    
    def print_startup_info(self):
        print(f"₿ Bitcoin Price Database Tracker Started")
        print(f"📊 Monitoring interval: {self.config.monitoring_interval_seconds} seconds (every minute)")
        print(f"⚠️  Alert threshold: {self.config.alert_threshold_percent}%")
        print(f"💾 Database: {self.config.db_path}")
    
    def handle_alert(self, identifier: str, price: float):
        print(f"🔔 Significant BTC price movement detected! Current: ${price:,.2f}")
        
        # Log alert to database with special flag
        self.database.insert_price_record(
            symbol=f"{self.symbol}_ALERT",
            coin_id=self.coin_id,
            price_usd=price,
            alert_triggered=True,
            alert_threshold=self.config.alert_threshold_percent
        )
    
    def show_session_summary(self):
        print("\n📊 Session Summary:")
        
        # Get recent stats
        stats = self.database.get_price_stats(self.coin_id, hours=1)
        if stats and stats['record_count'] > 0:
            print(f"Records this hour: {stats['record_count']}")
            print(f"Price range: ${stats['min_price']:,.2f} - ${stats['max_price']:,.2f}")
            print(f"Average price: ${stats['avg_price']:,.2f}")
        
        # Get database info
        db_info = self.database.get_database_info()
        print(f"Total records in database: {db_info.get('total_records', 0)}")
    
    def get_price_history_from_db(self, limit: int = 100):
        return self.database.get_price_history(self.coin_id, limit)
    
    def cleanup_old_data(self, days: int = 30):
        self.database.cleanup_old_records(days)