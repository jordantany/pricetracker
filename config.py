from typing import Dict, List
from dataclasses import dataclass

@dataclass
class TrackerConfig:
    alert_threshold_percent: float = 5.0
    monitoring_interval_seconds: int = 60
    max_price_history: int = 100
    keep_history_count: int = 50

@dataclass
class MainstreamCryptoConfig(TrackerConfig):
    coins: List[str] = None
    alert_threshold_percent: float = 5.0
    monitoring_interval_seconds: int = 60
    
    def __post_init__(self):
        if self.coins is None:
            self.coins = ['bitcoin', 'ethereum', 'solana', 'binancecoin', 'ripple']

@dataclass
class SolanaMemeConfig(TrackerConfig):
    contract_addresses: List[str] = None
    alert_threshold_percent: float = 10.0
    monitoring_interval_seconds: int = 30
    
    def __post_init__(self):
        if self.contract_addresses is None:
            self.contract_addresses = []

class CoinSymbols:
    MAINSTREAM_COINS = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH',
        'solana': 'SOL',
        'binancecoin': 'BNB',
        'ripple': 'XRP'
    }
    
    COIN_MAP = {
        'btc': 'bitcoin', 'bitcoin': 'bitcoin',
        'eth': 'ethereum', 'ethereum': 'ethereum',
        'sol': 'solana', 'solana': 'solana',
        'bnb': 'binancecoin', 'binancecoin': 'binancecoin',
        'xrp': 'ripple', 'ripple': 'ripple'
    }

class APIEndpoints:
    COINGECKO_PRICE = "https://api.coingecko.com/api/v3/simple/price"
    DEXSCREENER_TOKENS = "https://api.dexscreener.com/latest/dex/tokens"
    JUPITER_PRICE = "https://price.jup.ag/v4/price"