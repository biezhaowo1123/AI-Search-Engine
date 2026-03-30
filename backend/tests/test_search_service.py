import pytest
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from backend.app.services.search_service import SearchService, CRAWLER_SOURCES
except ModuleNotFoundError:
    from app.services.search_service import SearchService, CRAWLER_SOURCES

def test_search_service_import():
    assert SearchService is not None

def test_search_service_can_be_instantiated():
    service = SearchService()
    assert service is not None
    assert hasattr(service, 'search')
    assert hasattr(service, '_fetch_page')

def test_crawler_sources_defined():
    assert "zhihu" in CRAWLER_SOURCES
    assert "weibo" in CRAWLER_SOURCES
    assert "baidu_news" in CRAWLER_SOURCES
    assert CRAWLER_SOURCES["zhihu"]["name"] == "知乎"
