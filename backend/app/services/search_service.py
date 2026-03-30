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
    "baidu": {
        "name": "百度",
        "url": "https://www.baidu.com/s?wd={query}&pn={offset}",
        "offset_calc": lambda page: (page - 1) * 10,
        "priority": 1,
    },
    "bing": {
        "name": "Bing搜索",
        "url": "https://cn.bing.com/search?q={query}&first={offset}",
        "offset_calc": lambda page: (page - 1) * 10,
        "priority": 2,
    },
    "sogou": {
        "name": "搜狗",
        "url": "https://www.sogou.com/web?query={query}&page={page}",
        "offset_calc": lambda page: page,
        "priority": 3,
    },
    "toutiao": {
        "name": "头条",
        "url": "https://so.toutiao.com/search?keyword={query}&page={page}",
        "offset_calc": lambda page: page,
        "priority": 4,
    },
    "csdn": {
        "name": "CSDN",
        "url": "https://so.csdn.net/so/search?q={query}&page={page}",
        "offset_calc": lambda page: page,
        "priority": 5,
    },
}

class SearchService:
    def __init__(self):
        self.timeout = 45.0
        self.max_retries = 3
        self.retry_delay = 2
        self.max_results_per_source = 5

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
            url_template = source_info.get("url", "")
            offset_calc = source_info.get("offset_calc", lambda p: p)
            offset = offset_calc(page)
            url = url_template.format(query=query, page=page, offset=offset)
            name = source_info.get("name", source)

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

            parsers = {
                "baidu": self._parse_baidu,
                "bing": self._parse_bing,
                "sogou": self._parse_sogou,
                "toutiao": self._parse_toutiao,
                "csdn": self._parse_csdn,
            }
            
            parser = parsers.get(source)
            if parser:
                results = parser(soup, name)

        except Exception as e:
            print(f"Parse Error [{source}]: {e}")
        return results

    def _parse_baidu(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".result, .c-container")[:self.max_results_per_source]:
            title_elem = item.select_one("h3 a") or item.select_one("a")
            snippet_elem = item.select_one(".c-abstract") or item.select_one(".content-right")
            date_elem = item.select_one(".c-color-gray") or item.select_one(".c-author")
            if title_elem and title_elem.get("href"):
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=title_elem.get("href", ""),
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    date=date_elem.get_text(strip=True) if date_elem else None,
                    source=name
                ))
        return results

    def _parse_bing(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select("li.b_algo")[:self.max_results_per_source]:
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

    def _parse_sogou(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".vrwrap, .result")[:self.max_results_per_source]:
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

    def _parse_toutiao(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".article-card, .result-item")[:self.max_results_per_source]:
            title_elem = item.select_one(".article-title, .title")
            link_elem = item.select_one("a")
            snippet_elem = item.select_one(".article-desc, .desc")
            title = title_elem.get_text(strip=True) if title_elem else ""
            if title:
                results.append(SearchResult(
                    title=title,
                    url=link_elem.get("href", "") if link_elem else "",
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name
                ))
        return results

    def _parse_csdn(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".article-item, .search-item")[:self.max_results_per_source]:
            title_elem = item.select_one(".article-title a") or item.select_one("h4 a")
            link_elem = item.select_one("a")
            snippet_elem = item.select_one(".description, .article-snippet")
            if title_elem:
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=link_elem.get("href", "") if link_elem else "",
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
        sorted_sources = sorted(CRAWLER_SOURCES.items(), key=lambda x: x[1]["priority"])

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            for source, _ in sorted_sources:
                results = await self._fetch_page(client, source, query, page)
                all_results.extend(results)
                await asyncio.sleep(random.uniform(0.5, 2.0))

        seen_urls = set()
        unique_results = []
        for r in all_results:
            if r.url and r.url.startswith("http") and r.url not in seen_urls:
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
