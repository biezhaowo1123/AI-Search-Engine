# AI 搜索引擎实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个简单的 AI 文字搜索引擎 - 用户输入查询，返回搜索结果 + AI 摘要

**Architecture:** 前端 Next.js 调用后端 FastAPI API，后端调用神马搜索 API 获取结果，再调用 Minimax AI 生成摘要，Redis 做缓存

**Tech Stack:** Next.js 14, Tailwind CSS, FastAPI, Redis, 神马搜索 API, Minimax API

---

## 文件结构

```
/project01
├── frontend/                    # Next.js 前端
│   ├── app/
│   │   ├── page.tsx           # 首页搜索界面
│   │   ├── layout.tsx         # 布局
│   │   └── globals.css        # 全局样式
│   ├── components/
│   │   ├── SearchBox.tsx      # 搜索框组件
│   │   └── SearchResults.tsx  # 搜索结果组件
│   └── package.json
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── routers/
│   │   │   ├── search.py      # 搜索路由
│   │   │   └── auth.py        # 认证路由
│   │   ├── services/
│   │   │   ├── search_service.py    # 搜索服务
│   │   │   ├── cache_service.py     # 缓存服务
│   │   │   └── ai_summary_service.py # AI 摘要服务
│   │   └── models/
│   │       └── schemas.py     # Pydantic 模型
│   ├── tests/
│   │   ├── test_search.py
│   │   └── test_ai_summary.py
│   ├── requirements.txt
│   └── Dockerfile
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-03-30-ai-search-engine-design.md
│       └── plans/
│           └── 2026-03-30-ai-search-engine-plan.md
└── README.md
```

---

## Task 1: 项目初始化

**Files:**
- Create: `README.md`
- Create: `frontend/package.json`
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`

- [ ] **Step 1: 创建 README.md**

```markdown
# AI 搜索引擎

简单的 AI 文字搜索引擎，返回搜索结果 + AI 摘要。

## 技术栈

- 前端: Next.js 14 + Tailwind CSS
- 后端: FastAPI + Redis
- 搜索: 神马搜索 API
- AI: Minimax

## 开发

### 前端
cd frontend
npm install
npm run dev

### 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- [ ] **Step 2: 创建前端 package.json**

```json
{
  "name": "ai-search-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

- [ ] **Step 3: 创建后端 requirements.txt**

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
redis==5.0.1
httpx==0.26.0
pydantic==2.5.3
python-dotenv==1.0.0
```

- [ ] **Step 4: 创建 backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 5: Commit**

```bash
git add README.md frontend/package.json backend/requirements.txt backend/Dockerfile
git commit -m "feat: initial project structure"
```

---

## Task 2: 后端配置管理

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/.env.example`

- [ ] **Step 1: 创建 backend/.env.example**

```
# 神马搜索 API
SHENMA_APP_KEY=your_shenma_app_key
SHENMA_APP_SECRET=your_shenma_app_secret

# Minimax API
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_API_URL=https://api.minimax.chat/v1

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Server
API_PORT=8000
```

- [ ] **Step 2: 创建 backend/app/config.py**

```python
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
    
    CACHE_TTL_SEARCH = 1800  # 30 minutes
    CACHE_TTL_SUMMARY = 3600  # 1 hour
    
    API_PORT = int(os.getenv("API_PORT", "8000"))

config = Config()
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/config.py backend/.env.example
git commit -m "feat: add backend config management"
```

---

## Task 3: 后端 Pydantic 模型

**Files:**
- Create: `backend/app/models/schemas.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: 创建 backend/app/models/schemas.py**

```python
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
    date: Optional[str] = None

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
```

- [ ] **Step 2: 创建测试 backend/tests/test_models.py**

```python
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
```

- [ ] **Step 3: 运行测试验证**

```bash
cd backend
pytest tests/test_models.py -v
# Expected: PASS
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/schemas.py backend/tests/test_models.py
git commit -m "feat: add Pydantic models"
```

---

## Task 4: 缓存服务

**Files:**
- Create: `backend/app/services/cache_service.py`
- Create: `backend/tests/test_cache_service.py`

