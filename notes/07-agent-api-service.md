> [!info] related notes
> - 前置笔记: [[06-multi-agent-writing-team|多 Agent 写作团队]]
> - 所属 MOC: [[learn-ai-agent-moc|学习 AI Agent MOC]]
> - 相关概念: [[fastapi|FastAPI]]、[[rest-api|REST API]]、[[pydantic|Pydantic]]
> - 相关资源: [[open-router|OpenRouter]]

# Agent API 服务 — 部署你的 Agent

## 目标

把前 6 天学的所有能力包装成 HTTP API 服务，让别人可以通过网络调用你的 Agent。

## 和前两天的区别

| | Day 6（Multi-Agent） | Day 7（API Service） |
|---|---|---|
| 运行方式 | CLI 命令行交互 | HTTP API 服务 |
| 用户 | 只有你自己 | 任何人都可以调用 |
| 核心能力 | 多 Agent 协作 | 路由、认证、日志、错误处理 |
| 关注点 | Agent 逻辑 | 服务化、安全性、可观测性 |

## 前置条件

```bash
uv add fastapi "uvicorn[standard]" pydantic requests python-dotenv

# 启动服务
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 测试
uv run python test_api.py
```

项目结构：

```
day7-agent-api/
├── main.py        # FastAPI 应用，路由定义
├── agents.py      # Agent 逻辑（复用 Day 1-6 的能力）
├── models.py      # Pydantic 请求/响应模型
├── config.py      # 配置、认证、日志
├── test_api.py    # API 测试脚本
└── .env
```

## 核心理解：API 服务化

### 什么是 API 服务？

**把你的代码变成一个"服务器"，别人通过 HTTP 请求调用它。**

```
CLI 方式（Day 1-6）:    你在终端输入 → 程序运行 → 输出结果
API 方式（Day 7）:      别人发 HTTP 请求 → 你的服务处理 → 返回 JSON
```

### REST API 的基本概念

| 概念 | 说明 | 示例 |
|------|------|------|
| 路由 (Route) | 不同的 URL 对应不同的功能 | `/chat`、`/research`、`/write` |
| HTTP 方法 | GET（读取）、POST（创建/执行） | `GET /health`、`POST /chat` |
| 请求 | 客户端发送的数据 | `{"message": "你好"}` |
| 响应 | 服务端返回的数据 | `{"reply": "你好！有什么可以帮你？"}` |
| 状态码 | 请求的结果 | 200（成功）、401（未认证）、500（服务器错误） |

### 两层 API Key 的区别

```
用户 → X-API-Key → 你的服务 → OPENROUTER_API_KEY → OpenRouter → LLM
```

| Key | 谁用 | 保护什么 |
|-----|------|---------|
| `X-API-Key` | 你的用户 | 你的服务 |
| `OPENROUTER_API_KEY` | 你的服务 | OpenRouter 的 API |

没有 `X-API-Key` 的话，任何人都能调用你的服务，你的 OpenRouter 额度瞬间用完。

## 完整代码

### config.py — 配置和认证

> [!note]- 展开查看 config.py
> ```python
> """
> 配置和认证模块。
> 生产环境需要：API Key 认证 + 日志 + 超时控制。
> """
>
> import os
> import logging
> from dotenv import load_dotenv
>
> load_dotenv()
>
> # OpenRouter API
> OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
> OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
> MODEL = "openai/gpt-oss-120b:free"
>
> # API 服务的密钥（客户端调用时需要带上这个 key）
> API_SERVICE_KEY = os.environ.get("API_SERVICE_KEY", "dev-key-change-in-production")
>
> # 超时设置（秒）
> LLM_TIMEOUT = 120
> REQUEST_TIMEOUT = 300
>
> # 日志配置
> # 级别：DEBUG < INFO < WARNING < ERROR < CRITICAL
> logging.basicConfig(
>     level=logging.INFO,
>     format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
>     datefmt="%Y-%m-%d %H:%M:%S",
> )
> logger = logging.getLogger("agent-api")
> ```

### models.py — Pydantic 数据模型

