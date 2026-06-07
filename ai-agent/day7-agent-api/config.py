"""
配置和认证模块。

生产环境的 Agent 服务需要：
1. API Key 认证 — 防止未授权访问
2. 日志 — 记录每次请求，方便排查问题
3. 超时控制 — 防止 LLM 调用卡住
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 配置
# ============================================================

# OpenRouter API
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-120b:free"

# API 服务的密钥（客户端调用时需要带上这个 key）
# 和 OPENROUTER_API_KEY 不同 — 这个是"你的服务"的密钥
API_SERVICE_KEY = os.environ.get("API_SERVICE_KEY", "dev-key-change-in-production")

# 超时设置（秒）
LLM_TIMEOUT = 120
REQUEST_TIMEOUT = 300

# ============================================================
# 日志配置
# ============================================================
#
# 日志是生产环境最重要的调试工具。
# 没有日志 = 出了问题只能猜。
#
# 日志级别：
#   DEBUG    → 详细信息，开发时用
#   INFO     → 正常操作记录
#   WARNING  → 警告，不影响运行但需要注意
#   ERROR    → 错误，某个操作失败了
#   CRITICAL → 严重错误，服务可能崩溃
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# 创建一个 logger 实例
logger = logging.getLogger("agent-api")
