"""
Day 6: 多 Agent 写作团队

核心思想：
  多 Agent = 角色拆分 + 中间结果传递 + 质量检查

和 Day 5 的区别：
  Day 5: 一个 Agent 反复修改自己的代码（自我反思）
  Day 6: 多个 Agent 各司其职，互相检查（团队协作）

三个角色：
  Researcher → 找资料
  Writer → 写文章
  Reviewer → 检查质量 → 给修改意见 → Writer 改稿

Setup:
  uv add requests python-dotenv
  uv run python main.py
"""

from agents import researcher, writer, reviewer


def write_article(topic: str) -> str:
    """
    多 Agent 协作的完整流程。

    每个 Agent 的输出是下一个 Agent 的输入。
    这就是"中间结果传递"。
    """
    print(f"\n{'='*60}")
    print(f"写作任务: {topic}")
    print(f"{'='*60}")

    # Step 1: Researcher 找资料
    print("\n📌 Step 1/4: 调研阶段")
    research = researcher(topic)

    # Step 2: Writer 写初稿
    print("\n📌 Step 2/4: 撰写初稿")
    draft = writer(topic, research)

    # Step 3: Reviewer 审查
    print("\n📌 Step 3/4: 质量审查")
    feedback = reviewer(topic, draft)

    # 显示审查意见摘要
    print("\n  📋 审查意见摘要:")
    for line in feedback.split("\n"):
        line = line.strip()
        if line and (line.startswith("-") or line.startswith("*") or line.startswith("评分")):
            print(f"     {line}")

    # Step 4: Writer 根据反馈修改
    print("\n📌 Step 4/4: 修改定稿")
    final = writer(topic, research, feedback=feedback)

    print(f"\n{'='*60}")
    print("写作完成！")
    print(f"{'='*60}")

    return final


def main():
    print("=" * 60)
    print("多 Agent 写作团队")
    print("=" * 60)
    print()
    print("三个 Agent 协作完成一篇技术博客：")
    print("  🔍 Researcher — 搜集资料")
    print("  ✍️ Writer — 撰写文章")
    print("  🔎 Reviewer — 审查质量")
    print()
    print("流程: 调研 → 初稿 → 审查 → 修改 → 定稿")
    print("输入 'quit' 退出")
    print("-" * 60)

    while True:
        topic = input("\n写作主题: ").strip()

        if not topic:
            continue

        if topic.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # 执行多 Agent 流程
        article = write_article(topic)

        # 输出最终文章
        print("\n" + "=" * 60)
        print("📄 最终文章")
        print("=" * 60)
        print(article)

        # 保存
        safe_name = topic.replace(" ", "_")[:30]
        filename = f"article_{safe_name}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(article)
        print(f"\n📄 已保存到: {filename}")


if __name__ == "__main__":
    main()
