from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from backend.app.routers import search, auth
    from backend.app.models.schemas import HealthResponse
except ModuleNotFoundError:
    from app.routers import search, auth
    from app.models.schemas import HealthResponse

app = FastAPI(title="AI Search Engine API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(auth.router)

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")

@app.get("/")
async def root():
    return {"message": "AI Search Engine API", "version": "0.1.0"}
