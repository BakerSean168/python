"""
Day 3: RAG 文件问答 Agent

核心思想：
  不要让模型"猜"答案，先从文档里找相关内容，再让模型基于真实内容回答。
  这就是 RAG — Retrieval Augmented Generation（检索增强生成）。

流程：
  用户提问 → 向量搜索找到相关段落 → 把段落塞进 prompt → 模型回答

和 Day 2 的区别：
  Day 2: 模型调用工具（天气、计算）— 工具返回精确结果
  Day 3: 模型基于检索到的文档段落回答 — 更适合"知识问答"场景

Setup:
  1. uv add sentence-transformers chromadb requests python-dotenv
  2. uv run python main.py
  3. 输入文件路径加载文档，然后开始提问
"""

import os
import json
import requests
from dotenv import load_dotenv
from rag import VectorStore, load_and_index

load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    print("Error: 在 .env 文件中设置 OPENROUTER_API_KEY")
    exit(1)

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-120b:free"


def call_llm(system_prompt: str, user_message: str) -> str:
    """
    调用 LLM（非流式）。

    RAG 场景下，system_prompt 会包含检索到的文档内容。
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=(10, 60))
        if r.status_code != 200:
            return f"API 错误 (HTTP {r.status_code})"
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"网络请求失败：{e}"


def build_rag_prompt(query: str, store: VectorStore, top_k: int = 3) -> str:
    """
    RAG 的核心：构建包含检索结果的 prompt。

    步骤：
    1. 用问题搜索相关文本块
    2. 把文本块拼成"参考资料"
    3. 告诉模型"基于这些资料回答"

    返回:
        完整的 system prompt（包含检索到的内容）
    """
    # 搜索相关文本块
    results = store.search(query, top_k=top_k)

    if not results:
        return (
            "你是一个助手。没有找到相关文档内容。"
            "请根据你的知识回答，如果不确定请说明。"
        )

    # 拼装参考资料
    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(
            f"--- 参考段落 {i}（来源: {r['source']}）---\n{r['text']}"
        )

    context = "\n\n".join(context_parts)

    # 构建 prompt
    system_prompt = f"""你是一个知识问答助手。请根据以下参考资料回答用户的问题。

规则：
1. 优先使用参考资料中的内容回答
2. 如果参考资料中没有相关信息，请明确说明
3. 回答时可以引用来源
4. 保持回答简洁准确

参考资料：
{context}
"""

    return system_prompt


# --- 主程序 ---
print("=" * 60)
print("RAG 文件问答 Agent")
print("=" * 60)

# 初始化向量数据库
store = VectorStore()

# 加载文档
print("\n可用命令:")
print("  load <文件路径>  — 加载文档到知识库")
print("  ask <问题>       — 基于文档回答问题")
print("  search <关键词>  — 直接搜索相关段落（不经过 LLM）")
print("  status           — 查看已加载的文档")
print("  quit             — 退出")
print("-" * 60)

while True:
    user_input = input("\n> ").strip()

    if not user_input:
        continue

    if user_input.lower() in ("quit", "exit", "q"):
        print("Goodbye!")
        break

    # 加载文档
    if user_input.lower().startswith("load "):
        file_path = user_input[5:].strip().strip('"').strip("'")
        try:
            count = load_and_index(file_path, store)
            print(f"✅ 成功加载，共 {count} 个文本块")
        except FileNotFoundError:
            print(f"❌ 文件不存在: {file_path}")
        except Exception as e:
            print(f"❌ 加载失败: {e}")
        continue

    # 搜索（不经过 LLM）
    if user_input.lower().startswith("search "):
        query = user_input[7:].strip()
        results = store.search(query, top_k=3)
        if results:
            for i, r in enumerate(results, 1):
                print(f"\n--- 结果 {i} (来源: {r['source']}, 距离: {r['distance']:.4f}) ---")
                print(r["text"][:300])
        else:
            print("没有找到相关内容。")
        continue

    # 查看状态
    if user_input.lower() == "status":
        count = store.collection.count()
        print(f"向量数据库中有 {count} 个文本块")
        continue

    # 默认：RAG 问答
    query = user_input
    print("正在检索相关文档...")
    system_prompt = build_rag_prompt(query, store)

    print("正在生成回答...\n")
    answer = call_llm(system_prompt, query)
    print(f"Agent: {answer}")
