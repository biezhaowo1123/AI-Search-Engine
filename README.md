# AI 搜索引擎

简单的 AI 文字搜索引擎，返回搜索结果 + AI 摘要。

## 技术栈

- 前端: Next.js 14 + Tailwind CSS
- 后端: FastAPI + Redis
- 搜索: 神马搜索 API
- AI: Minimax

## 开发

### 前端
```bash
cd frontend
npm install
npm run dev
```

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 环境变量

复制 `backend/.env.example` 到 `backend/.env` 并填写配置。
