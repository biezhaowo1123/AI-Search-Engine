import json
import redis
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from backend.app.config import config
except ModuleNotFoundError:
    from app.config import config

class CacheService:
    def __init__(self):
        self.client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[dict]:
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, value: dict, ttl: int = 1800):
        self.client.setex(key, ttl, json.dumps(value))

    def delete(self, key: str):
        self.client.delete(key)

    def generate_search_key(self, query: str, page: int) -> str:
        return f"search:{query}:{page}"

    def generate_summary_key(self, query: str) -> str:
        return f"summary:{query}"

cache_service = CacheService()
