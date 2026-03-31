import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
    MINIMAX_API_URL = os.getenv("MINIMAX_API_URL", "https://api.minimax.chat/v1")
    MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")
    MINIMAX_TOKENS = int(os.getenv("MINIMAX_TOKENS", "500"))
    MINIMAX_TEMPERATURE = float(os.getenv("MINIMAX_TEMPERATURE", "0.7"))

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))

    CACHE_TTL_SEARCH = 1800
    CACHE_TTL_SUMMARY = 3600

    API_PORT = int(os.getenv("API_PORT", "8000"))

config = Config()
