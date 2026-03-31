import httpx
import asyncio
import random
from typing import Optional
from bs4 import BeautifulSoup
import sys
from pathlib import Path
import urllib.parse

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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

COOKIES = {
    "baidu": "BAIDUID=test; BIDUPSID=test; PSTM=1234567890",
    "bing": "MUID=test; MOPHISH=1",
}

def get_random_headers(source=None):
    ua = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    if source and COOKIES.get(source):
        headers["Cookie"] = COOKIES[source]
    return headers

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
    "360": {
        "name": "360搜索",
        "url": "https://www.so.com/s?q={query}&pn={offset}",
        "offset_calc": lambda page: (page - 1) * 10,
        "priority": 4,
    },
    "weixin": {
        "name": "微信",
        "url": "https://weixin.sogou.com/weixin?type=2&query={query}&page={page}",
        "offset_calc": lambda page: page,
        "priority": 5,
    },
    "sina": {
        "name": "新浪搜索",
        "url": "https://search.sina.com.cn/?q={query}&range=all&c=news&from=index",
        "offset_calc": lambda page: page * 20,
        "priority": 6,
    },
    "ifeng": {
        "name": "凤凰网",
        "url": "https://search.ifeng.com/sofeng/search?query={query}&page={page}",
        "offset_calc": lambda page: page,
        "priority": 7,
    },
    "yandex": {
        "name": "Yandex",
        "url": "https://yandex.com/search/?text={query}&p={offset}",
        "offset_calc": lambda page: (page - 1) * 10,
        "priority": 8,
    },
}

