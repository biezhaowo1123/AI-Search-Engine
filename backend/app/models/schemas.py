from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    query: str
    page: int = 1
    page_size: int = 20

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: Optional[str] = None
    date: Optional[str] = None
    image: Optional[str] = None

class SearchResponse(BaseModel):
    results: list[SearchResult]
    ai_summary: Optional[str] = None
    cached: bool = False

class AuthRequest(BaseModel):
    email: str

class AuthResponse(BaseModel):
    api_key: str
    rate_limit: dict

class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"
