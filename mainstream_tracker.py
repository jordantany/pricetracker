from typing import Dict, Optional, List
from base_tracker import BaseTracker
from api_clients import CoinGeckoClient
from config import MainstreamCryptoConfig, CoinSymbols

class MainstreamCryptoTracker(BaseTracker):
    def __init__(self, config: MainstreamCryptoConfig):
        super().__init__(config)
        self.config = config
        self.coin_symbols = CoinSymbols.MAINSTREAM_COINS
        self.coingecko_client = CoinGeckoClient()
        
        for coin in self.config.coins:
            self.price_history[coin] = []
    
    def fetch_prices(self) -> Dict[str, Optional[float]]:
        return self.coingecko_client.get_prices(self.config.coins)
    
    def get_display_name(self, identifier: str) -> str:
        return self.coin_symbols.get(identifier, identifier.upper())
    
    def display_price_info(self, identifier: str, price: float, timestamp: str, **kwargs):
        alert_triggered = kwargs.get('alert_triggered', False)
        symbol = self.get_display_name(identifier)
        price_change_info = self.format_price_change(identifier, price)
        alert_indicator = "🚨 ALERT! " if alert_triggered else ""
        
        print(f"{alert_indicator}[{timestamp}] {symbol}: ${price:,.2f} {price_change_info}")
    
    def print_startup_info(self):
        coin_names = [self.get_display_name(coin) for coin in self.config.coins]
        print(f"🚀 Crypto Price Tracker Started - Monitoring: {', '.join(coin_names)}")
        print(f"📊 Monitoring interval: {self.config.monitoring_interval_seconds} seconds")
        print(f"⚠️  Alert threshold: {self.config.alert_threshold_percent}%")
        print("-" * 70)
    
    def get_price_summary(self) -> Dict:
        summary = {}
        for coin in self.config.coins:
            if not self.price_history[coin]:
                summary[coin] = {}
                continue
            
            prices = [item.price for item in self.price_history[coin]]
            summary[coin] = {
                'symbol': self.get_display_name(coin),
                'current_price': prices[-1] if prices else None,
                'highest_price': max(prices),
                'lowest_price': min(prices),
                'average_price': sum(prices) / len(prices),
                'total_records': len(prices)
            }
        return summary