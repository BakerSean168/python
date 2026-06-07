"""
Day 7: Agent API 服务

把前 6 天学的所有能力包装成 HTTP API。

核心概念：
1. 路由 (Routes) — 不同的 URL 对应不同的功能
2. 请求/响应模型 — 用 Pydantic 验证数据
3. 认证 — API Key 保护你的服务
4. 日志 — 记录每次请求
5. 错误处理 — 优雅地处理异常

运行:
  uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

测试:
  curl http://localhost:8000/health
  curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -H "X-API-Key: dev-key-change-in-production" -d '{"message": "你好"}'
"""

import time
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import API_SERVICE_KEY, logger
from models import (
    ChatRequest, ChatResponse,
    ResearchRequest, ResearchResponse,
    WriteRequest, WriteResponse,
    HealthResponse, ErrorResponse,
)
from agents import chat_agent, research_agent, write_agent
from config import MODEL

# ============================================================
# 创建 FastAPI 应用
# ============================================================

app = FastAPI(
    title="Agent API",
    description="AI Agent 服务 — 提供聊天、调研、写作能力",
    version="1.0.0",
)

# CORS 中间件 — 允许前端页面调用这个 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制为你的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 中间件：请求日志
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    记录每个请求的方法、路径、状态码和耗时。

    这是生产环境必备的 — 没有日志就无法排查问题。
    """
    start_time = time.time()

    # 处理请求
    response = await call_next(request)

    # 计算耗时
    duration = time.time() - start_time

    # 记录日志
    logger.info(
        f"{request.method} {request.url.path} "
        f"→ {response.status_code} "
        f"({duration:.2f}s)"
    )

    return response


# ============================================================
# 认证函数
# ============================================================

def verify_api_key(x_api_key: str | None = Header(None)) -> str:
    """
    验证 API Key。

    客户端需要在请求头中带上 X-API-Key。
    这是最简单的认证方式，生产环境建议用 OAuth2 或 JWT。
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-Key header",
        )
    if x_api_key != API_SERVICE_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
        )
    return x_api_key


# ============================================================
# 路由：健康检查
# ============================================================

@app.get("/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """
    健康检查端点。

    用途：
    - 负载均衡器检查服务是否存活
    - 监控系统定期探测
    - 部署后验证服务启动成功
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model=MODEL,
    )


# ============================================================
# 路由：聊天
# ============================================================

@app.post("/chat", response_model=ChatResponse, tags=["Agent"])
async def chat(request: ChatRequest, api_key: str = Header(..., alias="X-API-Key")):
    """
    聊天 Agent — 基础的 LLM 对话能力。

    这是 Day 1 的能力：发送消息，返回回复。
    """
    verify_api_key(api_key)

    try:
        reply = chat_agent(request.message, request.system_prompt)
        return ChatResponse(
            reply=reply,
            model=MODEL,
        )
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 路由：调研
# ============================================================

@app.post("/research", response_model=ResearchResponse, tags=["Agent"])
async def research(request: ResearchRequest, api_key: str = Header(..., alias="X-API-Key")):
    """
    调研 Agent — 多步骤调研流程。

    这是 Day 4 的能力：主题 → 生成关键词 → 搜索 → 提取 → 报告。
    """
    verify_api_key(api_key)

    try:
        report = research_agent(request.topic)
        return ResearchResponse(
            topic=request.topic,
            report=report,
            sources_count=0,  # 简化版没有实际搜索
        )
    except Exception as e:
        logger.error(f"Research error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 路由：写作
# ============================================================

@app.post("/write", response_model=WriteResponse, tags=["Agent"])
async def write(request: WriteRequest, api_key: str = Header(..., alias="X-API-Key")):
    """
    写作 Agent — 多 Agent 协作写作。

    这是 Day 6 的能力：Researcher → Writer → Reviewer → Writer。
    """
    verify_api_key(api_key)

    try:
        article = write_agent(request.topic)
        return WriteResponse(
            topic=request.topic,
            article=article,
            rounds=2,  # 初稿 + 修改
        )
    except Exception as e:
        logger.error(f"Write error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 全局异常处理
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理 — 捕获所有未处理的异常。

    作用：
    1. 返回统一的错误格式
    2. 记录错误日志
    3. 防止泄露内部信息
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if app.debug else None,
        ).model_dump(),
    )


# ============================================================
# 启动信息
# ============================================================

@app.on_event("startup")
async def startup():
    """服务启动时执行"""
    logger.info("=" * 60)
    logger.info("Agent API 服务启动")
    logger.info(f"模型: {MODEL}")
    logger.info(f"API Key 验证: {'已启用' if API_SERVICE_KEY != 'dev-key-change-in-production' else '开发模式'}")
    logger.info("=" * 60)
    logger.info("可用端点:")
    logger.info("  GET  /health   — 健康检查")
    logger.info("  POST /chat     — 聊天")
    logger.info("  POST /research — 调研")
    logger.info("  POST /write    — 写作")
    logger.info("=" * 60)
    logger.info("API 文档: http://localhost:8000/docs")
