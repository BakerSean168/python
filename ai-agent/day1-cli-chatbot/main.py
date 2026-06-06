"""
Day 1: CLI Chatbot — OpenRouter 版本

核心思想: Agent = LLM + system instruction + conversation history + loop

这次用 OpenRouter 作为 AI 提供商，格式兼容 OpenAI Chat Completions API。
好处：一个 API key 访问几百个模型（GPT、Claude、Gemini、Llama...）

Setup:
  1. 注册 https://openrouter.ai → 获取 API key
  2. uv add requests python-dotenv
  3. 在 .env 文件中添加: OPENROUTER_API_KEY=your-key-here
  4. uv run python main.py
"""

import os
import json
import requests
from dotenv import load_dotenv

# --- Step 1: 加载 .env 中的 API key ---
load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    print("Error: 在 .env 文件中设置 OPENROUTER_API_KEY")
    print("  示例: OPENROUTER_API_KEY=sk-or-v1-xxxxxxxx")
    exit(1)

# --- Step 2: API 配置 ---
# OpenRouter 兼容 OpenAI 的 Chat Completions 格式
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# 选择模型 — 去 https://openrouter.ai/models 查看所有可用模型
# 免费模型以 ":free" 结尾，例如:
#   google/gemini-2.0-flash-exp:free
#   meta-llama/llama-3.3-8b-instruct:free
#   deepseek/deepseek-chat-v3-0324:free
MODEL = "openai/gpt-oss-120b:free"

# --- Step 3: System instruction ---
# 这是 Agent 的"人格"和"规则"
SYSTEM_INSTRUCTION = {
    "role": "system",
    "content": (
        "You are a friendly Python tutor. "
        "Keep answers short and clear. "
        "Use simple code examples when helpful. "
        "Respond in the same language the user uses."
    ),
}

# --- Step 4: 对话历史 ---
# 列表里每一条都是一个 dict: {"role": "...", "content": "..."}
# role 只有三种: system / user / assistant
history = [SYSTEM_INSTRUCTION]


def chat_stream(messages: list[dict]) -> str:
    """
    调用 OpenRouter API，流式返回响应。

    参数:
        messages: 对话历史列表

    返回:
        完整的响应文本
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,  # 流式输出
    }

    full_response = ""

    try:
        with requests.post(API_URL, headers=headers, json=payload, stream=True, timeout=(10,30)) as r:
            r.encoding = "utf-8"
            # 检查 HTTP 状态码
            if r.status_code != 200:
                print(f"\nAPI 错误 (HTTP {r.status_code}): {r.text}")
                return ""

            # 处理 SSE (Server-Sent Events) 流式数据
            buffer = ""
            done = False
            for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
                if done:
                    break
                buffer += chunk

                while True:
                    line_end = buffer.find("\n")
                    if line_end == -1:
                        break
                    line = buffer[:line_end].strip()
                    buffer = buffer[line_end + 1 :]

                    if line.startswith("data: "):
                        data = line[6:]

                        if data == "[DONE]":
                            done = True
                            break

                        try:
                            data_obj = json.loads(data)
                            content = data_obj["choices"][0]["delta"].get("content")
                            if content:
                                print(content, end="", flush=True)
                                full_response += content
                        except json.JSONDecodeError:
                            pass

        print()  # 换行
        return full_response
    except requests.exceptions.RequestException as e:
        print(f"\n网络请求失败： {e}")
        return ""

# --- Step 5: 主循环 ---
print(f"Python Tutor Agent (model: {MODEL})")
print("输入 'quit' 退出 | 输入 'history' 查看历史 | 输入 'clear' 清空历史")
print("-" * 60)

while True:
    user_input = input("\nYou: ").strip()

    # 特殊命令
    if user_input.lower() in ("quit", "exit", "q"):
        print("Goodbye!")
        break

    if user_input.lower() == "history":
        for msg in history:
            if msg["role"] == "system":
                continue
            role = "You" if msg["role"] == "user" else "Agent"
            if len(msg["content"]) > 80:
                print(f"  [{role}] {msg['content'][:80]}...")
            else:                
                print(f"  [{role}] {msg['content']}")
        continue

    if user_input.lower() == "clear":
        history = [SYSTEM_INSTRUCTION]
        print("历史已清空。")
        continue

    if not user_input:
        continue

    # 添加用户消息到历史
    history.append({"role": "user", "content": user_input})

    # 调用 API，流式输出
    print("\nAgent: ", end="")
    reply = chat_stream(history)

    # 添加助手回复到历史
    if reply:
        history.append({"role": "assistant", "content": reply})
    else:
        print("(没有收到回复，请重试)")
