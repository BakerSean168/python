"""
Agent 逻辑模块。

这里复用 Day 1-6 学到的所有能力：
- LLM 调用（Day 1）
- 工具调用（Day 2，简化版）
- 多步骤 Pipeline（Day 4）
- 多 Agent 协作（Day 6）
"""

import requests
from config import OPENROUTER_API_KEY, OPENROUTER_API_URL, MODEL, LLM_TIMEOUT, logger


def call_llm(prompt: str, system: str = "You are a helpful assistant.", max_tokens: int = 3000) -> str:
    """
    调用 LLM 的基础函数。

    所有 Agent 都通过这个函数和 LLM 交互。
    """
    if not OPENROUTER_API_KEY:
        return "Error: OPENROUTER_API_KEY not configured"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
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
        r = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=(10, LLM_TIMEOUT),
        )
        if r.status_code != 200:
            logger.error(f"LLM API error: HTTP {r.status_code} - {r.text[:200]}")
            return f"API error: HTTP {r.status_code}"
        return r.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logger.error(f"LLM request failed: {e}")
        return f"Network error: {e}"


# ============================================================
# Agent 1: 聊天 Agent（Day 1 的能力）
# ============================================================

def chat_agent(message: str, system_prompt: str) -> str:
    """简单的聊天 Agent"""
    logger.info(f"Chat request: {message[:50]}...")
    response = call_llm(message, system=system_prompt)
    logger.info(f"Chat response: {len(response)} chars")
    return response


# ============================================================
# Agent 2: 调研 Agent（Day 4 的能力，简化版）
# ============================================================

def research_agent(topic: str) -> str:
    """
    调研 Agent — 简化版。

    完整版（Day 4）会搜索网页、抓取内容。
    这里用 LLM 的知识模拟，但保持多步骤结构。
    """
    logger.info(f"Research request: {topic}")

    # Step 1: 生成关键词（简化 — 直接用主题）
    # Step 2-3: 搜索和抓取（省略 — 用 LLM 知识代替）

    # Step 4: 让 LLM 整理调研资料
    research_prompt = f"""请对以下主题进行调研，整理出结构化的资料。

主题：{topic}

要求：
1. 列出 5-8 个关键知识点
2. 每个知识点包含：概念解释、实际例子
3. 提供 2-3 个代码示例（如果是技术主题）
4. 列出 3-5 个值得深入的方向
5. 用 Markdown 格式输出
"""
    research = call_llm(research_prompt, system="You are a technical researcher.")

    # Step 5: 生成报告
    report_prompt = f"""请根据以下调研资料，写一份简洁的调研报告。

调研资料：
{research}

报告格式：
# {topic} 调研报告

## 核心发现
（3-5 个要点）

## 详细内容
（分点展开）

## 总结
（一段话概括）
"""
    report = call_llm(report_prompt, system="You are a research report writer.")
    logger.info(f"Research completed: {len(report)} chars")
    return report


# ============================================================
# Agent 3: 写作 Agent（Day 6 的能力，简化版）
# ============================================================

def write_agent(topic: str) -> str:
    """
    多 Agent 写作 — 简化版。

    完整版（Day 6）有 Researcher + Writer + Reviewer 三个角色。
    这里合并成两个 LLM 调用（写 + 审查改写）。
    """
    logger.info(f"Write request: {topic}")

    # Step 1: 写初稿
    draft_prompt = f"""请写一篇关于"{topic}"的技术博客文章。

要求：
1. 标题吸引人
2. 结构：引言 → 核心内容（3-5 个要点）→ 总结
3. 包含代码示例（如果是技术主题）
4. 1500-2500 字
5. 用 Markdown 格式
"""
    draft = call_llm(draft_prompt, system="You are a technical blog writer.", max_tokens=4000)

    # Step 2: 审查
    review_prompt = f"""请审查以下文章，给出 3-5 个具体的改进建议。

文章：
{draft[:3000]}

只返回改进建议，不要重写文章。
"""
    feedback = call_llm(review_prompt, system="You are a technical editor.")

    # Step 3: 修改
    revise_prompt = f"""请根据以下建议修改文章。

原文：
{draft}

修改建议：
{feedback}

返回修改后的完整文章。
"""
    final = call_llm(revise_prompt, system="You are a technical blog writer.", max_tokens=4000)
    logger.info(f"Write completed: {len(final)} chars")
    return final
