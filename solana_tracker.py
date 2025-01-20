from typing import Dict, Optional
from base_tracker import BaseTracker, PriceData
from api_clients import DexScreenerClient, JupiterClient
from config import SolanaMemeConfig

class SolanaMemeTracker(BaseTracker):
    def __init__(self, config: SolanaMemeConfig):
        super().__init__(config)
        self.config = config
        self.dexscreener_client = DexScreenerClient()
        self.jupiter_client = JupiterClient()
        self.token_info: Dict[str, Dict] = {}
        
        for addr in self.config.contract_addresses:
            self.price_history[addr] = []
    
    def fetch_token_data(self, contract_address: str) -> Optional[Dict]:
        token_info = self.dexscreener_client.get_token_info(contract_address)
        if token_info and token_info['price_usd'] > 0:
            return token_info
        
        jupiter_price = self.jupiter_client.get_price(contract_address)
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
    
    def fetch_prices(self) -> Dict[str, Optional[float]]:
        prices = {}
        for contract_address in self.config.contract_addresses:
            token_data = self.fetch_token_data(contract_address)
            if token_data:
                prices[contract_address] = token_data['price_usd']
                self.token_info[contract_address] = token_data
            else:
                prices[contract_address] = None
        return prices
    
    def get_display_name(self, identifier: str) -> str:
        if identifier in self.token_info:
            return self.token_info[identifier].get('symbol', 'UNKNOWN')
        return f"{identifier[:8]}...{identifier[-8:]}"
    
    def display_price_info(self, identifier: str, price: float, timestamp: str, **kwargs):
        alert_triggered = kwargs.get('alert_triggered', False)
        symbol = self.get_display_name(identifier)
        price_change_info = self.format_price_change(identifier, price, "🚀", "💥", "➡️")
        alert_indicator = "🚨 MOON! " if alert_triggered else ""
        
        token_data = self.token_info.get(identifier, {})
        volume_info = f"Vol: ${token_data.get('volume_24h', 0):,.0f}" if token_data.get('volume_24h', 0) > 0 else ""
        liquidity_info = f"Liq: ${token_data.get('liquidity', 0):,.0f}" if token_data.get('liquidity', 0) > 0 else ""
        
        print(f"{alert_indicator}[{timestamp}] {symbol}: ${price:.8f} {price_change_info} {volume_info} {liquidity_info}")
    
    def handle_alert(self, identifier: str, price: float):
        symbol = self.get_display_name(identifier)
        print(f"🎯 Significant price movement detected for {symbol}!")
    
    def print_startup_info(self):
        print(f"🎭 Solana Meme Coin Tracker Started - Monitoring {len(self.config.contract_addresses)} tokens")
        print(f"📊 Monitoring interval: {self.config.monitoring_interval_seconds} seconds")
        print(f"⚠️  Alert threshold: {self.config.alert_threshold_percent}%")
        print("-" * 80)
        
        for addr in self.config.contract_addresses:
            token_data = self.fetch_token_data(addr)
            if token_data:
                self.token_info[addr] = token_data
                print(f"📋 {token_data['symbol']} ({token_data['name']}) - {addr[:8]}...{addr[-8:]}")
        print("-" * 80)
    
    def update_price_history(self, identifier: str, price_data: PriceData):
        token_data = self.token_info.get(identifier, {})
        enhanced_price_data = PriceData(
            price_data.timestamp,
            price_data.price,
            volume_24h=token_data.get('volume_24h', 0),
            liquidity=token_data.get('liquidity', 0)
        )
        super().update_price_history(identifier, enhanced_price_data)