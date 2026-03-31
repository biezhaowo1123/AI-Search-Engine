# AI Search Engine - 智能搜索聚合引擎

一个基于 AI 的搜索聚合引擎，整合多个中文搜索源（百度、Bing、搜狗、360、微信等），并使用 AI 生成智能摘要。

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)

## 功能特性

- 🔍 **多源聚合搜索** - 同时从多个搜索引擎获取结果
  - 百度搜索
  - Bing 搜索
  - 搜狗搜索
  - 360 搜索
  - 微信搜索
  - 新浪搜索
  - GitHub 仓库搜索（API）
  - 凤凰网搜索
  - Yandex 搜索

- 🤖 **AI 智能摘要** - 基于 Minimax 大语言模型生成搜索结果摘要
  - 支持 Markdown 格式
  - 代码块语法高亮
  - 一键复制代码

- ⚡ **快速响应** - 并行搜索 + Redis 缓存
- 📱 **简洁界面** - Google 风格搜索体验
- 🔄 **分页浏览** - 支持大量结果分页查看

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Redis（可选，用于缓存）

### 安装

#### 1. 克隆项目
```bash
git clone <your-repo-url>
cd ai-search-engine
```

#### 2. 配置后端

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 配置：

```env
# Minimax API（必需）
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_API_URL=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-M2.7
MINIMAX_TOKENS=500
MINIMAX_TEMPERATURE=0.7

# Redis（可选，默认 localhost:6379）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

#### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 4. 安装前端依赖

```bash
cd frontend
npm install
```

### 启动

#### 启动后端

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 启动前端

```bash
cd frontend
npm run dev
```

#### 访问

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 项目结构

```
ai-search-engine/
├── backend/
│   ├── app/
│   │   ├── config.py          # 配置管理
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── models/
│   │   │   └── schemas.py     # 数据模型
│   │   ├── routers/
│   │   │   ├── auth.py        # 认证路由
│   │   │   └── search.py      # 搜索路由
│   │   └── services/
│   │       ├── ai_summary_service.py   # AI 摘要服务
│   │       ├── cache_service.py         # 缓存服务
│   │       └── search_service.py        # 搜索服务
│   ├── tests/                  # 测试文件
│   ├── .env.example            # 环境变量示例
│   └── requirements.txt        # Python 依赖
├── frontend/
│   ├── app/
│   │   ├── api/search/route.ts # 搜索 API 路由
│   │   ├── layout.tsx          # 布局组件
│   │   └── page.tsx           # 首页
│   ├── components/
│   │   ├── Pagination.tsx     # 分页组件
│   │   ├── SearchBox.tsx       # 搜索框组件
│   │   └── SearchResults.tsx   # 搜索结果组件
│   ├── package.json
│   └── tsconfig.json
├── .gitignore
├── README.md
└── SPEC.md                    # 技术规格文档
```

## API 接口

### 搜索

```http
POST /api/search
Content-Type: application/json

{
  "query": "搜索关键词",
  "page": 1,
  "page_size": 20
}
```

### AI 摘要

```http
POST /api/search/ai-summary
Content-Type: application/json

{
  "query": "搜索关键词",
  "snippets": ["搜索结果摘要1", "搜索结果摘要2"]
}
```

### 健康检查

```http
GET /health
```

## 配置说明

### Minimax API 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MINIMAX_API_KEY` | Minimax API 密钥 | - |
| `MINIMAX_API_URL` | API 地址 | `https://api.minimax.chat/v1` |
| `MINIMAX_MODEL` | 模型名称 | `MiniMax-M2.7` |
| `MINIMAX_TOKENS` | 最大生成 Token 数 | `500` |
| `MINIMAX_TEMPERATURE` | 温度参数 | `0.7` |

### Redis 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `REDIS_HOST` | Redis 主机 | `localhost` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `REDIS_DB` | 数据库编号 | `0` |

## 技术栈

### 后端
- **FastAPI** - 现代高性能 Web 框架
- **httpx** - 异步 HTTP 客户端
- **BeautifulSoup** - HTML 解析
- **Redis** - 缓存层
- **Minimax API** - AI 摘要生成

### 前端
- **Next.js 16** - React 框架
- **Tailwind CSS** - 样式框架
- **react-markdown** - Markdown 渲染
- **react-syntax-highlighter** - 代码高亮

## 开发

### 运行测试

```bash
cd backend
pytest tests/
```

### 构建前端生产版本

```bash
cd frontend
npm run build
```

## License

MIT License
