"""
Pydantic AI Tool Agent — 对比 Day 2 手写版和 LangChain 版

Pydantic AI 的设计哲学：
  - 类型安全优先 — 用 Pydantic 模型定义一切
  - 依赖注入 — Agent 的依赖（API key、配置）通过 DI 传入
  - 结构化输出 — 可以强制 LLM 返回特定格式
  - 简洁 — 没有 Chain、Graph 等复杂抽象

Setup:
  uv add pydantic-ai python-dotenv
  uv run python main.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Step 1: 创建 Agent
# ============================================================

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

# 创建模型 — 指向 OpenRouter
# OpenAIModel 已改名为 OpenAIChatModel
model = OpenAIChatModel(
    "openai/gpt-oss-120b:free",
    provider=OpenAIProvider(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
    ),
)

# 创建 Agent
# deps_type=None 表示这个 Agent 不需要依赖注入
# 这样 @agent.tool_plain 就不需要 RunContext 参数
agent = Agent(
    model,
    deps_type=None,
    system_prompt=(
        "You are a helpful assistant with access to tools. "
        "Use tools when the user's question needs real-time data or calculations. "
        "Answer in the same language the user uses."
    ),
)


# ============================================================
# Step 2: 定义工具
# ============================================================
#
# Pydantic AI 有两种工具装饰器：
#   @agent.tool        — 需要 RunContext 参数（用于访问依赖）
#   @agent.tool_plain  — 纯函数，不需要上下文（适合我们的场景）
#
# 我们的工具不需要访问 Agent 的依赖，所以用 tool_plain
# ============================================================


@agent.tool_plain
def get_weather(city: str) -> str:
    """获取指定城市的当前天气信息。

    Args:
        city: 城市名称
    """
    mock_data = {
        "东京": "25°C，晴天，湿度 60%",
        "北京": "18°C，多云",
        "上海": "22°C，小雨",
    }
    city_lower = city.lower().strip()
    if city_lower in mock_data:
        return f"{city}的天气：{mock_data[city_lower]}"
    return f"{city}的天气数据暂不可用"


@agent.tool_plain
def calculate(expression: str) -> str:
    """计算数学表达式。

    Args:
        expression: 数学表达式
    """
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return f"错误：不允许的字符"
    try:
        return f"{expression} = {eval(expression)}"
    except Exception as e:
        return f"计算错误：{e}"


@agent.tool_plain
def search_notes(keyword: str) -> str:
    """搜索本地笔记库。

    Args:
        keyword: 搜索关键词
    """
    notes = [
        {"title": "Python 装饰器", "content": "装饰器是一个接收函数并返回函数的函数..."},
        {"title": "Git 常用命令", "content": "git add . && git commit -m 'msg'"},
        {"title": "Docker 入门", "content": "docker build -t myapp ."},
    ]
    results = [f"  [{n['title']}] {n['content']}" for n in notes
               if keyword.lower() in n["title"].lower() or keyword.lower() in n["content"].lower()]
    if results:
        return f"找到 {len(results)} 条笔记：\n" + "\n".join(results)
    return f"没有找到包含 '{keyword}' 的笔记"


# ============================================================
# Step 3: 对话循环
# ============================================================

def main():
    print("=" * 60)
    print("Pydantic AI Tool Agent")
    print(f"模型: openai/gpt-oss-120b:free (via OpenRouter)")
    print("=" * 60)
    print()
    print("对比三种实现：")
    print("  手写版 (Day 2): ~100 行 — 自己处理 JSON schema、tool_calls、循环")
    print("  LangChain:      ~40 行 — @tool + create_react_agent")
    print("  Pydantic AI:    ~40 行 — @tool_plain + Agent 类")
    print()
    print("输入 'quit' 退出")
    print("-" * 60)

    # 对话历史
    message_history = []

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        try:
            result = agent.run_sync(
                user_input,
                message_history=message_history,
            )

            print(f"\nAgent: {result.output}")

            # 更新对话历史
            message_history = result.all_messages()

        except Exception as e:
            print(f"\n错误: {e}")


if __name__ == "__main__":
    main()