- [ ] **Step 1: 创建 backend/app/services/cache_service.py**

```python
import json
import redis
from typing import Optional
from backend.app.config import config

class CacheService:
    def __init__(self):
        self.client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[dict]:
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None
    
    def set(self, key: str, value: dict, ttl: int = 1800):
        self.client.setex(key, ttl, json.dumps(value))
    
    def delete(self, key: str):
        self.client.delete(key)
    
    def generate_search_key(self, query: str, page: int) -> str:
        return f"search:{query}:{page}"
    
    def generate_summary_key(self, query: str) -> str:
        return f"summary:{query}"

cache_service = CacheService()
```

- [ ] **Step 2: 创建测试 backend/tests/test_cache_service.py**

```python
import pytest
from unittest.mock import MagicMock, patch
from app.services.cache_service import CacheService

@pytest.fixture
def mock_redis():
    with patch('redis.Redis') as mock:
        yield mock.return_value

def test_cache_service_get(mock_redis):
    mock_redis.get.return_value = '{"title": "test"}'
    service = CacheService()
    result = service.get("test_key")
    assert result == {"title": "test"}

def test_cache_service_set(mock_redis):
    service = CacheService()
    service.set("test_key", {"data": "value"}, ttl=60)
    mock_redis.setex.assert_called_once()

def test_generate_search_key():
    service = CacheService()
    key = service.generate_search_key("test query", 1)
    assert key == "search:test query:1"

def test_generate_summary_key():
    service = CacheService()
    key = service.generate_summary_key("test query")
    assert key == "summary:test query"
```

- [ ] **Step 3: 运行测试**

```bash
cd backend
pytest tests/test_cache_service.py -v
# Expected: PASS
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/cache_service.py backend/tests/test_cache_service.py
git commit -m "feat: add Redis cache service"
```

---

## Task 5: AI 摘要服务

**Files:**
- Create: `backend/app/services/ai_summary_service.py`
- Create: `backend/tests/test_ai_summary_service.py`

- [ ] **Step 1: 创建 backend/app/services/ai_summary_service.py**

```python
import httpx
from typing import Optional
from backend.app.config import config

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
            "model": "abab6-chat",
            "tokens_to_generate": 200,
            "temperature": 0.7,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.api_url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("choices", [{}])[0].get("text", "").strip()
        except Exception as e:
            print(f"AI Summary Error: {e}")
        
        return None

ai_summary_service = AISummaryService()
```

- [ ] **Step 2: 创建测试 backend/tests/test_ai_summary_service.py**

```python
import pytest
from unittest.mock import patch, AsyncMock
from app.services.ai_summary_service import AISummaryService

@pytest.fixture
def service():
    with patch('app.services.ai_summary_service.config') as mock_config:
        mock_config.MINIMAX_API_KEY = "test_key"
        mock_config.MINIMAX_API_URL = "https://api.test.com"
        service = AISummaryService()
        yield service

@pytest.mark.asyncio
async def test_generate_summary_success(service):
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"text": "这是一个测试摘要"}]
        }
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        result = await service.generate_summary(
            "测试问题",
            ["搜索结果1", "搜索结果2"]
        )
        assert result == "这是一个测试摘要"

@pytest.mark.asyncio
async def test_generate_summary_no_api_key():
    with patch('app.services.ai_summary_service.config') as mock_config:
        mock_config.MINIMAX_API_KEY = ""
        service = AISummaryService()
        result = await service.generate_summary("test", [])
        assert result is None
```

- [ ] **Step 3: 运行测试**

```bash
cd backend
pytest tests/test_ai_summary_service.py -v
# Expected: PASS
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/ai_summary_service.py backend/tests/test_ai_summary_service.py
git commit -m "feat: add AI summary service with Minimax"
```

---

## Task 6: 搜索服务

**Files:**
- Create: `backend/app/services/search_service.py`
- Create: `backend/tests/test_search_service.py`

- [ ] **Step 1: 创建 backend/app/services/search_service.py**

