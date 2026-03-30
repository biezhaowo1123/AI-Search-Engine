import pytest
from unittest.mock import MagicMock, patch
from app.services.cache_service import CacheService

@pytest.fixture
def mock_redis():
    with patch('redis.Redis') as mock:
        yield mock.return_value

def test_cache_service_get(mock_redis):
    mock_redis.get.return_value = '{"title": "test"}'
    service = CacheService()
    result = service.get("test_key")
    assert result == {"title": "test"}

def test_cache_service_set(mock_redis):
    service = CacheService()
    service.set("test_key", {"data": "value"}, ttl=60)
    mock_redis.setex.assert_called_once()

def test_generate_search_key():
    service = CacheService()
    key = service.generate_search_key("test query", 1)
    assert key == "search:test query:1"

def test_generate_summary_key():
    service = CacheService()
    key = service.generate_summary_key("test query")
    assert key == "summary:test query"
