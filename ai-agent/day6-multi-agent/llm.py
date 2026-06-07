"""
LLM 调用模块（复用 Day 4 的设计）
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-120b:free"


def call_llm(prompt: str, system: str = "You are a helpful assistant.", max_tokens: int = 3000) -> str:
    """调用 LLM，返回文本响应"""
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
            return f"API error: {r.status_code}"
        return r.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        return f"Network error: {e}"
