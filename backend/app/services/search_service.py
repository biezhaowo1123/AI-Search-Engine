import httpx
import hashlib
import time
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from backend.app.config import config
    from backend.app.models.schemas import SearchResult
    from backend.app.services.cache_service import cache_service
except ModuleNotFoundError:
    from app.config import config
    from app.models.schemas import SearchResult
    from app.services.cache_service import cache_service

class SearchService:
    def __init__(self):
        self.api_url = config.SHENMA_API_URL
        self.app_key = config.SHENMA_APP_KEY
        self.app_secret = config.SHENMA_APP_SECRET

    def _generate_signature(self, params: dict) -> str:
        sorted_params = sorted(params.items())
        sign_str = "".join([f"{k}{v}" for k, v in sorted_params])
        sign_str += self.app_secret
        return hashlib.md5(sign_str.encode()).hexdigest()

    async def search(self, query: str, page: int = 1, page_size: int = 20) -> tuple[list[SearchResult], bool]:
        cache_key = cache_service.generate_search_key(query, page)
        cached = cache_service.get(cache_key)
        if cached:
            results = [SearchResult(**r) for r in cached["results"]]
            return results, True

        params = {
            "app_key": self.app_key,
            "query": query,
            "page": page,
            "page_size": page_size,
            "timestamp": int(time.time())
        }
        params["sign"] = self._generate_signature(params)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.api_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results = self._parse_results(data)
                    cache_service.set(cache_key, {
                        "results": [r.model_dump() for r in results]
                    }, config.CACHE_TTL_SEARCH)
                    return results, False
        except Exception as e:
            print(f"Search Error: {e}")

        return [], False

    def _parse_results(self, data: dict) -> list[SearchResult]:
        results = []
        items = data.get("results", [])
        for item in items:
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
                date=item.get("date")
            ))
        return results

search_service = SearchService()
