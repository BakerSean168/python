"""
Day 2: Tool Agent — 手写工具调用

核心思想：
  Agent = LLM + tools + loop
  模型决定"要不要调用工具"，代码负责"执行工具"，然后把结果还给模型。

和 Day 1 的区别：
  Day 1: 用户 → 模型 → 回答（模型只能用自己知道的知识）
  Day 2: 用户 → 模型 → 可能调用工具 → 基于工具结果回答（模型能使用外部能力）

Setup:
  1. 复用 Day 1 的 .env（OPENROUTER_API_KEY）
  2. uv add requests python-dotenv
  3. uv run python main.py
"""

import os
import json
import requests
from dotenv import load_dotenv
from tools import TOOLS, TOOL_MAP

load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    print("Error: 在 .env 文件中设置 OPENROUTER_API_KEY")
    exit(1)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-120b:free"

SYSTEM_INSTRUCTION = {
    "role": "system",
    "content": (
        "You are a helpful assistant with access to tools. "
        "Use tools when the user's question needs real-time data or calculations. "
        "Answer in the same language the user uses. "
        "Keep answers concise."
    ),
}

history = [SYSTEM_INSTRUCTION]


def call_api(messages: list[dict]) -> dict:
    """
    调用 OpenRouter API（非流式）。

    和 Day 1 不同，这次我们不用流式输出。
    因为工具调用时，API 返回的不是文字，而是结构化的 tool_calls 数据。
    流式处理 tool_calls 会更复杂，Day 2 先用非流式理解原理。

    返回:
        API 的完整响应对象（dict）
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,  # 关键：告诉模型有哪些工具可用
        "stream": False,
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=(10, 60))
        if r.status_code != 200:
            print(f"\nAPI 错误 (HTTP {r.status_code}): {r.text[:200]}")
            return {}
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"\n网络请求失败：{e}")
        return {}


def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    执行一个工具函数。

    参数:
        tool_name: 工具名（如 "get_weather"）
        arguments: 参数字典（如 {"city": "东京"}）

    返回:
        工具执行结果的字符串
    """
    func = TOOL_MAP.get(tool_name)
    if not func:
        return f"错误：未知工具 '{tool_name}'"

    try:
        result = func(**arguments)  # **arguments 把字典展开为关键字参数
        return result
    except Exception as e:
        return f"工具执行错误：{e}"


def agent_loop(user_input: str) -> str:
    """
    Agent 的核心循环。

    流程：
    1. 把用户消息加入历史
    2. 调用 API
    3. 检查返回：
       - 有 content → 直接返回（不需要工具）
       - 有 tool_calls → 执行工具 → 把结果加入历史 → 回到第 2
    4. 重复直到模型给出最终文字回答

    这就是 Agent 的 "loop" 部分。
    """
    history.append({"role": "user", "content": user_input})

    while True:
        response = call_api(history)

        if not response or "choices" not in response:
            return "API 返回异常，请重试。"

        message = response["choices"][0]["message"]

        # 情况 1：模型直接回答（没有调用工具）
        if message.get("content") and not message.get("tool_calls"):
            reply = message["content"]
            history.append({"role": "assistant", "content": reply})
            return reply

        # 情况 2：模型想调用工具
        if message.get("tool_calls"):
            # 先把模型的 tool_calls 请求加入历史
            # 注意：这里要原样保存整个 message，不能只取 content
            history.append(message)

            # 逐个执行工具
            for tool_call in message["tool_calls"]:
                func_name = tool_call["function"]["name"]
                # arguments 是 JSON 字符串，需要解析成 dict
                func_args = json.loads(tool_call["function"]["arguments"])
                tool_call_id = tool_call["id"]

                print(f"  🔧 调用工具: {func_name}({func_args})")

                # 执行工具
                result = execute_tool(func_name, func_args)
                print(f"  📋 工具结果: {result}")

                # 把工具结果加入历史
                # role 是 "tool"，tool_call_id 告诉模型这是哪个工具调用的结果
                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result,
                })

            # 工具结果已加入历史，继续循环，让模型基于结果生成回答
            continue

        # 情况 3：既没有 content 也没有 tool_calls（异常）
        return "模型返回了未知格式的响应。"


# --- 主循环 ---
print(f"Tool Agent (model: {MODEL})")
print("我有 3 个工具：查天气、算数学、搜笔记")
print("输入 'quit' 退出 | 'history' 查看历史 | 'clear' 清空")
print("-" * 60)

while True:
    user_input = input("\nYou: ").strip()

    if user_input.lower() in ("quit", "exit", "q"):
        print("Goodbye!")
        break

    if user_input.lower() == "history":
        for msg in history:
            role = msg.get("role", "?")
            if role == "system":
                continue
            if role == "tool":
                print(f"  [tool] {msg['content'][:80]}")
            elif msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    print(f"  [call] {tc['function']['name']}({tc['function']['arguments']})")
            elif msg.get("content"):
                label = "You" if role == "user" else "Agent"
                print(f"  [{label}] {msg['content'][:80]}")
        continue

    if user_input.lower() == "clear":
        history = [SYSTEM_INSTRUCTION]
        print("历史已清空。")
        continue

    if not user_input:
        continue

    # Agent 处理
    reply = agent_loop(user_input)
    print(f"\nAgent: {reply}")
