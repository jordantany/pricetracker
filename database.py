import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

class PriceDatabase:
    def __init__(self, db_path: str = "price_tracker.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    coin_id TEXT NOT NULL,
                    price_usd REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    volume_24h REAL DEFAULT 0,
                    market_cap REAL DEFAULT 0,
                    price_change_24h REAL DEFAULT 0,
                    extra_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_symbol_timestamp 
                ON price_records(symbol, timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_coin_timestamp 
                ON price_records(coin_id, timestamp)
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def insert_price_record(self, symbol: str, coin_id: str, price_usd: float, 
                          timestamp: str = None, **kwargs) -> bool:
        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            extra_data = {}
            volume_24h = kwargs.get('volume_24h', 0)
            market_cap = kwargs.get('market_cap', 0)
            price_change_24h = kwargs.get('price_change_24h', 0)
            
            for key, value in kwargs.items():
                if key not in ['volume_24h', 'market_cap', 'price_change_24h']:
                    extra_data[key] = value
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO price_records 
                    (symbol, coin_id, price_usd, timestamp, volume_24h, market_cap, price_change_24h, extra_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, coin_id, price_usd, timestamp, volume_24h, market_cap, price_change_24h, json.dumps(extra_data)))
                conn.commit()
                return True
        except Exception as e:
            print(f"Database insert error: {e}")
            return False
    
    def get_latest_price(self, coin_id: str) -> Optional[Dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM price_records 
                    WHERE coin_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ''', (coin_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Database query error: {e}")
            return None
    
    def get_price_history(self, coin_id: str, limit: int = 100) -> List[Dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM price_records 
                    WHERE coin_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (coin_id, limit))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Database query error: {e}")
            return []
    
    def get_price_stats(self, coin_id: str, hours: int = 24) -> Optional[Dict]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COUNT(*) as record_count,
                        MIN(price_usd) as min_price,
                        MAX(price_usd) as max_price,
                        AVG(price_usd) as avg_price,
                        MIN(timestamp) as earliest_time,
                        MAX(timestamp) as latest_time
                    FROM price_records 
                    WHERE coin_id = ? 
                    AND timestamp >= datetime('now', '-{} hours')
                '''.format(hours), (coin_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"Database query error: {e}")
            return None
    
    def cleanup_old_records(self, days: int = 30):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM price_records 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                deleted_count = cursor.rowcount
                conn.commit()
                print(f"Cleaned up {deleted_count} old records (older than {days} days)")
        except Exception as e:
            print(f"Database cleanup error: {e}")
    
    def get_database_info(self) -> Dict:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) as total_records FROM price_records')
                total_records = cursor.fetchone()['total_records']
                
                cursor.execute('''
                    SELECT symbol, COUNT(*) as count 
                    FROM price_records 
                    GROUP BY symbol
                ''')
                symbol_counts = {row['symbol']: row['count'] for row in cursor.fetchall()}
                
                return {
                    'total_records': total_records,
                    'symbol_counts': symbol_counts,
                    'database_path': self.db_path
                }
        except Exception as e:
            print(f"Database info error: {e}")
            return {}