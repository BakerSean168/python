"""
LangChain Tool Agent — 对比 Day 2 手写版

Day 2 手写版做了什么：
  1. 自己定义 TOOLS JSON schema（30 行）
  2. 自己解析 tool_calls 响应（20 行）
  3. 自己执行工具函数（15 行）
  4. 自己把结果发回 API（10 行）
  5. 自己写 while 循环（30 行）
  总计：~100 行核心逻辑

LangChain 版做了什么：
  1. 用 @tool 装饰器定义工具（3 个函数）
  2. 用 ChatOpenAI 连接 LLM
  3. 用 create_react_agent 创建 Agent
  4. 调用 agent.invoke()
  总计：~40 行核心逻辑

框架的价值：把重复的"胶水代码"封装掉，让你专注业务逻辑。

Setup:
  uv add langchain-core langchain-openai langgraph python-dotenv
  uv run python main.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Step 1: 定义工具
# ============================================================
#
# LangChain 的 @tool 装饰器：
# - 自动从函数签名和 docstring 生成 JSON schema
# - 不用手写 parameters 定义
# - 函数名就是工具名，docstring 就是工具描述
#
# 对比 Day 2 手写版：
#   手写版需要 30 行 JSON schema 定义
#   LangChain 只需要 3 个函数 + @tool 装饰器
# ============================================================

from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """获取指定城市的当前天气信息。当用户询问天气时使用。

    Args:
        city: 城市名称，例如 '东京'、'北京'
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


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。支持加减乘除和括号。

    Args:
        expression: 数学表达式，例如 '2 + 3 * 4'
    """
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return f"错误：表达式 '{expression}' 包含不允许的字符"
    try:
        return f"{expression} = {eval(expression)}"
    except Exception as e:
        return f"计算错误：{e}"


@tool
def search_notes(keyword: str) -> str:
    """搜索本地笔记库。当用户想找笔记、回忆某个知识点时使用。

    Args:
        keyword: 搜索关键词，例如 '装饰器'、'docker'
    """
    notes = [
        {"title": "Python 装饰器", "content": "装饰器是一个接收函数并返回函数的函数..."},
        {"title": "Git 常用命令", "content": "git add . && git commit -m 'msg' && git push"},
        {"title": "Docker 入门", "content": "docker build -t myapp . && docker run -p 8080:80 myapp"},
    ]
    results = [f"  [{n['title']}] {n['content']}" for n in notes
               if keyword.lower() in n["title"].lower() or keyword.lower() in n["content"].lower()]
    if results:
        return f"找到 {len(results)} 条笔记：\n" + "\n".join(results)
    return f"没有找到包含 '{keyword}' 的笔记"


# 工具列表
tools = [get_weather, calculate, search_notes]


# ============================================================
# Step 2: 创建 LLM
# ============================================================
#
# ChatOpenAI 默认连接 OpenAI API。
# 通过 base_url 参数可以指向任何 OpenAI 兼容的 API（包括 OpenRouter）。
#
# 这就是"OpenAI 兼容格式"的价值：
#   - OpenRouter、Groq、Together、本地 Ollama 都兼容
#   - 换 provider 只需改 base_url 和 api_key
# ============================================================

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    model="openai/gpt-oss-120b:free",
    temperature=0,
)


# ============================================================
# Step 3: 创建 Agent
# ============================================================
#
# create_react_agent 是 LangGraph 提供的预构建 Agent。
# 它实现了 ReAct 模式：
#   Reason（推理）→ Act（行动）→ Observe（观察）→ 循环
#
# 对比 Day 2 手写版：
#   手写版的 agent_loop() 函数就是 ReAct 的手动实现
#   LangGraph 把它封装成了一个函数调用
# ============================================================

from langgraph.prebuilt import create_react_agent

agent = create_react_agent(llm, tools)


# ============================================================
# Step 4: 对话循环
# ============================================================

def main():
    print("=" * 60)
    print("LangChain Tool Agent")
    print(f"模型: openai/gpt-oss-120b:free (via OpenRouter)")
    print(f"工具: {', '.join(t.name for t in tools)}")
    print("=" * 60)
    print()
    print("对比 Day 2 手写版：")
    print("  手写版: ~100 行核心逻辑（JSON schema + tool_calls 解析 + 循环）")
    print("  LangChain: ~10 行核心逻辑（@tool + create_react_agent）")
    print()
    print("输入 'quit' 退出")
    print("-" * 60)

    # 对话历史（LangChain 用消息列表管理）
    chat_history = []

    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # 调用 Agent
        # LangChain 的 Agent 自动处理：
        #   1. 把消息和工具定义发给 LLM
        #   2. 解析 tool_calls
        #   3. 执行工具
        #   4. 把结果发回 LLM
        #   5. 重复直到 LLM 给出最终回答
        try:
            result = agent.invoke({
                "messages": chat_history + [
                    {"role": "user", "content": user_input}
                ]
            })

            # 提取最终回答
            # result["messages"] 包含了完整的消息历史
            # 最后一条是 AI 的最终回答
            ai_message = result["messages"][-1]
            reply = ai_message.content

            # 更新对话历史
            chat_history = result["messages"]

            print(f"\nAgent: {reply}")

        except Exception as e:
            print(f"\n错误: {e}")


if __name__ == "__main__":
    main()
