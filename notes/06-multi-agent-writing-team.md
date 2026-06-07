> [!info] related notes
> - 前置笔记: [[05-bugfix-agent|Bug 修复 Agent]]
> - 后续笔记: [[07-agent-api-service|Agent API 服务]]
> - 所属 MOC: [[learn-ai-agent-moc|学习 AI Agent MOC]]
> - 相关概念: [[multi-agent-pattern|多 Agent 模式]]、[[role-separation|角色分离]]
> - 相关资源: [[open-router|OpenRouter]]

# 多 Agent 写作团队 — 角色协作

## 目标

用 3 个 Agent 协作完成一篇技术博客：**Researcher（找资料）→ Writer（写文章）→ Reviewer（审查）→ Writer（改稿）。**

## 和前两天的区别

| | Day 5（Bugfix Agent） | Day 6（Multi-Agent） |
|---|---|---|
| Agent 数量 | 1 个 | 3 个 |
| 核心模式 | 自我反思（一个 Agent 反复修改自己） | 团队协作（多个 Agent 各司其职） |
| 质量保障 | 测试通过/失败 | Reviewer 审查 + Writer 改稿 |
| 适用场景 | 执行-观察-修正 | 需要不同视角的任务 |

## 前置条件

```bash
uv add requests python-dotenv
uv run python main.py
```

项目结构：

```
day6-multi-agent/
├── main.py        # 入口，编排多 Agent 流程
├── agents.py      # 3 个 Agent 角色定义
├── llm.py         # LLM 调用封装
└── .env
```

## 核心理解：多 Agent 模式

### 什么是多 Agent？

**不同角色的 LLM 调用，串联起来，传递中间结果。**

"多 Agent" 不是什么神秘架构，本质上就是：

```python
research = researcher(topic)        # LLM 调用 1：调研员角色
draft = writer(topic, research)     # LLM 调用 2：写手角色
feedback = reviewer(topic, draft)   # LLM 调用 3：审查员角色
final = writer(topic, research, feedback=feedback)  # LLM 调用 4：写手改稿
```

每个 Agent = 一个函数 + 专属的 system prompt + 特定的任务。

### 为什么多 Agent 比单 Agent 好？

```
单 Agent: "你又找资料又写又检查"
→ 角色模糊，容易遗漏，质量不稳定

多 Agent: 每个角色只做一件事
→ 专注、可检查、可迭代
```

类比：
- 单 Agent = 一个人写文章，写完就交
- 多 Agent = 一个团队，有人调研、有人写、有人审

### 三个角色的分工

| 角色 | 职责 | 输入 | 输出 |
|------|------|------|------|
| Researcher | 搜集和整理资料 | 主题 | 结构化调研资料 |
| Writer | 撰写/修改文章 | 主题 + 资料 +（修改意见） | 文章 |
| Reviewer | 检查质量 | 主题 + 文章 | 修改意见 |

### 中间结果传递

**每个 Agent 的输出是下一个 Agent 的输入：**

```
Researcher 输出 → 传给 Writer 作为素材
Writer 输出 → 传给 Reviewer 审查
Reviewer 输出 → 传给 Writer 改稿
```

这就是"中间结果传递" — 多 Agent 协作的核心机制。

## 完整代码

### agents.py — 三个 Agent 角色

