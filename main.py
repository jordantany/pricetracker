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

class SolanaMemeTracker:
    def __init__(self, contract_addresses: list, alert_threshold_percent: float = 10.0):
        self.contract_addresses = contract_addresses
        self.dexscreener_api_url = "https://api.dexscreener.com/latest/dex/tokens"
        self.jupiter_api_url = "https://price.jup.ag/v4/price"
        self.alert_threshold = alert_threshold_percent
        self.last_prices = {}
        self.token_info = {}
        self.price_history = {addr: [] for addr in contract_addresses}
    
    def fetch_token_info_dexscreener(self, contract_address: str) -> Optional[Dict]:
        try:
            url = f"{self.dexscreener_api_url}/{contract_address}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'pairs' in data and data['pairs']:
                pair = data['pairs'][0]
                return {
                    'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                    'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
                    'price_usd': float(pair.get('priceUsd', 0)),
                    'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                    'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                    'liquidity': float(pair.get('liquidity', {}).get('usd', 0))
                }
        except Exception as e:
            print(f"DexScreener API error for {contract_address}: {e}")
        return None
    
    def fetch_price_jupiter(self, contract_address: str) -> Optional[float]:
        try:
            url = f"{self.jupiter_api_url}?ids={contract_address}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and contract_address in data['data']:
                return float(data['data'][contract_address]['price'])
        except Exception as e:
            print(f"Jupiter API error for {contract_address}: {e}")
        return None
    
    def get_token_data(self, contract_address: str) -> Optional[Dict]:
        token_info = self.fetch_token_info_dexscreener(contract_address)
        if token_info and token_info['price_usd'] > 0:
            return token_info
        
        jupiter_price = self.fetch_price_jupiter(contract_address)
        if jupiter_price:
            return {
                'name': self.token_info.get(contract_address, {}).get('name', 'Unknown'),
                'symbol': self.token_info.get(contract_address, {}).get('symbol', 'UNKNOWN'),
                'price_usd': jupiter_price,
                'volume_24h': 0,
                'price_change_24h': 0,
                'liquidity': 0
            }
        
        return None
    
    def check_price_alert(self, contract_address: str, current_price: float) -> bool:
        if contract_address not in self.last_prices or self.last_prices[contract_address] is None:
            return False
        
        last_price = self.last_prices[contract_address]
        price_change_percent = abs((current_price - last_price) / last_price * 100)
        return price_change_percent >= self.alert_threshold
    
    def format_price_change(self, contract_address: str, current_price: float) -> str:
        if contract_address not in self.last_prices or self.last_prices[contract_address] is None:
            return ""
        
        last_price = self.last_prices[contract_address]
        change = current_price - last_price
        change_percent = (change / last_price) * 100
        direction = "🚀" if change > 0 else "💥" if change < 0 else "➡️"
        
        return f"{direction} ${change:+.8f} ({change_percent:+.2f}%)"
    
    def monitor_meme_coins(self, interval_seconds: int = 30):
        print(f"🎭 Solana Meme Coin Tracker Started - Monitoring {len(self.contract_addresses)} tokens")
        print(f"📊 Monitoring interval: {interval_seconds} seconds")
        print(f"⚠️  Alert threshold: {self.alert_threshold}%")
        print("-" * 80)
        
        for addr in self.contract_addresses:
            token_data = self.get_token_data(addr)
            if token_data:
                self.token_info[addr] = token_data
                print(f"📋 {token_data['symbol']} ({token_data['name']}) - {addr[:8]}...{addr[-8:]}")
        print("-" * 80)
        
        while True:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                for contract_address in self.contract_addresses:
                    token_data = self.get_token_data(contract_address)
                    
                    if not token_data or token_data['price_usd'] == 0:
                        print(f"❌ Failed to fetch price for {contract_address[:8]}...{contract_address[-8:]}")
                        continue
                    
                    current_price = token_data['price_usd']
                    symbol = token_data['symbol']
                    
                    price_change_info = self.format_price_change(contract_address, current_price)
                    
                    self.price_history[contract_address].append({
                        'timestamp': timestamp,
                        'price': current_price,
                        'volume_24h': token_data.get('volume_24h', 0),
                        'liquidity': token_data.get('liquidity', 0)
                    })
                    
                    if len(self.price_history[contract_address]) > 100:
                        self.price_history[contract_address] = self.price_history[contract_address][-50:]
                    
                    alert_triggered = self.check_price_alert(contract_address, current_price)
                    alert_indicator = "🚨 MOON! " if alert_triggered else ""
                    
                    volume_info = f"Vol: ${token_data.get('volume_24h', 0):,.0f}" if token_data.get('volume_24h', 0) > 0 else ""
                    liquidity_info = f"Liq: ${token_data.get('liquidity', 0):,.0f}" if token_data.get('liquidity', 0) > 0 else ""
                    
                    print(f"{alert_indicator}[{timestamp}] {symbol}: ${current_price:.8f} {price_change_info} {volume_info} {liquidity_info}")
                    
                    if alert_triggered:
                        print(f"🎯 Significant price movement detected for {symbol}!")
                    
                    self.last_prices[contract_address] = current_price
                
                print()
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n👋 Meme coin monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                time.sleep(interval_seconds)

def main():
    try:
        print("🔧 Crypto Price Tracker Configuration")
        print("1. Monitor mainstream cryptocurrencies (BTC, ETH, SOL, BNB, XRP)")
        print("2. Monitor Solana meme coins by contract address")
        
        mode = input("Select mode (1 or 2, default 1): ").strip() or "1"
        
        if mode == "2":
            print("\n🎭 Solana Meme Coin Tracker Setup")
            print("Enter Solana token contract addresses (one per line, empty line to finish):")
            print("Example: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263 (Bonk)")
            
            contract_addresses = []
            while True:
                addr = input(f"Contract address #{len(contract_addresses) + 1}: ").strip()
                if not addr:
                    break
                if len(addr) >= 32:  # Basic validation for Solana address length
                    contract_addresses.append(addr)
                else:
                    print("⚠️  Invalid address format. Solana addresses should be 32-44 characters.")
            
            if not contract_addresses:
                print("❌ No contract addresses provided. Exiting.")
                return
            
            threshold = float(input("Enter alert threshold percentage (default 10.0): ") or "10.0")
            interval = int(input("Enter monitoring interval in seconds (default 30): ") or "30")
            
            meme_tracker = SolanaMemeTracker(contract_addresses=contract_addresses, alert_threshold_percent=threshold)
            meme_tracker.monitor_meme_coins(interval_seconds=interval)
            
        else:
            print("\n🚀 Mainstream Crypto Tracker Setup")
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