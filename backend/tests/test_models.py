import pytest
from app.models.schemas import SearchRequest, SearchResponse, SearchResult

def test_search_request_model():
    req = SearchRequest(query="test query")
    assert req.query == "test query"
    assert req.page == 1
    assert req.page_size == 20

def test_search_result_model():
    result = SearchResult(
        title="Test Title",
        url="https://example.com",
        snippet="Test snippet"
    )
    assert result.title == "Test Title"
    assert result.url == "https://example.com"

def test_search_response_model():
    result = SearchResult(
        title="Test",
        url="https://example.com",
        snippet="Snippet"
    )
    response = SearchResponse(
        results=[result],
        ai_summary="AI summary",
        cached=False
    )
    assert len(response.results) == 1
    assert response.ai_summary == "AI summary"
    assert response.cached is False
