# src/storage/cache_engine.py
import redis
import pickle
from typing import Any, Optional

class CacheManager:
    def __init__(self, host: str = 'localhost', port: int = 6379):
        self.pool = redis.ConnectionPool(host=host, port=port, decode_responses=False)
        
    def get(self, key: str) -> Optional[Any]:
        with redis.Redis(connection_pool=self.pool) as conn:
            data = conn.get(key)
            return pickle.loads(data) if data else None
            
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        with redis.Redis(connection_pool=self.pool) as conn:
            conn.set(key, pickle.dumps(value), ex=ttl)
            
    def delete(self, key: str) -> None:
        with redis.Redis(connection_pool=self.pool) as conn:
            conn.delete(key)
