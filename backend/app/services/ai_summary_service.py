import httpx
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
try:
    from backend.app.config import config
except ModuleNotFoundError:
    from app.config import config

class AISummaryService:
    def __init__(self):
        self.api_key = config.MINIMAX_API_KEY
        self.api_url = f"{config.MINIMAX_API_URL}/text/chatcompletion_pro"

    async def generate_summary(self, query: str, context: list[str]) -> Optional[str]:
        if not self.api_key:
            return None

        context_text = "\n\n".join([f"[{i+1}] {c}" for i, c in enumerate(context)])

        prompt = f"""基于以下搜索结果，为用户的问题生成一个简洁的答案摘要。

用户问题: {query}

搜索结果:
{context_text}

请生成一段 2-3 句话的摘要，直接回答用户问题。"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "abab5.5-chat",
            "tokens_to_generate": 200,
            "temperature": 0.7,
            "bot_setting": [
                {
                    "bot_name": "AI助手",
                    "identity": "助手",
                    "content": "你是一个友好的AI助手"
                }
            ],
            "reply_constraints": {
                "reply_language": "auto",
                "sender_type": "BOT",
                "sender_name": "AI助手"
            },
            "messages": [
                {"role": "user", "content": prompt, "sender_name": "用户", "sender_type": "USER"}
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply", "")
                    if reply:
                        return reply.strip()
        except Exception as e:
            print(f"AI Summary Error: {e}")

        return None

ai_summary_service = AISummaryService()
