"""
Day 4: 网页调研 Agent

核心思想：
  Agent 不只是"问一句答一句"，它可以执行多步骤任务。
  每一步的输出是下一步的输入，这就是 Pipeline。

今天的流程：
  1. LLM 生成搜索关键词（把人类问题转成搜索词）
  2. DuckDuckGo 搜索（获取网页链接）
  3. 抓取网页内容（获取原始文本）
  4. LLM 提取重点（从长文中提炼关键信息）
  5. LLM 生成报告（汇总成结构化文档）

这个模式叫 RAG 的"外部知识获取"变种 — 不是从本地文档检索，
而是主动去互联网搜索、抓取、提取、整合。

Setup:
  uv add requests beautifulsoup4 duckduckgo-search python-dotenv
  uv run python main.py
"""

from pipeline import run_research


def main():
    print("=" * 60)
    print("网页调研 Agent")
    print("=" * 60)
    print()
    print("输入一个研究主题，Agent 会自动：")
    print("  生成关键词 → 搜索网页 → 抓取内容 → 提取重点 → 生成报告")
    print()
    print("输入 'quit' 退出")
    print("-" * 60)

    while True:
        topic = input("\n研究主题: ").strip()

        if not topic:
            continue

        if topic.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # 执行调研 pipeline
        report = run_research(topic)

        # 输出报告
        print("\n" + "=" * 60)
        print("📊 调研报告")
        print("=" * 60)
        print(report)

        # 保存报告到文件
        safe_name = topic.replace(" ", "_")[:30]
        filename = f"report_{safe_name}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n📄 报告已保存到: {filename}")


if __name__ == "__main__":
    main()