> [!note]- 展开查看 agents.py
> ```python
> """
> Agent 角色定义。
> 每个 Agent 就是一个函数，有自己专属的 system prompt 和任务。
> """
>
> from llm import call_llm
>
>
> def researcher(topic: str) -> str:
>     """
>     调研员：负责搜集和整理资料。
>     输入: 研究主题 → 输出: 结构化的调研资料
>     """
>     print("  🔍 Researcher: 正在搜集资料...")
>
>     system = (
>         "You are a technical researcher. "
>         "Your job is to gather comprehensive, accurate information on a given topic. "
>         "Organize your findings into clear sections with key facts, examples, and references. "
>         "Write in the same language as the topic."
>     )
>
>     prompt = f"""请对以下主题进行调研，整理出结构化的资料。
> 主题：{topic}
> 要求：
> 1. 列出 5-8 个关键知识点
> 2. 每个知识点包含：概念解释、实际例子、常见误区
> 3. 提供 2-3 个代码示例（如果是技术主题）
> 4. 列出 3-5 个值得深入的方向
> 5. 用 Markdown 格式输出
> 这些资料将用于撰写一篇技术博客文章。
> """
>     result = call_llm(prompt, system=system)
>     print(f"  ✅ Researcher: 资料整理完成（{len(result)} 字符）")
>     return result
>
>
> def writer(topic: str, research: str, feedback: str = "") -> str:
>     """
>     写手：基于调研资料撰写文章。
>     如果有 feedback，说明是第二轮 — 根据 Reviewer 的意见改稿。
>     """
>     if feedback:
>         print("  ✍️ Writer: 正在根据反馈修改文章...")
>         action = "修改"
>     else:
>         print("  ✍️ Writer: 正在撰写初稿...")
>         action = "撰写"
>
>     system = (
>         "You are a technical blog writer. "
>         "You write clear, engaging, and well-structured articles. "
>         "Use a friendly but professional tone. "
>         "Include code examples when appropriate. "
>         "Write in the same language as the topic."
>     )
>
>     prompt = f"""请基于以下调研资料，{action}一篇技术博客文章。
> 主题：{topic}
> 调研资料：{research}
> """
>     if feedback:
>         prompt += f"\n上一版的修改意见：{feedback}\n请根据以上意见修改文章。保留好的部分，改进不足的地方。\n"
>
>     prompt += """
> 文章要求：
> 1. 标题吸引人
> 2. 开头用一两句话说明"为什么读者应该关心这个话题"
> 3. 结构清晰：引言 → 核心内容（3-5 个要点）→ 总结
> 4. 每个要点有解释 + 代码示例（如果是技术主题）
> 5. 结尾有总结和行动建议
> 6. 1500-2500 字，Markdown 格式
> """
>     result = call_llm(prompt, system=system, max_tokens=4000)
>     print(f"  ✅ Writer: {action}完成（{len(result)} 字符）")
>     return result
>
>
> def reviewer(topic: str, article: str) -> str:
>     """
>     审查员：检查文章的质量。
>     输入: 主题 + 文章 → 输出: 结构化的修改意见
>     """
>     print("  🔎 Reviewer: 正在审查文章...")
>
>     system = (
>         "You are a senior technical editor. "
>         "Your job is to review articles for accuracy, structure, readability, and completeness. "
>         "Be constructive but thorough. "
>         "Write your review in the same language as the article."
>     )
>
>     prompt = f"""请审查以下技术博客文章，给出详细的修改意见。
> 主题：{topic}
> 文章内容：{article}
>
> 请从以下维度审查：
> 1. **准确性**：技术内容是否正确？
> 2. **结构**：文章结构是否清晰？
> 3. **可读性**：代码示例是否清晰？解释是否易懂？
> 4. **完整性**：是否覆盖了重要知识点？
> 5. **吸引力**：标题和开头是否吸引人？
>
> 输出格式：
> - 总体评分（1-10）
> - 优点（2-3 个）
> - 需要改进的地方（3-5 个，按优先级排序）
> - 具体修改建议（每个建议要说明改什么、为什么改）
> """
>     result = call_llm(prompt, system=system)
>     print(f"  ✅ Reviewer: 审查完成（{len(result)} 字符）")
>     return result
> ```

### main.py — 编排流程

> [!note]- 展开查看 main.py
> ```python
> """
> Day 6: 多 Agent 写作团队
> 多 Agent = 角色拆分 + 中间结果传递 + 质量检查
> """
>
> from agents import researcher, writer, reviewer
>
>
> def write_article(topic: str) -> str:
>     """多 Agent 协作的完整流程。每个 Agent 的输出是下一个 Agent 的输入。"""
>     print(f"\n{'='*60}")
>     print(f"写作任务: {topic}")
>
>     # Step 1: Researcher 找资料
>     print("\n📌 Step 1/4: 调研阶段")
>     research = researcher(topic)
>
>     # Step 2: Writer 写初稿
>     print("\n📌 Step 2/4: 撰写初稿")
>     draft = writer(topic, research)
>
>     # Step 3: Reviewer 审查
>     print("\n📌 Step 3/4: 质量审查")
>     feedback = reviewer(topic, draft)
>
>     # 显示审查意见摘要
>     print("\n  📋 审查意见摘要:")
>     for line in feedback.split("\n"):
>         line = line.strip()
>         if line and (line.startswith("-") or line.startswith("*") or line.startswith("评分")):
>             print(f"     {line}")
>
>     # Step 4: Writer 根据反馈修改
>     print("\n📌 Step 4/4: 修改定稿")
>     final = writer(topic, research, feedback=feedback)
>
>     return final
>
>
> def main():
>     print("多 Agent 写作团队")
>     print("  🔍 Researcher — 搜集资料")
>     print("  ✍️ Writer — 撰写文章")
>     print("  🔎 Reviewer — 审查质量")
>     print("流程: 调研 → 初稿 → 审查 → 修改 → 定稿")
>
>     while True:
>         topic = input("\n写作主题: ").strip()
>         if not topic:
>             continue
>         if topic.lower() in ("quit", "exit", "q"):
>             break
>
>         article = write_article(topic)
>         print("\n📄 最终文章:")
>         print(article)
>
>         safe_name = topic.replace(" ", "_")[:30]
>         filename = f"article_{safe_name}.md"
>         with open(filename, "w", encoding="utf-8") as f:
>             f.write(article)
>         print(f"\n📄 已保存到: {filename}")
>
>
> if __name__ == "__main__":
>     main()
> ```

