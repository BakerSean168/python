"""
请求和响应的数据模型。

Pydantic 是 Python 的数据验证库。
FastAPI 用它来：
1. 自动验证请求数据
2. 自动生成 API 文档
3. 自动序列化/反序列化 JSON
"""

from pydantic import BaseModel, Field


# ============================================================
# 请求模型
# ============================================================

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="用户消息",
        examples=["你好，介绍一下 Python"],
    )
    system_prompt: str = Field(
        default="You are a helpful assistant. Respond in the same language the user uses.",
        max_length=5000,
        description="系统指令（可选）",
    )


class ResearchRequest(BaseModel):
    """调研请求"""
    topic: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="研究主题",
        examples=["Python 异步编程入门"],
    )


class WriteRequest(BaseModel):
    """写作请求"""
    topic: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="写作主题",
        examples=["为什么应该学 Rust"],
    )


# ============================================================
# 响应模型
# ============================================================

class ChatResponse(BaseModel):
    """聊天响应"""
    reply: str = Field(description="Agent 的回复")
    model: str = Field(description="使用的模型")
    tokens_used: int | None = Field(default=None, description="消耗的 token 数")


class ResearchResponse(BaseModel):
    """调研响应"""
    topic: str = Field(description="研究主题")
    report: str = Field(description="调研报告")
    sources_count: int = Field(description="参考来源数量")


class WriteResponse(BaseModel):
    """写作响应"""
    topic: str = Field(description="写作主题")
    article: str = Field(description="最终文章")
    rounds: int = Field(description="写作轮数（初稿 + 修改）")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(description="服务状态")
    version: str = Field(description="API 版本")
    model: str = Field(description="当前使用的模型")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(description="错误信息")
    detail: str | None = Field(default=None, description="详细错误信息")
