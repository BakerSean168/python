"""
Agent 角色定义。

每个 Agent 就是一个函数，有自己专属的 system prompt 和任务。
"多 Agent"的本质：不同角色的 LLM 调用，串联起来，传递中间结果。
"""

from llm import call_llm


# ============================================================
# Agent 1: Researcher（调研员）
# ============================================================

def researcher(topic: str) -> str:
    """
    调研员：负责搜集和整理资料。

    输入: 研究主题
    输出: 结构化的调研资料

    注意：这里用 LLM 模拟调研（基于训练数据）。
    实际项目中，这个角色会调用搜索 API（像 Day 4 那样）。
    """
    print("  🔍 Researcher: 正在搜集资料...")

    system = (
        "You are a technical researcher. "
        "Your job is to gather comprehensive, accurate information on a given topic. "
        "Organize your findings into clear sections with key facts, examples, and references. "
        "Write in the same language as the topic."
    )

    prompt = f"""请对以下主题进行调研，整理出结构化的资料。

主题：{topic}

要求：
1. 列出 5-8 个关键知识点
2. 每个知识点包含：概念解释、实际例子、常见误区
3. 提供 2-3 个代码示例（如果是技术主题）
4. 列出 3-5 个值得深入的方向
5. 用 Markdown 格式输出

这些资料将用于撰写一篇技术博客文章。
"""

    result = call_llm(prompt, system=system)
    print(f"  ✅ Researcher: 资料整理完成（{len(result)} 字符）")
    return result


# ============================================================
# Agent 2: Writer（写手）
# ============================================================

def writer(topic: str, research: str, feedback: str = "") -> str:
    """
    写手：基于调研资料撰写文章。

    输入: 主题 + 调研资料 +（可选的修改意见）
    输出: 文章初稿或修改稿

    如果有 feedback，说明是第二轮 — 根据 Reviewer 的意见改稿。
    """
    if feedback:
        print("  ✍️ Writer: 正在根据反馈修改文章...")
        action = "修改"
    else:
        print("  ✍️ Writer: 正在撰写初稿...")
        action = "撰写"

    system = (
        "You are a technical blog writer. "
        "You write clear, engaging, and well-structured articles. "
        "Use a friendly but professional tone. "
        "Include code examples when appropriate. "
        "Write in the same language as the topic."
    )

    prompt = f"""请基于以下调研资料，{action}一篇技术博客文章。

主题：{topic}

调研资料：
{research}
"""

    if feedback:
        prompt += f"""
上一版的修改意见：
{feedback}

请根据以上意见修改文章。保留好的部分，改进不足的地方。
"""

    prompt += """
文章要求：
1. 标题吸引人
2. 开头用一两句话说明"为什么读者应该关心这个话题"
3. 结构清晰：引言 → 核心内容（3-5 个要点）→ 总结
4. 每个要点有解释 + 代码示例（如果是技术主题）
5. 结尾有总结和行动建议
6. 1500-2500 字
7. 用 Markdown 格式
"""

    result = call_llm(prompt, system=system, max_tokens=4000)
    print(f"  ✅ Writer: {action}完成（{len(result)} 字符）")
    return result


# ============================================================
# Agent 3: Reviewer（审查员）
# ============================================================

def reviewer(topic: str, article: str) -> str:
    """
    审查员：检查文章的质量。

    输入: 主题 + 文章
    输出: 结构化的修改意见

    审查维度：准确性、结构、可读性、完整性。
    """
    print("  🔎 Reviewer: 正在审查文章...")

    system = (
        "You are a senior technical editor. "
        "Your job is to review articles for accuracy, structure, readability, and completeness. "
        "Be constructive but thorough. "
        "Write your review in the same language as the article."
    )

    prompt = f"""请审查以下技术博客文章，给出详细的修改意见。

主题：{topic}

文章内容：
{article}

请从以下维度审查：

1. **准确性**：技术内容是否正确？有没有过时或错误的信息？
2. **结构**：文章结构是否清晰？段落之间是否有逻辑衔接？
3. **可读性**：代码示例是否清晰？解释是否易懂？
4. **完整性**：是否覆盖了重要知识点？有没有遗漏？
5. **吸引力**：标题和开头是否吸引人？结尾是否有力？

输出格式：
- 总体评分（1-10）
- 优点（2-3 个）
- 需要改进的地方（3-5 个，按优先级排序）
- 具体修改建议（每个建议要说明改什么、为什么改）
"""

    result = call_llm(prompt, system=system)
    print(f"  ✅ Reviewer: 审查完成（{len(result)} 字符）")
    return result