> [!note]- 展开查看 models.py
> ```python
> """
> 请求和响应的数据模型。
> Pydantic 自动验证数据、生成 API 文档、序列化 JSON。
> """
>
> from pydantic import BaseModel, Field
>
>
> # 请求模型
>
> class ChatRequest(BaseModel):
>     """聊天请求"""
>     message: str = Field(..., min_length=1, max_length=10000, description="用户消息",
>                          examples=["你好，介绍一下 Python"])
>     system_prompt: str = Field(
>         default="You are a helpful assistant. Respond in the same language the user uses.",
>         max_length=5000, description="系统指令（可选）")
>
> class ResearchRequest(BaseModel):
>     """调研请求"""
>     topic: str = Field(..., min_length=2, max_length=500, description="研究主题",
>                        examples=["Python 异步编程入门"])
>
> class WriteRequest(BaseModel):
>     """写作请求"""
>     topic: str = Field(..., min_length=2, max_length=500, description="写作主题",
>                        examples=["为什么应该学 Rust"])
>
>
> # 响应模型
>
> class ChatResponse(BaseModel):
>     reply: str = Field(description="Agent 的回复")
>     model: str = Field(description="使用的模型")
>     tokens_used: int | None = Field(default=None, description="消耗的 token 数")
>
> class ResearchResponse(BaseModel):
>     topic: str = Field(description="研究主题")
>     report: str = Field(description="调研报告")
>     sources_count: int = Field(description="参考来源数量")
>
> class WriteResponse(BaseModel):
>     topic: str = Field(description="写作主题")
>     article: str = Field(description="最终文章")
>     rounds: int = Field(description="写作轮数")
>
> class HealthResponse(BaseModel):
>     status: str = Field(description="服务状态")
>     version: str = Field(description="API 版本")
>     model: str = Field(description="当前使用的模型")
>
> class ErrorResponse(BaseModel):
>     error: str = Field(description="错误信息")
>     detail: str | None = Field(default=None, description="详细错误信息")
> ```

### agents.py — Agent 逻辑

> [!note]- 展开查看 agents.py
> ```python
> """
> Agent 逻辑模块。
> 复用 Day 1-6 学到的所有能力：LLM 调用、多步骤 Pipeline、多 Agent 协作。
> """
>
> import requests
> from config import OPENROUTER_API_KEY, OPENROUTER_API_URL, MODEL, LLM_TIMEOUT, logger
>
>
> def call_llm(prompt: str, system: str = "You are a helpful assistant.", max_tokens: int = 3000) -> str:
>     """所有 Agent 都通过这个函数和 LLM 交互。"""
>     if not OPENROUTER_API_KEY:
>         return "Error: OPENROUTER_API_KEY not configured"
>     headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
>     payload = {
>         "model": MODEL,
>         "messages": [
>             {"role": "system", "content": system},
>             {"role": "user", "content": prompt},
>         ],
>         "max_tokens": max_tokens, "stream": False,
>     }
>     try:
>         r = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=(10, LLM_TIMEOUT))
>         if r.status_code != 200:
>             logger.error(f"LLM API error: HTTP {r.status_code}")
>             return f"API error: HTTP {r.status_code}"
>         return r.json()["choices"][0]["message"]["content"]
>     except requests.RequestException as e:
>         logger.error(f"LLM request failed: {e}")
>         return f"Network error: {e}"
>
>
> def chat_agent(message: str, system_prompt: str) -> str:
>     """聊天 Agent — Day 1 的能力"""
>     logger.info(f"Chat request: {message[:50]}...")
>     response = call_llm(message, system=system_prompt)
>     logger.info(f"Chat response: {len(response)} chars")
>     return response
>
>
> def research_agent(topic: str) -> str:
>     """调研 Agent — Day 4 的能力（简化版）"""
>     logger.info(f"Research request: {topic}")
>     research_prompt = f"请对以下主题进行调研：{topic}\n列出 5-8 个关键知识点，用 Markdown 格式。"
>     research = call_llm(research_prompt, system="You are a technical researcher.")
>     report_prompt = f"根据以下资料写一份调研报告：\n{research}\n格式：标题 → 核心发现 → 详细内容 → 总结"
>     report = call_llm(report_prompt, system="You are a research report writer.")
>     logger.info(f"Research completed: {len(report)} chars")
>     return report
>
>
> def write_agent(topic: str) -> str:
>     """写作 Agent — Day 6 的能力（简化版：写 + 审查 + 改）"""
>     logger.info(f"Write request: {topic}")
>     draft = call_llm(f"写一篇关于'{topic}'的技术博客，1500-2500 字，Markdown 格式。",
>                      system="You are a technical blog writer.", max_tokens=4000)
>     feedback = call_llm(f"审查以下文章，给 3-5 个改进建议：\n{draft[:3000]}",
>                         system="You are a technical editor.")
>     final = call_llm(f"根据建议修改文章：\n原文：{draft}\n建议：{feedback}",
>                      system="You are a technical blog writer.", max_tokens=4000)
>     logger.info(f"Write completed: {len(final)} chars")
>     return final
> ```

