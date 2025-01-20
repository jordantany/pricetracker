import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import TrackerConfig

class PriceData:
    def __init__(self, timestamp: str, price: float, **kwargs):
        self.timestamp = timestamp
        self.price = price
        self.extra_data = kwargs

class BaseTracker(ABC):
    def __init__(self, config: TrackerConfig):
        self.config = config
        self.last_prices: Dict[str, Optional[float]] = {}
        self.price_history: Dict[str, List[PriceData]] = {}
        self.is_running = False
    
    def check_price_alert(self, identifier: str, current_price: float) -> bool:
        if identifier not in self.last_prices or self.last_prices[identifier] is None:
            return False
        
        last_price = self.last_prices[identifier]
        price_change_percent = abs((current_price - last_price) / last_price * 100)
        return price_change_percent >= self.config.alert_threshold_percent
    
    def format_price_change(self, identifier: str, current_price: float, 
                          up_emoji: str = "📈", down_emoji: str = "📉", 
                          neutral_emoji: str = "➡️") -> str:
        if identifier not in self.last_prices or self.last_prices[identifier] is None:
            return ""
        
        last_price = self.last_prices[identifier]
        change = current_price - last_price
        change_percent = (change / last_price) * 100
        direction = up_emoji if change > 0 else down_emoji if change < 0 else neutral_emoji
        
        return f"{direction} ${change:+.8f} ({change_percent:+.2f}%)"
    
    def update_price_history(self, identifier: str, price_data: PriceData):
        if identifier not in self.price_history:
            self.price_history[identifier] = []
        
        self.price_history[identifier].append(price_data)
        
        if len(self.price_history[identifier]) > self.config.max_price_history:
            self.price_history[identifier] = self.price_history[identifier][-self.config.keep_history_count:]
    
    def update_last_price(self, identifier: str, price: float):
        self.last_prices[identifier] = price
    
    @abstractmethod
    def fetch_prices(self) -> Dict[str, Optional[float]]:
        pass
    
    @abstractmethod
    def display_price_info(self, identifier: str, price: float, timestamp: str, **kwargs):
        pass
    
    @abstractmethod
    def get_display_name(self, identifier: str) -> str:
        pass
    
    def start_monitoring(self):
        self.print_startup_info()
        self.is_running = True
        
        while self.is_running:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                prices = self.fetch_prices()
                
                if all(price is None for price in prices.values()):
                    print(f"❌ Failed to fetch prices at {datetime.now().strftime('%H:%M:%S')}")
                    time.sleep(self.config.monitoring_interval_seconds)
                    continue
                
                for identifier, price in prices.items():
                    if price is None:
                        continue
                    
                    price_data = PriceData(timestamp, price)
                    self.update_price_history(identifier, price_data)
                    
                    alert_triggered = self.check_price_alert(identifier, price)
                    
                    self.display_price_info(
                        identifier=identifier,
                        price=price,
                        timestamp=timestamp,
                        alert_triggered=alert_triggered
                    )
                    
                    if alert_triggered:
                        self.handle_alert(identifier, price)
                    
                    self.update_last_price(identifier, price)
                
                print()
                time.sleep(self.config.monitoring_interval_seconds)
                
            except KeyboardInterrupt:
                print("\n👋 Price monitoring stopped by user")
                self.is_running = False
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                time.sleep(self.config.monitoring_interval_seconds)
    
    def stop_monitoring(self):
        self.is_running = False
    
    def handle_alert(self, identifier: str, price: float):
        display_name = self.get_display_name(identifier)
        print(f"🔔 Significant price movement detected for {display_name}!")
    
    @abstractmethod
    def print_startup_info(self):
        pass