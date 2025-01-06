#!/usr/bin/env python3

import requests
import time
from datetime import datetime
from typing import Dict, Optional

class BTCPriceTracker:
    def __init__(self, alert_threshold_percent: float = 5.0):
        self.api_url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
        self.backup_api_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        self.alert_threshold = alert_threshold_percent
        self.last_price = None
        self.price_history = []
    
    def fetch_price_coindesk(self) -> Optional[float]:
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            price_str = data['bpi']['USD']['rate'].replace(',', '').replace('$', '')
            return float(price_str)
        except Exception as e:
            print(f"CoinDesk API error: {e}")
            return None
    
    def fetch_price_coingecko(self) -> Optional[float]:
        try:
            response = requests.get(self.backup_api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return float(data['bitcoin']['usd'])
        except Exception as e:
            print(f"CoinGecko API error: {e}")
            return None
    
    def get_current_price(self) -> Optional[float]:
        price = self.fetch_price_coindesk()
        if price is None:
            price = self.fetch_price_coingecko()
        return price
    
    def check_price_alert(self, current_price: float) -> bool:
        if self.last_price is None:
            return False
        
        price_change_percent = abs((current_price - self.last_price) / self.last_price * 100)
        return price_change_percent >= self.alert_threshold
    
    def format_price_change(self, current_price: float) -> str:
        if self.last_price is None:
            return ""
        
        change = current_price - self.last_price
        change_percent = (change / self.last_price) * 100
        direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        
        return f"{direction} ${change:+.2f} ({change_percent:+.2f}%)"
    
    def monitor_price(self, interval_seconds: int = 60):
        print("🚀 Bitcoin Price Tracker Started")
        print(f"📊 Monitoring interval: {interval_seconds} seconds")
        print(f"⚠️  Alert threshold: {self.alert_threshold}%")
        print("-" * 50)
        
        while True:
            try:
                current_price = self.get_current_price()
                
                if current_price is None:
                    print(f"❌ Failed to fetch price at {datetime.now().strftime('%H:%M:%S')}")
                    time.sleep(interval_seconds)
                    continue
                
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                price_change_info = self.format_price_change(current_price)
                
                self.price_history.append({
                    'timestamp': timestamp,
                    'price': current_price
                })
                
                if len(self.price_history) > 100:
                    self.price_history = self.price_history[-50:]
                
                alert_triggered = self.check_price_alert(current_price)
                alert_indicator = "🚨 ALERT! " if alert_triggered else ""
                
                print(f"{alert_indicator}[{timestamp}] BTC: ${current_price:,.2f} {price_change_info}")
                
                if alert_triggered:
                    print(f"🔔 Significant price movement detected!")
                
                self.last_price = current_price
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n👋 Price monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                time.sleep(interval_seconds)
    
    def get_price_summary(self) -> Dict:
        if not self.price_history:
            return {}
        
        prices = [item['price'] for item in self.price_history]
        return {
            'current_price': prices[-1] if prices else None,
            'highest_price': max(prices),
            'lowest_price': min(prices),
            'average_price': sum(prices) / len(prices),
            'total_records': len(prices)
        }

def main():
    try:
        threshold = float(input("Enter alert threshold percentage (default 5.0): ") or "5.0")
        interval = int(input("Enter monitoring interval in seconds (default 60): ") or "60")
        
        tracker = BTCPriceTracker(alert_threshold_percent=threshold)
        tracker.monitor_price(interval_seconds=interval)
        
    except ValueError:
        print("❌ Invalid input. Using default values.")
        tracker = BTCPriceTracker()
        tracker.monitor_price()
    except Exception as e:
        print(f"❌ Error starting tracker: {e}")

if __name__ == "__main__":
    main()