```python
import httpx
import hashlib
import time
from typing import Optional
from backend.app.config import config
from backend.app.models.schemas import SearchResult
from backend.app.services.cache_service import cache_service

class SearchService:
    def __init__(self):
        self.api_url = config.SHENMA_API_URL
        self.app_key = config.SHENMA_APP_KEY
        self.app_secret = config.SHENMA_APP_SECRET
    
    def _generate_signature(self, params: dict) -> str:
        sorted_params = sorted(params.items())
        sign_str = "".join([f"{k}{v}" for k, v in sorted_params])
        sign_str += self.app_secret
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    async def search(self, query: str, page: int = 1, page_size: int = 20) -> tuple[list[SearchResult], bool]:
        cache_key = cache_service.generate_search_key(query, page)
        cached = cache_service.get(cache_key)
        if cached:
            results = [SearchResult(**r) for r in cached["results"]]
            return results, True
        
        params = {
            "app_key": self.app_key,
            "query": query,
            "page": page,
            "page_size": page_size,
            "timestamp": int(time.time())
        }
        params["sign"] = self._generate_signature(params)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.api_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results = self._parse_results(data)
                    cache_service.set(cache_key, {
                        "results": [r.model_dump() for r in results]
                    }, config.CACHE_TTL_SEARCH)
                    return results, False
        except Exception as e:
            print(f"Search Error: {e}")
        
        return [], False
    
    def _parse_results(self, data: dict) -> list[SearchResult]:
        results = []
        items = data.get("results", [])
        for item in items:
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
                date=item.get("date")
            ))
        return results

search_service = SearchService()
```

- [ ] **Step 2: 创建测试 backend/tests/test_search_service.py**

```python
import pytest
from unittest.mock import patch, AsyncMock
from app.services.search_service import SearchService

@pytest.fixture
def service():
    with patch('app.services.search_service.config') as mock_config:
        mock_config.SHENMA_APP_KEY = "test_key"
        mock_config.SHENMA_APP_SECRET = "test_secret"
        mock_config.SHENMA_API_URL = "https://api.test.com"
        mock_config.CACHE_TTL_SEARCH = 1800
        service = SearchService()
        yield service

@pytest.mark.asyncio
async def test_search_with_cache(service):
    with patch('app.services.search_service.cache_service') as mock_cache:
        mock_cache.generate_search_key.return_value = "test_key"
        mock_cache.get.return_value = {
            "results": [{"title": "Cached", "url": "http://test.com", "snippet": "Test"}]
        }
        results, cached = await service.search("test")
        assert len(results) == 1
        assert cached is True
        assert results[0].title == "Cached"

@pytest.mark.asyncio
async def test_search_without_cache(service):
    with patch('app.services.search_service.cache_service') as mock_cache:
        mock_cache.generate_search_key.return_value = "test_key"
        mock_cache.get.return_value = None
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "results": [
                    {"title": "Result 1", "url": "http://test1.com", "snippet": "Snippet 1"},
                    {"title": "Result 2", "url": "http://test2.com", "snippet": "Snippet 2"}
                ]
            }
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            results, cached = await service.search("test")
            assert len(results) == 2
            assert cached is False
```

- [ ] **Step 3: 运行测试**

```bash
cd backend
pytest tests/test_search_service.py -v
# Expected: PASS
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/services/search_service.py backend/tests/test_search_service.py
git commit -m "feat: add search service with Shenma API"
```

---

## Task 7: API 路由

**Files:**
- Create: `backend/app/routers/search.py`
- Create: `backend/app/routers/auth.py`
- Create: `backend/tests/test_routes.py`

- [ ] **Step 1: 创建 backend/app/routers/search.py**

```python
from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import SearchRequest, SearchResponse
from backend.app.services.search_service import search_service
from backend.app.services.ai_summary_service import ai_summary_service
from backend.app.services.cache_service import cache_service

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
```

- [ ] **Step 2: 创建 backend/app/routers/auth.py**

```python
from fastapi import APIRouter
import hashlib
import time
from backend.app.models.schemas import AuthRequest, AuthResponse

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
```

- [ ] **Step 3: 创建 backend/tests/test_routes.py**

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