### main.py — FastAPI 应用

> [!note]- 展开查看 main.py
> ```python
> """
> Day 7: Agent API 服务
> 把前 6 天学的所有能力包装成 HTTP API。
> 运行: uv run uvicorn main:app --reload --port 8000
> 文档: http://localhost:8000/docs
> """
>
> import time
> from fastapi import FastAPI, Header, HTTPException, Request
> from fastapi.responses import JSONResponse
> from fastapi.middleware.cors import CORSMiddleware
>
> from config import API_SERVICE_KEY, logger, MODEL
> from models import (ChatRequest, ChatResponse, ResearchRequest, ResearchResponse,
>                     WriteRequest, WriteResponse, HealthResponse, ErrorResponse)
> from agents import chat_agent, research_agent, write_agent
>
>
> app = FastAPI(title="Agent API", description="AI Agent 服务", version="1.0.0")
>
> # CORS — 允许前端页面调用
> app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
>
>
> # 中间件：请求日志
> @app.middleware("http")
> async def log_requests(request: Request, call_next):
>     """记录每个请求的方法、路径、状态码和耗时。"""
>     start_time = time.time()
>     response = await call_next(request)
>     duration = time.time() - start_time
>     logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration:.2f}s)")
>     return response
>
>
> # 认证
> def verify_api_key(x_api_key: str | None = Header(None)) -> str:
>     if not x_api_key:
>         raise HTTPException(status_code=401, detail="Missing X-API-Key header")
>     if x_api_key != API_SERVICE_KEY:
>         logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
>         raise HTTPException(status_code=403, detail="Invalid API key")
>     return x_api_key
>
>
> # 路由
>
> @app.get("/health", response_model=HealthResponse)
> async def health_check():
>     """健康检查 — 负载均衡器和监控系统用"""
>     return HealthResponse(status="healthy", version="1.0.0", model=MODEL)
>
> @app.post("/chat", response_model=ChatResponse)
> async def chat(request: ChatRequest, api_key: str = Header(..., alias="X-API-Key")):
>     """聊天 Agent"""
>     verify_api_key(api_key)
>     try:
>         reply = chat_agent(request.message, request.system_prompt)
>         return ChatResponse(reply=reply, model=MODEL)
>     except Exception as e:
>         logger.error(f"Chat error: {e}", exc_info=True)
>         raise HTTPException(status_code=500, detail=str(e))
>
> @app.post("/research", response_model=ResearchResponse)
> async def research(request: ResearchRequest, api_key: str = Header(..., alias="X-API-Key")):
>     """调研 Agent"""
>     verify_api_key(api_key)
>     try:
>         report = research_agent(request.topic)
>         return ResearchResponse(topic=request.topic, report=report, sources_count=0)
>     except Exception as e:
>         logger.error(f"Research error: {e}", exc_info=True)
>         raise HTTPException(status_code=500, detail=str(e))
>
> @app.post("/write", response_model=WriteResponse)
> async def write(request: WriteRequest, api_key: str = Header(..., alias="X-API-Key")):
>     """写作 Agent"""
>     verify_api_key(api_key)
>     try:
>         article = write_agent(request.topic)
>         return WriteResponse(topic=request.topic, article=article, rounds=2)
>     except Exception as e:
>         logger.error(f"Write error: {e}", exc_info=True)
>         raise HTTPException(status_code=500, detail=str(e))
>
>
> # 全局异常处理
> @app.exception_handler(Exception)
> async def global_exception_handler(request: Request, exc: Exception):
>     logger.error(f"Unhandled exception: {exc}", exc_info=True)
>     return JSONResponse(status_code=500,
>                         content=ErrorResponse(error="Internal server error").model_dump())
>
>
> # 启动信息
> @app.on_event("startup")
> async def startup():
>     logger.info("=" * 60)
>     logger.info("Agent API 服务启动")
>     logger.info(f"模型: {MODEL}")
>     logger.info("API 文档: http://localhost:8000/docs")
>     logger.info("=" * 60)
> ```

## 运行效果

### 启动服务

