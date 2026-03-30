import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SHENMA_APP_KEY = os.getenv("SHENMA_APP_KEY", "")
    SHENMA_APP_SECRET = os.getenv("SHENMA_APP_SECRET", "")
    SHENMA_API_URL = "https://api.shenmadu.com/v1/search"

    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_API_URL = os.getenv("MINIMAX_API_URL", "https://api.minimax.chat/v1")

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))

    CACHE_TTL_SEARCH = 1800
    CACHE_TTL_SUMMARY = 3600

    API_PORT = int(os.getenv("API_PORT", "8000"))

config = Config()
