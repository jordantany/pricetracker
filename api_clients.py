import requests
from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from config import APIEndpoints

class APIClient(ABC):
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def _make_request(self, url: str) -> Optional[Dict]:
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API request error for {url}: {e}")
            return None

class CoinGeckoClient(APIClient):
    def get_prices(self, coin_ids: List[str]) -> Dict[str, Optional[float]]:
        coin_ids_str = ','.join(coin_ids)
        url = f"{APIEndpoints.COINGECKO_PRICE}?ids={coin_ids_str}&vs_currencies=usd"
        data = self._make_request(url)
        
        if not data:
            return {coin: None for coin in coin_ids}
        
        prices = {}
        for coin in coin_ids:
            if coin in data and 'usd' in data[coin]:
                prices[coin] = float(data[coin]['usd'])
            else:
                prices[coin] = None
        
        return prices

class DexScreenerClient(APIClient):
    def get_token_info(self, contract_address: str) -> Optional[Dict]:
        url = f"{APIEndpoints.DEXSCREENER_TOKENS}/{contract_address}"
        data = self._make_request(url)
        
        if not data or 'pairs' not in data or not data['pairs']:
            return None
        
        pair = data['pairs'][0]
        return {
            'name': pair.get('baseToken', {}).get('name', 'Unknown'),
            'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN'),
            'price_usd': float(pair.get('priceUsd', 0)),
            'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
            'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
            'liquidity': float(pair.get('liquidity', {}).get('usd', 0))
        }

class JupiterClient(APIClient):
    def get_price(self, contract_address: str) -> Optional[float]:
        url = f"{APIEndpoints.JUPITER_PRICE}?ids={contract_address}"
        data = self._make_request(url)
        
        if not data or 'data' not in data or contract_address not in data['data']:
            return None
        
        return float(data['data'][contract_address]['price'])