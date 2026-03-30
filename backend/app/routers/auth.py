from fastapi import APIRouter
import hashlib
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from backend.app.models.schemas import AuthRequest, AuthResponse
except ModuleNotFoundError:
    from app.models.schemas import AuthRequest, AuthResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/apikey", response_model=AuthResponse)
async def create_apikey(request: AuthRequest):
    api_key = hashlib.sha256(
        f"{request.email}{int(time.time())}".encode()
    ).hexdigest()

    return AuthResponse(
        api_key=api_key,
        rate_limit={
            "per_minute": 60,
            "per_hour": 1000
        }
    )