class SearchService:
    def __init__(self):
        self.timeout = 10.0
        self.max_retries = 2
        self.max_results_per_source = 50

    async def _fetch_with_retry(self, client: httpx.AsyncClient, url: str, source: str = None) -> Optional[str]:
        for attempt in range(self.max_retries):
            try:
                response = await client.get(url, headers=get_random_headers(source), timeout=self.timeout)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    print(f"Access forbidden (403): {url}")
                elif response.status_code == 429:
                    print(f"Rate limited (429): {url}")
            except Exception as e:
                print(f"Fetch attempt {attempt + 1} failed for {url}: {e}")
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(random.uniform(2, 5))
        
        return None

    async def _fetch_page(self, client: httpx.AsyncClient, source: str, query: str, page: int = 1) -> list[SearchResult]:
        try:
            source_info = CRAWLER_SOURCES.get(source, {})
            url_template = source_info.get("url", "")
            offset_calc = source_info.get("offset_calc", lambda p: p)
            offset = offset_calc(page)
            url = url_template.format(query=query, page=page, offset=offset)
            name = source_info.get("name", source)

            html = await self._fetch_with_retry(client, url, source)
            if html:
                return self._parse_html(source, html, name)
        except Exception as e:
            print(f"Crawler Error [{source}]: {e}")
        return []

    def _parse_html(self, source: str, html: str, name: str) -> list[SearchResult]:
        results = []
        try:
            soup = BeautifulSoup(html, "lxml")
            parsers = {
                "baidu": self._parse_baidu,
                "bing": self._parse_bing,
                "sogou": self._parse_sogou,
                "360": self._parse_360,
                "weixin": self._parse_weixin,
                "sina": self._parse_sina,
                "ifeng": self._parse_ifeng,
                "yandex": self._parse_yandex,
            }
            parser = parsers.get(source)
            if parser:
                results = parser(soup, name)
        except Exception as e:
            print(f"Parse Error [{source}]: {e}")
        return results

    def _parse_baidu(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".result, .c-container")[:self.max_results_per_source * 2]:
            if item.select_one(".c-adsence") or item.select_one("[class*='ad']"):
                continue
            title_elem = item.select_one("h3 a") or item.select_one("a")
            snippet_elem = item.select_one(".c-abstract") or item.select_one(".content-right")
            img_elem = item.select_one("img") or item.select_one(".c-img")
            img_url = None
            if img_elem:
                img_url = img_elem.get("src") or img_elem.get("data-src")
            if title_elem and title_elem.get("href"):
                url = title_elem.get("href", "")
                if "baidu.com" in url and "click" not in url.lower():
                    continue
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=url,
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name,
                    image=img_url
                ))
            if len(results) >= self.max_results_per_source:
                break
        return results

    def _parse_bing(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select("li.b_algo")[:self.max_results_per_source * 2]:
            if item.select_one(".b_ad"):
                continue
            title_elem = item.select_one("h2 a")
            snippet_elem = item.select_one("p")
            img_elem = item.select_one("img.thumb")
            img_url = img_elem.get("src") if img_elem else None
            if title_elem and title_elem.get("href"):
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=title_elem.get("href", ""),
                    snippet=snippet_elem.get_text(strip=True) if snippet_elem else "",
                    source=name,
                    image=img_url
                ))
            if len(results) >= self.max_results_per_source:
                break
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

    def _parse_360(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".result, .res-list")[:self.max_results_per_source]:
            title_elem = item.select_one("h3 a") or item.select_one(".res-title a")
            link_elem = item.select_one("a")
            snippet_elem = item.select_one(".res-desc, .description")
            if title_elem:
                url = link_elem.get("href", "") if link_elem else title_elem.get("href", "")
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=url,
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name
                ))
        return results

    def _parse_quark(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".result, .card")[:self.max_results_per_source]:
            title_elem = item.select_one("h3 a") or item.select_one(".title a")
            link_elem = item.select_one("a")
            snippet_elem = item.select_one(".desc, .summary")
            if title_elem:
                url = link_elem.get("href", "") if link_elem else title_elem.get("href", "")
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=url,
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name
                ))
        return results

    def _parse_github(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".repo-list-item, .Box-row")[:self.max_results_per_source]:
            title_elem = item.select_one("a[itemprop='name codeRepository']") or item.select_one(".prc-target a") or item.select_one("h3 a")
            link_elem = item.select_one("a[itemprop='name codeRepository']") or item.select_one(".prc-target a")
            snippet_elem = item.select_one("p") or item.select_one(".markdown-body")
            if title_elem:
                url = "https://github.com" + title_elem.get("href", "") if not title_elem.get("href", "").startswith("http") else title_elem.get("href", "")
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=url,
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name
                ))
        return results

    def _parse_zhihu(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".List-item, .ContentItem, .Card")[:self.max_results_per_source]:
            title_elem = item.select_one("h2 a") or item.select_one(".ContentItem-title a") or item.select_one(".item-title a")
            link_elem = item.select_one("h2 a") or item.select_one(".ContentItem-title a") or item.select_one("a")
            snippet_elem = item.select_one(".RichText") or item.select_one(".item-excerpt") or item.select_one(".description")
            if title_elem:
                url = link_elem.get("href", "") if link_elem else ""
                if url and not url.startswith("http"):
                    url = "https://www.zhihu.com" + url
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=url,
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name
                ))
        return results

    def _parse_weixin(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".wx-rb__item, .news-box li")[:self.max_results_per_source]:
            title_elem = item.select_one(".wx-rb__title") or item.select_one("h3 a") or item.select_one("a")
            link_elem = item.select_one("a")
            snippet_elem = item.select_one(".wx-rb__desc") or item.select_one(".info")
            if title_elem:
                url = link_elem.get("href", "") if link_elem else title_elem.get("href", "")
                if url and not url.startswith("http"):
                    url = "https://weixin.sogou.com" + url
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=url,
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name
                ))
        return results

    def _parse_sina(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".result, .item, .news-item")[:self.max_results_per_source]:
            title_elem = item.select_one("h2 a") or item.select_one(".title a") or item.select_one("a")
            link_elem = item.select_one("a")
            snippet_elem = item.select_one(".content, .desc, p")
            if title_elem:
                url = link_elem.get("href", "") if link_elem else title_elem.get("href", "")
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=url,
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name
                ))
        return results

    def _parse_ifeng(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".f-bgList02 li, .searchResult li, .item")[:self.max_results_per_source]:
            title_elem = item.select_one("h3 a") or item.select_one("a")
            link_elem = item.select_one("a")
            snippet_elem = item.select_one(".content, .desc, p")
            if title_elem:
                url = link_elem.get("href", "") if link_elem else ""
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=url,
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name
                ))
        return results

    def _parse_yandex(self, soup: BeautifulSoup, name: str) -> list[SearchResult]:
        results = []
        for item in soup.select(".serp-item, .OrganicTitle")[:self.max_results_per_source]:
            title_elem = item.select_one("h2 a") or item.select_one(".OrganicTitle-Link a") or item.select_one("a")
            link_elem = item.select_one("a")
            snippet_elem = item.select_one(".OrganicTitle-Description, .TextContainer")
            if title_elem:
                url = link_elem.get("href", "") if link_elem else ""
                results.append(SearchResult(
                    title=title_elem.get_text(strip=True),
                    url=url,
                    snippet=snippet_elem.get_text(strip=True)[:200] if snippet_elem else "",
                    source=name
                ))
        return results

    async def _fetch_github_api(self, query: str, page: int) -> list[SearchResult]:
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc&page={page}&per_page=30"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": random.choice(USER_AGENTS),
            }
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for item in data.get("items", [])[:self.max_results_per_source]:
                        results.append(SearchResult(
                            title=item.get("full_name", ""),
                            url=item.get("html_url", ""),
                            snippet=f"⭐ {item.get('stargazers_count', 0)} | {item.get('description', 'No description')[:150]}",
                            source="GitHub"
                        ))
                    return results
        except Exception as e:
            print(f"GitHub API error: {e}")
        return []

    async def search(self, query: str, page: int = 1, page_size: int = 20) -> tuple[list[SearchResult], bool]:
        cache_key = cache_service.generate_search_key(query, page)
        cached = cache_service.get(cache_key)
        if cached:
            results = [SearchResult(**r) for r in cached["results"]]
            return results[:page_size], True

        all_results = []
        sorted_sources = sorted(CRAWLER_SOURCES.items(), key=lambda x: x[1]["priority"])

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            tasks = [self._fetch_page(client, source, query, page) for source, _ in sorted_sources]
            results_list = await asyncio.gather(*tasks)
            for results in results_list:
                all_results.extend(results)

        github_results = await self._fetch_github_api(query, page)
        all_results.extend(github_results)

        seen_urls = set()
        unique_results = []
        for r in all_results:
            if r.url and r.url.startswith("http") and r.url not in seen_urls:
                seen_urls.add(r.url)
                unique_results.append(r)

        unique_results.sort(key=lambda x: (len(x.snippet or "") > 0, x.source != "GitHub"), reverse=True)

        if unique_results:
            cache_service.set(cache_key, {
                "results": [r.model_dump() for r in unique_results]
            }, config.CACHE_TTL_SEARCH)

        start = (page - 1) * page_size
        end = start + page_size
        return unique_results[start:end], False

search_service = SearchService()
