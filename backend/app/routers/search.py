from fastapi import APIRouter, HTTPException
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from backend.app.models.schemas import SearchRequest, SearchResponse
    from backend.app.services.search_service import search_service
    from backend.app.services.ai_summary_service import ai_summary_service
    from backend.app.services.cache_service import cache_service
except ModuleNotFoundError:
    from app.models.schemas import SearchRequest, SearchResponse
    from app.services.search_service import search_service
    from app.services.ai_summary_service import ai_summary_service
    from app.services.cache_service import cache_service

router = APIRouter(prefix="/api", tags=["search"])

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    results, cached = await search_service.search(
        query=request.query,
        page=request.page,
        page_size=request.page_size
    )

    ai_summary = None
    summary_key = cache_service.generate_summary_key(request.query)
    cached_summary = cache_service.get(summary_key)

    if cached_summary:
        ai_summary = cached_summary.get("summary")
    else:
        snippets = [r.snippet for r in results[:5]]
        if snippets:
            ai_summary = await ai_summary_service.generate_summary(
                request.query,
                snippets
            )
            if ai_summary:
                cache_service.set(summary_key, {"summary": ai_summary})

    return SearchResponse(
        results=results,
        ai_summary=ai_summary,
        cached=cached
    )
