import pytest
from unittest.mock import patch, AsyncMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from backend.app.services.search_service import SearchService
except ModuleNotFoundError:
    from app.services.search_service import SearchService

def test_search_service_import():
    assert SearchService is not None

def test_search_service_can_be_instantiated():
    with patch('app.services.search_service.config') as mock_config:
        mock_config.SHENMA_APP_KEY = "test_key"
        mock_config.SHENMA_APP_SECRET = "test_secret"
        mock_config.SHENMA_API_URL = "https://api.test.com"
        service = SearchService()
        assert service is not None
        assert hasattr(service, 'search')

def test_generate_signature():
    with patch('app.services.search_service.config') as mock_config:
        mock_config.SHENMA_APP_KEY = "test_key"
        mock_config.SHENMA_APP_SECRET = "test_secret"
        mock_config.SHENMA_API_URL = "https://api.test.com"
        service = SearchService()
        params = {"app_key": "test_key", "query": "test", "timestamp": 123456}
        sign = service._generate_signature(params)
        assert sign is not None
        assert len(sign) == 32
