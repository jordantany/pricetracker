#!/usr/bin/env python3

import requests
import time
from datetime import datetime
from typing import Dict, Optional

class CryptoPriceTracker:
    def __init__(self, coins: list = ['bitcoin', 'ethereum', 'solana', 'binancecoin', 'ripple'], alert_threshold_percent: float = 5.0):
        self.coins = coins
        self.coin_symbols = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH',
            'solana': 'SOL',
            'binancecoin': 'BNB',
            'ripple': 'XRP'
        }
        self.coingecko_api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.alert_threshold = alert_threshold_percent
        self.last_prices = {}
        self.price_history = {coin: [] for coin in coins}
    
    def fetch_all_prices(self) -> Dict[str, Optional[float]]:
        try:
            coin_ids = ','.join(self.coins)
            url = f"{self.coingecko_api_url}?ids={coin_ids}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            prices = {}
            for coin in self.coins:
                if coin in data and 'usd' in data[coin]:
                    prices[coin] = float(data[coin]['usd'])
                else:
                    prices[coin] = None
            
            return prices
        except Exception as e:
            print(f"CoinGecko API error: {e}")
            return {coin: None for coin in self.coins}
    
    def check_price_alert(self, coin: str, current_price: float) -> bool:
        if coin not in self.last_prices or self.last_prices[coin] is None:
            return False
        
        last_price = self.last_prices[coin]
        price_change_percent = abs((current_price - last_price) / last_price * 100)
        return price_change_percent >= self.alert_threshold
    
    def format_price_change(self, coin: str, current_price: float) -> str:
        if coin not in self.last_prices or self.last_prices[coin] is None:
            return ""
        
        last_price = self.last_prices[coin]
        change = current_price - last_price
        change_percent = (change / last_price) * 100
        direction = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        
        return f"{direction} ${change:+.2f} ({change_percent:+.2f}%)"
    
    def monitor_price(self, interval_seconds: int = 60):
        coin_names = [self.coin_symbols.get(coin, coin.upper()) for coin in self.coins]
        print(f"🚀 Crypto Price Tracker Started - Monitoring: {', '.join(coin_names)}")
        print(f"📊 Monitoring interval: {interval_seconds} seconds")
        print(f"⚠️  Alert threshold: {self.alert_threshold}%")
        print("-" * 70)
        
        while True:
            try:
                current_prices = self.fetch_all_prices()
                
                if all(price is None for price in current_prices.values()):
                    print(f"❌ Failed to fetch prices at {datetime.now().strftime('%H:%M:%S')}")
                    time.sleep(interval_seconds)
                    continue
                
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                for coin in self.coins:
                    current_price = current_prices[coin]
                    if current_price is None:
                        continue
                    
                    price_change_info = self.format_price_change(coin, current_price)
                    
                    self.price_history[coin].append({
                        'timestamp': timestamp,
                        'price': current_price
                    })
                    
                    if len(self.price_history[coin]) > 100:
                        self.price_history[coin] = self.price_history[coin][-50:]
                    
                    alert_triggered = self.check_price_alert(coin, current_price)
                    alert_indicator = "🚨 ALERT! " if alert_triggered else ""
                    
                    symbol = self.coin_symbols.get(coin, coin.upper())
                    print(f"{alert_indicator}[{timestamp}] {symbol}: ${current_price:,.2f} {price_change_info}")
                    
                    if alert_triggered:
                        print(f"🔔 Significant price movement detected for {symbol}!")
                    
                    self.last_prices[coin] = current_price
                
                print()
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n👋 Price monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                time.sleep(interval_seconds)
    
    def get_price_summary(self) -> Dict:
        summary = {}
        for coin in self.coins:
            if not self.price_history[coin]:
                summary[coin] = {}
                continue
            
            prices = [item['price'] for item in self.price_history[coin]]
            summary[coin] = {
                'symbol': self.coin_symbols.get(coin, coin.upper()),
                'current_price': prices[-1] if prices else None,
                'highest_price': max(prices),
                'lowest_price': min(prices),
                'average_price': sum(prices) / len(prices),
                'total_records': len(prices)
            }
        return summary

def main():
    try:
        print("🔧 Crypto Price Tracker Configuration")
        print("Available cryptocurrencies: BTC (bitcoin), ETH (ethereum), SOL (solana), BNB (binancecoin), XRP (ripple)")
        
        coins_input = input("Enter coins to monitor (default: bitcoin,ethereum,solana,binancecoin,ripple): ").strip()
        if not coins_input:
            coins = ['bitcoin', 'ethereum', 'solana', 'binancecoin', 'ripple']
        else:
            coin_map = {
                'btc': 'bitcoin', 'bitcoin': 'bitcoin',
                'eth': 'ethereum', 'ethereum': 'ethereum',
                'sol': 'solana', 'solana': 'solana',
                'bnb': 'binancecoin', 'binancecoin': 'binancecoin',
                'xrp': 'ripple', 'ripple': 'ripple'
            }
            coins = []
            for coin in coins_input.lower().split(','):
                coin = coin.strip()
                if coin in coin_map:
                    coins.append(coin_map[coin])
                else:
                    print(f"⚠️  Unknown coin: {coin}, skipping...")
            
            if not coins:
                print("❌ No valid coins selected. Using defaults.")
                coins = ['bitcoin', 'ethereum', 'solana', 'binancecoin', 'ripple']
        
        threshold = float(input("Enter alert threshold percentage (default 5.0): ") or "5.0")
        interval = int(input("Enter monitoring interval in seconds (default 60): ") or "60")
        
        tracker = CryptoPriceTracker(coins=coins, alert_threshold_percent=threshold)
        tracker.monitor_price(interval_seconds=interval)
        
    except ValueError:
        print("❌ Invalid input. Using default values.")
        tracker = CryptoPriceTracker()
        tracker.monitor_price()
    except Exception as e:
        print(f"❌ Error starting tracker: {e}")

if __name__ == "__main__":
    main()