```
$ uv run uvicorn main:app --reload --port 8000

2026-06-06 20:30:15 | INFO    | agent-api | ============================================================
2026-06-06 20:30:15 | INFO    | agent-api | Agent API 服务启动
2026-06-06 20:30:15 | INFO    | agent-api | 模型: openai/gpt-oss-120b:free
2026-06-06 20:30:15 | INFO    | agent-api | API 文档: http://localhost:8000/docs
```

### 测试 API

```
$ uv run python test_api.py

测试: GET /health
状态码: 200
响应: {'status': 'healthy', 'version': '1.0.0', 'model': 'openai/gpt-oss-120b:free'}

测试: 认证失败（无 API Key）
状态码: 422
响应: {'detail': [{'type': 'missing', 'loc': ['header', 'X-API-Key'], ...}]}

测试: 认证失败（错误的 API Key）
状态码: 403
响应: {'detail': 'Invalid API key'}

测试: POST /chat
状态码: 200
回复: Python 是一种简洁且强大的高级编程语言...
```

### 日志输出

```
2026-06-06 20:30:20 | INFO    | agent-api | GET /health → 200 (0.00s)
2026-06-06 20:30:21 | WARNING | agent-api | Invalid API key attempt: wrong-key-...
2026-06-06 20:30:22 | INFO    | agent-api | Chat request: 用一句话介绍 Python...
2026-06-06 20:30:24 | INFO    | agent-api | Chat response: 89 chars
2026-06-06 20:30:24 | INFO    | agent-api | POST /chat → 200 (2.35s)
```

## 踩坑记录

### 自动生成的 API 文档

访问 `http://localhost:8000/docs` 可以看到 FastAPI 自动生成的交互式文档。这是 Pydantic 模型的附加值 — 你定义了数据结构，文档自动生成。

### `X-API-Key` vs `OPENROUTER_API_KEY`

这是两个完全不同的 Key：

```
X-API-Key:           你给用户的 key，控制谁能用你的服务
OPENROUTER_API_KEY:  你付钱给 OpenRouter 的 key，控制你的服务能调用哪个 LLM
```

类比：
- `X-API-Key` = 你家的门钥匙（你发给别人）
- `OPENROUTER_API_KEY` = 你的信用卡（你自己用）

### CORS 中间件

```python
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```

没有 CORS，浏览器的前端页面无法调用你的 API。`allow_origins=["*"]` 允许所有域名，生产环境应该限制为你的域名。

## 关键流程解析

### API 服务的 5 个核心组件

```
1. 路由 (Routes)     — 不同 URL 对应不同功能
2. 数据模型 (Models)  — Pydantic 验证请求/响应
3. 认证 (Auth)       — API Key 保护服务
4. 日志 (Logging)    — 记录每次请求
5. 错误处理 (Errors)  — 优雅地处理异常
```

### 请求的完整生命周期

```
客户端发请求
  ↓
中间件：记录开始时间
  ↓
路由匹配：找到对应的处理函数
  ↓
认证：验证 X-API-Key
  ↓
Pydantic：验证请求数据
  ↓
Agent 逻辑：调用 LLM
  ↓
Pydantic：格式化响应数据
  ↓
中间件：记录耗时、状态码
  ↓
返回 JSON 给客户端
```

### 错误处理的层次

```
1. Pydantic 验证失败 → 422 Unprocessable Entity
2. 认证失败 → 401 / 403
3. Agent 逻辑异常 → 500 Internal Server Error（被 try/except 捕获）
4. 全局异常 → 500（被 exception_handler 捕获）
```

## 常见问题

1. **端口被占用**：换一个端口 `--port 8001`
2. **CORS 错误**：确保 CORS 中间件已添加
3. **422 错误**：请求数据格式不对，检查 Pydantic 模型的 `Field` 定义
4. **日志不输出**：检查 `logging.basicConfig` 的 `level` 设置

## 7 天计划总结

| Day | 项目 | 核心能力 |
|-----|------|---------|
| 1 | CLI Chatbot | LLM 调用、流式输出、对话历史 |
| 2 | Tool Agent | 工具调用、JSON Schema、执行循环 |
| 3 | RAG Agent | 切块、Embedding、向量搜索、上下文注入 |
| 4 | Research Agent | 多步骤 Pipeline、网页搜索、信息提取 |
| 5 | Bugfix Agent | 执行-观察-修正循环、自我反思 |
| 6 | Multi-Agent | 角色分离、中间结果传递、质量检查 |
| 7 | API Service | 路由、认证、日志、错误处理、部署 |
