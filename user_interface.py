from typing import List, Tuple
from config import MainstreamCryptoConfig, SolanaMemeConfig, CoinSymbols

class UserInterface:
    @staticmethod
    def get_tracker_mode() -> str:
        print("🔧 Crypto Price Tracker Configuration")
        print("1. Monitor mainstream cryptocurrencies (BTC, ETH, SOL, BNB, XRP)")
        print("2. Monitor Solana meme coins by contract address")
        
        mode = input("Select mode (1 or 2, default 1): ").strip() or "1"
        return mode
    
    @staticmethod
    def setup_mainstream_config() -> MainstreamCryptoConfig:
        print("\n🚀 Mainstream Crypto Tracker Setup")
        print("Available cryptocurrencies: BTC (bitcoin), ETH (ethereum), SOL (solana), BNB (binancecoin), XRP (ripple)")
        
        coins_input = input("Enter coins to monitor (default: bitcoin,ethereum,solana,binancecoin,ripple): ").strip()
        
        if not coins_input:
            coins = ['bitcoin', 'ethereum', 'solana', 'binancecoin', 'ripple']
        else:
            coins = []
            for coin in coins_input.lower().split(','):
                coin = coin.strip()
                if coin in CoinSymbols.COIN_MAP:
                    coins.append(CoinSymbols.COIN_MAP[coin])
                else:
                    print(f"⚠️  Unknown coin: {coin}, skipping...")
            
            if not coins:
                print("❌ No valid coins selected. Using defaults.")
                coins = ['bitcoin', 'ethereum', 'solana', 'binancecoin', 'ripple']
        
        threshold = float(input("Enter alert threshold percentage (default 5.0): ") or "5.0")
        interval = int(input("Enter monitoring interval in seconds (default 60): ") or "60")
        
        return MainstreamCryptoConfig(
            coins=coins,
            alert_threshold_percent=threshold,
            monitoring_interval_seconds=interval
        )
    
    @staticmethod
    def setup_solana_config() -> SolanaMemeConfig:
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
            raise ValueError("No contract addresses provided")
        
        threshold = float(input("Enter alert threshold percentage (default 10.0): ") or "10.0")
        interval = int(input("Enter monitoring interval in seconds (default 30): ") or "30")
        
        return SolanaMemeConfig(
            contract_addresses=contract_addresses,
            alert_threshold_percent=threshold,
            monitoring_interval_seconds=interval
        )
    
    @staticmethod
    def handle_user_input() -> Tuple[str, object]:
        try:
            mode = UserInterface.get_tracker_mode()
            
            if mode == "2":
                config = UserInterface.setup_solana_config()
                return "solana", config
            else:
                config = UserInterface.setup_mainstream_config()
                return "mainstream", config
                
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error during setup: {e}")
            raise