def test_health_endpoint():
    with patch('app.main.config') as mock_config:
        mock_config.API_PORT = 8000
        from app.main import app
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/routers/search.py backend/app/routers/auth.py backend/tests/test_routes.py
git commit -m "feat: add API routes for search and auth"
```

---

## Task 8: FastAPI 主入口

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/__init__.py`
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/models/__init__.py`

- [ ] **Step 1: 创建 backend/app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import search, auth
from backend.app.models.schemas import HealthResponse

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
```

- [ ] **Step 2: 创建 __init__.py 文件**

```python
# backend/app/__init__.py
# backend/app/routers/__init__.py
# backend/app/services/__init__.py
# backend/app/models/__init__.py
```

- [ ] **Step 3: 运行后端测试验证**

```bash
cd backend
pytest tests/ -v --ignore=tests/test_search_service.py --ignore=tests/test_ai_summary_service.py
# Expected: All tests PASS
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/main.py backend/app/__init__.py backend/app/routers/__init__.py backend/app/services/__init__.py backend/app/models/__init__.py
git commit -m "feat: add FastAPI main entry point"
```

---

## Task 9: 前端 - 项目初始化

**Files:**
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/tsconfig.json`
- Create: `frontend/next.config.js`
- Create: `frontend/app/globals.css`
- Create: `frontend/app/layout.tsx`

- [ ] **Step 1: 创建 frontend/tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

- [ ] **Step 2: 创建 frontend/postcss.config.js**

```javascript
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 3: 创建 frontend/tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 4: 创建 frontend/next.config.js**

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
}

module.exports = nextConfig
```

- [ ] **Step 5: 创建 frontend/app/globals.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-start-rgb: 255, 255, 255;
  --background-end-rgb: 255, 255, 255;
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
}
```

- [ ] **Step 6: 创建 frontend/app/layout.tsx**

```tsx
import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AI 搜索引擎',
  description: '智能搜索 + AI 摘要',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body className="min-h-screen bg-white">{children}</body>
    </html>
  )
}
```

- [ ] **Step 7: Commit**

```bash
git add frontend/tailwind.config.js frontend/postcss.config.js frontend/tsconfig.json frontend/next.config.js frontend/app/globals.css frontend/app/layout.tsx
git commit -m "feat: setup Next.js frontend with Tailwind"
```

---

## Task 10: 前端 - 搜索组件

**Files:**
- Create: `frontend/components/SearchBox.tsx`
- Create: `frontend/components/SearchResults.tsx`
- Create: `frontend/app/page.tsx`

- [ ] **Step 1: 创建 frontend/components/SearchBox.tsx**

```tsx
'use client'

import { useState } from 'react'

interface SearchBoxProps {
  onSearch: (query: string) => void
  loading: boolean
}

export default function SearchBox({ onSearch, loading }: SearchBoxProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && !loading) {
      onSearch(query.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="输入搜索内容..."
          className="w-full px-6 py-4 text-lg border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? '搜索中...' : '搜索'}
        </button>
      </div>
    </form>
  )
}
```

- [ ] **Step 2: 创建 frontend/components/SearchResults.tsx**

```tsx
interface SearchResult {
  title: string
  url: string
  snippet: string
  date?: string
}

interface SearchResultsProps {
  results: SearchResult[]
  aiSummary?: string
  cached: boolean
}

export default function SearchResults({ results, aiSummary, cached }: SearchResultsProps) {
  if (results.length === 0) {
    return null
  }

  return (
    <div className="w-full max-w-3xl mt-8">
      {aiSummary && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-sm font-medium text-blue-800 mb-2">AI 摘要</h3>
          <p className="text-blue-900">{aiSummary}</p>
          {cached && (
            <span className="text-xs text-blue-600 mt-2 inline-block">（缓存）</span>
          )}
        </div>
      )}

      <div className="space-y-4">
        {results.map((result, index) => (
          <div key={index} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
            <a
              href={result.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-lg text-blue-600 hover:text-blue-800 hover:underline"
            >
              {result.title}
            </a>
            {result.date && (
              <span className="ml-2 text-xs text-gray-500">{result.date}</span>
            )}
            <p className="mt-1 text-gray-600 text-sm">{result.snippet}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: 创建 frontend/app/page.tsx**

```tsx
'use client'

