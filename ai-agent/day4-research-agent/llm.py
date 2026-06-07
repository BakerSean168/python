"""
LLM 调用模块。

封装 OpenRouter API 调用，提供简单的接口给 pipeline 使用。
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-120b:free"


def call_llm(prompt: str, system: str = "You are a helpful assistant.", max_tokens: int = 2000) -> str:
    """
    调用 LLM，返回文本响应。

    参数:
        prompt: 用户消息
        system: 系统指令
        max_tokens: 最大输出长度

    返回:
        模型的回复文本
    """
    if not api_key:
        return "Error: OPENROUTER_API_KEY not set"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "stream": False,
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=(10, 120))
        if r.status_code != 200:
            return f"API error (HTTP {r.status_code}): {r.text[:200]}"
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        return f"Network error: {e}"


def call_llm_json(prompt: str, system: str = "You are a helpful assistant.") -> dict | list | None:
    """
    调用 LLM 并尝试解析返回的 JSON。

    有些步骤（如生成关键词）需要结构化输出。
    我们在 prompt 里要求模型返回 JSON，然后解析它。

    返回:
        解析后的 dict/list，失败返回 None
    """
    response = call_llm(prompt, system)

    # 尝试从响应中提取 JSON
    # 模型可能在 JSON 前后加了文字，需要处理
    try:
        # 先试直接解析
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # 尝试找 JSON 块（被 ```json ... ``` 包裹的）
    if "```json" in response:
        start = response.index("```json") + 7
        end = response.index("```", start)
        try:
            return json.loads(response[start:end].strip())
        except json.JSONDecodeError:
            pass

    # 尝试找 [ 或 { 开始的 JSON
    for start_char, end_char in [("[", "]"), ("{", "}")]:
        if start_char in response:
            start = response.index(start_char)
            # 从后往前找结束符
            end = response.rfind(end_char)
            if end > start:
                try:
                    return json.loads(response[start:end + 1])
                except json.JSONDecodeError:
                    pass

    return None
