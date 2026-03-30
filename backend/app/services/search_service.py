import httpx
import asyncio
import random
from typing import Optional
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

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def get_random_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

CRAWLER_SOURCES = {
    "bing": {
        "name": "Bing搜索",
        "url": "https://cn.bing.com/search?q={query}&first={page}",
    },
    "baidu": {
        "name": "百度",
        "url": "https://www.baidu.com/s?wd={query}&pn={(page-1)*10}",
    },
    "sogou": {
        "name": "搜狗",
        "url": "https://www.sogou.com/web?query={query}&page={page}",
    },
}

class SearchService:
    def __init__(self):
        self.timeout = 45.0
        self.max_retries = 3
        self.retry_delay = 2

    async def _fetch_with_retry(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        for attempt in range(self.max_retries):
            try:
                headers = get_random_headers()
                response = await client.get(url, headers=headers, timeout=self.timeout)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    print(f"Access forbidden (403): {url}")
                elif response.status_code == 429:
                    print(f"Rate limited (429): {url}, waiting...")
                    await asyncio.sleep(self.retry_delay * 2)
            except Exception as e:
                print(f"Fetch attempt {attempt + 1} failed for {url}: {e}")
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))
        
        return None

    async def _fetch_page(self, client: httpx.AsyncClient, source: str, query: str, page: int = 1) -> list[SearchResult]:
        try:
            source_info = CRAWLER_SOURCES.get(source, {})
            url = source_info["url"].format(query=query, page=page)
            name = source_info["name"]

            html = await self._fetch_with_retry(client, url)
            if html:
                return self._parse_html(source, html, query, name)
        except Exception as e:
            print(f"Crawler Error [{source}]: {e}")
        return []

    def _parse_html(self, source: str, html: str, query: str, name: str) -> list[SearchResult]:
        results = []
        try:
            soup = BeautifulSoup(html, "lxml")

            if source == "bing":
                results = self._parse_bing(soup, name)
            elif source == "baidu":
                results = self._parse_baidu(soup, name)
            elif source == "sogou":
                results = self._parse_sogou(soup, name)

        except Exception as e:
            print(f"Parse Error [{source}]: {e}")
        return results

    def _parse_bing(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select("li.b_algo")[:10]:
            title_elem = item.select_one("h2 a")
            snippet_elem = item.select_one("p")
            if title_elem:
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=title_elem.get("href", ""),
                    snippet=snippet_elem.get_text(strip=True) if snippet_elem else "",
                    source=name
                ))
        return results

    def _parse_baidu(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".result, .c-container")[:10]:
            title_elem = item.select_one("h3 a") or item.select_one("a")
            snippet_elem = item.select_one(".c-abstract") or item.select_one(".content-right")
            date_elem = item.select_one(".c-color-gray") or item.select_one(".c-author")
            if title_elem:
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=title_elem.get("href", ""),
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    date=date_elem.get_text(strip=True) if date_elem else None,
                    source=name
                ))
        return results

    def _parse_sogou(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".vrwrap, .result")[:10]:
            title_elem = item.select_one("h3 a") or item.select_one(".rb_title a")
            snippet_elem = item.select_one(".str-text, .rb_desc")
            if title_elem:
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=title_elem.get("href", ""),
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
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
            for source in CRAWLER_SOURCES.keys():
                results = await self._fetch_page(client, source, query, page)
                all_results.extend(results)
                await asyncio.sleep(random.uniform(1.0, 3.0))

        seen_urls = set()
        unique_results = []
        for r in all_results:
            if r.url and r.url not in seen_urls and r.url.startswith("http"):
                seen_urls.add(r.url)
                unique_results.append(r)

        if unique_results:
            cache_service.set(cache_key, {
                "results": [r.model_dump() for r in unique_results]
            }, config.CACHE_TTL_SEARCH)

        start = (page - 1) * page_size
        end = start + page_size
        return unique_results[start:end], False

search_service = SearchService()
