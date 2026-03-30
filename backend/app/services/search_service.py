import httpx
import asyncio
from typing import Optional, AsyncGenerator
from bs4 import BeautifulSoup
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

CRAWLER_SOURCES = {
    "zhihu": {
        "name": "知乎",
        "url": "https://www.zhihu.com/search?type=content&q={query}",
    },
    "weibo": {
        "name": "微博",
        "url": "https://s.weibo.com/weibo?q={query}",
    },
    "baidu_news": {
        "name": "百度新闻",
        "url": "https://www.baidu.com/s?wd={query}&tn=news",
    },
}

class SearchService:
    def __init__(self):
        self.timeout = 30.0

    async def _fetch_page(self, client: httpx.AsyncClient, source: str, query: str) -> list[SearchResult]:
        try:
            source_info = CRAWLER_SOURCES.get(source, {})
            url = source_info["url"].format(query=query)
            name = source_info["name"]

            response = await client.get(url, headers=HEADERS, timeout=self.timeout)
            if response.status_code == 200:
                return self._parse_html(source, response.text, query, name)
        except Exception as e:
            print(f"Crawler Error [{source}]: {e}")
        return []

    def _parse_html(self, source: str, html: str, query: str, name: str) -> list[SearchResult]:
        results = []
        try:
            soup = BeautifulSoup(html, "html.parser")

            if source == "zhihu":
                results = self._parse_zhihu(soup, name)
            elif source == "weibo":
                results = self._parse_weibo(soup, name)
            elif source == "baidu_news":
                results = self._parse_baidu_news(soup, name)

            results = [r for r in results if query.lower() in r.title.lower() or query.lower() in r.snippet.lower()]
        except Exception as e:
            print(f"Parse Error [{source}]: {e}")
        return results

    def _parse_zhihu(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".List-item")[:10]:
            title_elem = item.select_one(".ContentItem-title")
            link_elem = item.select_one("a")
            snippet_elem = item.select_one(".RichText")
            if title_elem and link_elem:
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=link_elem.get("href", ""),
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name
                ))
        return results

    def _parse_weibo(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".card-feed")[:10]:
            title_elem = item.select_one(".txt")
            link_elem = item.select_one("a")
            if title_elem:
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True)[:100],
                    url=f"https://weibo.com{link_elem.get('href', '')}" if link_elem else "",
                    snippet=title_elem.get_text(strip=True),
                    source=name
                ))
        return results

    def _parse_baidu_news(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".news-item")[:10]:
            title_elem = item.select_one("h3 a")
            snippet_elem = item.select_one(".c-author")
            if title_elem:
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=title_elem.get("href", ""),
                    snippet=snippet_elem.get_text(strip=True) if snippet_elem else "",
                    source=name
                ))
        return results

    async def search(self, query: str, page: int = 1, page_size: int = 20) -> tuple[list[SearchResult], bool]:
        cache_key = cache_service.generate_search_key(query, page)
        cached = cache_service.get(cache_key)
        if cached:
            results = [SearchResult(**r) for r in cached["results"]]
            return results[:page_size], True

        all_results = []
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            tasks = [
                self._fetch_page(client, source, query)
                for source in CRAWLER_SOURCES.keys()
            ]
            source_results = await asyncio.gather(*tasks, return_exceptions=True)

            for results in source_results:
                if isinstance(results, list):
                    all_results.extend(results)

        seen_urls = set()
        unique_results = []
        for r in all_results:
            if r.url and r.url not in seen_urls:
                seen_urls.add(r.url)
                unique_results.append(r)

        cache_service.set(cache_key, {
            "results": [r.model_dump() for r in unique_results]
        }, config.CACHE_TTL_SEARCH)

        start = (page - 1) * page_size
        end = start + page_size
        return unique_results[start:end], False

search_service = SearchService()
