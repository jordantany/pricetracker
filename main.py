#!/usr/bin/env python3

from mainstream_tracker import MainstreamCryptoTracker
from solana_tracker import SolanaMemeTracker
from user_interface import UserInterface
from config import MainstreamCryptoConfig, SolanaMemeConfig

def main():
    try:
        tracker_type, config = UserInterface.handle_user_input()
        
        if tracker_type == "solana":
            tracker = SolanaMemeTracker(config)
        else:
            tracker = MainstreamCryptoTracker(config)
        
        tracker.start_monitoring()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Using default mainstream crypto tracker...")
        default_config = MainstreamCryptoConfig()
        tracker = MainstreamCryptoTracker(default_config)
        tracker.start_monitoring()
    except Exception as e:
        print(f"❌ Error starting tracker: {e}")

if __name__ == "__main__":
    main()