## 运行效果

```
============================================================
写作任务: 写作主题：为什么你应该学RUST
============================================================

📌 Step 1/4: 调研阶段
  🔍 Researcher: 正在搜集资料...
  ✅ Researcher: 资料整理完成（4488 字符）

📌 Step 2/4: 撰写初稿
  ✍️ Writer: 正在撰写初稿...
  ✅ Writer: 撰写完成（5448 字符）

📌 Step 3/4: 质量审查
  🔎 Reviewer: 正在审查文章...
  ✅ Reviewer: 审查完成（2556 字符）

  📋 审查意见摘要:
     **总体评分**：8 / 10
     - 建议补充生命周期的具体例子
     - 建议添加基准测试数据
     - 建议保持客观，避免一刀切的负面评价

📌 Step 4/4: 修改定稿
  ✍️ Writer: 正在根据反馈修改文章...
  ✅ Writer: 修改完成（7056 字符）

============================================================
写作完成！
============================================================
```

## 踩坑记录

### Reviewer 给了 8 分而不是 10 分

这正是多 Agent 的价值 — **单 Agent 写完就结束了，多 Agent 有质量检查和迭代。**

Reviewer 给出了具体的改进建议：
- 补充生命周期的具体例子
- 添加基准测试数据
- 保持客观性

Writer 根据这些反馈改进了文章，最终版本比初稿增加了 30% 内容。

### 每个 Agent 的 system prompt 是关键

三个 Agent 用的是同一个 LLM，但 system prompt 不同：

```python
# Researcher 的 system prompt
"You are a technical researcher..."

# Writer 的 system prompt
"You are a technical blog writer..."

# Reviewer 的 system prompt
"You are a senior technical editor..."
```

**同一个 LLM + 不同的 system prompt = 不同的角色。** 这就是"多 Agent"的本质。

## 关键流程解析

### 多 Agent 的三个要素

```
1. 角色分离 — 每个 Agent 只做一件事（调研/写作/审查）
2. 中间结果传递 — Researcher 的输出变成 Writer 的输入
3. 质量循环 — Reviewer 的反馈回到 Writer
```

### 和 Day 5 的对比

```
Day 5 (Reflection):  一个 Agent 反复修改自己的代码
                     → 执行 → 观察 → 修正 → 执行 → ...

Day 6 (Multi-Agent): 多个 Agent 互相检查
                     → Researcher → Writer → Reviewer → Writer
```

区别在于"视角"：
- Reflection：同一个视角反复看
- Multi-Agent：不同角色从不同角度看

### 可以扩展的模式

今天的写法是简单的串行。实际项目中可以扩展为：

```
并行调研:  多个 Researcher 同时搜不同方向
投票审查:  多个 Reviewer 独立审查，投票决定是否通过
专家会诊:  不同领域的专家 Agent 各自审查自己擅长的部分
```

## 常见问题

1. **运行太慢**：要调 4 次 LLM，每轮需要 30-60 秒
2. **文章质量不稳定**：LLM 的输出有随机性，同一主题多次运行结果不同
3. **Reviewer 太严格/太宽松**：调整 Reviewer 的 system prompt
4. **Writer 没有采纳反馈**：在 prompt 中强调"必须根据反馈修改"