import { useState } from 'react'
import SearchBox from '@/components/SearchBox'
import SearchResults from '@/components/SearchResults'

interface SearchResult {
  title: string
  url: string
  snippet: string
  date?: string
}

interface SearchResponse {
  results: SearchResult[]
  ai_summary?: string
  cached: boolean
}

export default function Home() {
  const [results, setResults] = useState<SearchResult[]>([])
  const [aiSummary, setAiSummary] = useState<string | undefined>()
  const [cached, setCached] = useState(false)
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (query: string) => {
    setLoading(true)
    setSearched(true)
    
    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, page: 1, page_size: 20 })
      })
      
      if (response.ok) {
        const data: SearchResponse = await response.json()
        setResults(data.results)
        setAiSummary(data.ai_summary)
        setCached(data.cached)
      }
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center pt-20 px-4">
      <h1 className="text-4xl font-bold text-gray-900 mb-2">AI 搜索引擎</h1>
      <p className="text-gray-600 mb-8">智能搜索 + AI 摘要</p>
      
      <SearchBox onSearch={handleSearch} loading={loading} />
      
      {searched && (
        <SearchResults 
          results={results} 
          aiSummary={aiSummary} 
          cached={cached} 
        />
      )}
    </main>
  )
}
```

- [ ] **Step 4: Commit**

```bash
git add frontend/components/SearchBox.tsx frontend/components/SearchResults.tsx frontend/app/page.tsx
git commit -m "feat: add search page and components"
```

---

## Task 11: 前端 API 代理

**Files:**
- Modify: `frontend/next.config.js`
- Create: `frontend/app/api/search/route.ts`

- [ ] **Step 1: 修改 next.config.js 支持 API 代理**

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
```

- [ ] **Step 2: 创建 frontend/app/api/search/route.ts**

```typescript
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const apiUrl = process.env.API_URL || 'http://localhost:8000'
    
    const response = await fetch(`${apiUrl}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    
    if (!response.ok) {
      return NextResponse.json({ error: 'Search failed' }, { status: response.status })
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/next.config.js frontend/app/api/search/route.ts
git commit -m "feat: add API proxy in Next.js"
```

---

## Task 12: 集成测试与验证

**Files:**
- Create: `backend/tests/test_integration.py`
- Create: `docker-compose.yml`

- [ ] **Step 1: 创建 docker-compose.yml**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SHENMA_APP_KEY=${SHENMA_APP_KEY}
      - SHENMA_APP_SECRET=${SHENMA_APP_SECRET}
      - MINIMAX_API_KEY=${MINIMAX_API_KEY}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - API_URL=http://backend:8000
    depends_on:
      - backend
```

- [ ] **Step 2: 创建集成测试**

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

def test_search_endpoint_integration():
    with patch('app.services.search_service.search_service.search') as mock_search:
        from app.main import app
        mock_search.return_value = ([], False)
        
        client = TestClient(app)
        response = client.post("/api/search", json={"query": "test"})
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "cached" in data
```

- [ ] **Step 3: 运行完整后端测试**

```bash
cd backend
pytest tests/ -v
# Expected: All tests PASS
```

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml backend/tests/test_integration.py
git commit -m "feat: add docker-compose and integration tests"
```

---

## 执行总结

| Task | 内容 | 预估时间 |
|------|------|----------|
| 1 | 项目初始化 | 10 min |
| 2 | 后端配置管理 | 5 min |
| 3 | Pydantic 模型 | 10 min |
| 4 | 缓存服务 | 15 min |
| 5 | AI 摘要服务 | 15 min |
| 6 | 搜索服务 | 20 min |
| 7 | API 路由 | 15 min |
| 8 | FastAPI 主入口 | 10 min |
| 9 | 前端初始化 | 15 min |
| 10 | 前端搜索组件 | 20 min |
| 11 | 前端 API 代理 | 10 min |
| 12 | 集成测试 | 15 min |

**总计约：2.5 小时**
