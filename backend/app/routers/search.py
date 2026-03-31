from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from backend.app.models.schemas import SearchRequest, SearchResponse, AISummaryRequest
    from backend.app.services.search_service import search_service
    from backend.app.services.ai_summary_service import ai_summary_service
    from backend.app.services.cache_service import cache_service
except ModuleNotFoundError:
    from app.models.schemas import SearchRequest, SearchResponse, AISummaryRequest
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

    return SearchResponse(
        results=results,
        ai_summary=ai_summary,
        cached=cached
    )

@router.post("/search/ai-summary")
async def generate_ai_summary(request: AISummaryRequest):
    async def event_generator():
        summary_key = cache_service.generate_summary_key(request.query)
        cached_summary = cache_service.get(summary_key)

        if cached_summary:
            summary = cached_summary.get("summary", "")
            if summary:
                for i in range(0, len(summary), 20):
                    chunk = summary[i:i+20]
                    yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                    await asyncio.sleep(0.02)
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return

        snippets = [s for s in request.snippets if s and len(s.strip()) > 10][:10]
        if not snippets:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        full_summary = await ai_summary_service.generate_summary(
            request.query,
            snippets
        )

        if full_summary:
            cache_service.set(summary_key, {"summary": full_summary})
            for i in range(0, len(full_summary), 20):
                chunk = full_summary[i:i+20]
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                await asyncio.sleep(0.02)

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
