"""
调研流水线 (Pipeline)。

这是 Day 4 的核心 — 把多个步骤串起来，每一步的输出是下一步的输入。

Pipeline 是最简单的"多步骤规划"。
LangGraph 本质上就是把这种流水线画成图，加上条件分支和状态管理。
但核心思想和这里一样：拆步骤、传数据、顺序执行。
"""

from llm import call_llm, call_llm_json
from search import search_web, fetch_page


# ============================================================
# Step 1: 生成搜索关键词
# ============================================================

def generate_keywords(topic: str) -> list[str]:
    """
    让 LLM 根据主题生成搜索关键词。

    为什么要让 LLM 生成，不直接用用户输入？
    因为用户的提问方式和搜索引擎的关键词不一样。
    例如用户问"Python 异步编程怎么学"→ 应该搜 "python asyncio tutorial"
    """
    prompt = f"""请根据以下研究主题，生成 3-5 个搜索关键词。

主题：{topic}

要求：
1. 关键词要适合搜索引擎（简洁、精准）
2. 混合中英文关键词（英文结果通常更多更好）
3. 覆盖主题的不同方面

只返回 JSON 数组，不要其他内容。例如：
["python async await tutorial", "Python asyncio 入门", "python concurrency guide"]
"""

    result = call_llm_json(
        prompt,
        system="You are a search keyword generator. Return only valid JSON arrays.",
    )

    if isinstance(result, list) and all(isinstance(k, str) for k in result):
        return result

    # 如果 LLM 返回了非预期格式，用主题本身作为关键词
    print("  ⚠️ 关键词生成失败，使用主题作为搜索词")
    return [topic]


# ============================================================
# Step 2: 搜索网页
# ============================================================

def search_multiple_keywords(keywords: list[str], results_per_keyword: int = 3) -> list[dict]:
    """
    用多个关键词分别搜索，合并结果。

    为什么用多个关键词？
    不同关键词能覆盖不同角度。搜"Python 异步"和搜"asyncio 教程"得到的结果不同。
    """
    all_results = []
    seen_urls = set()

    for keyword in keywords:
        print(f"  🔍 搜索: {keyword}")
        results = search_web(keyword, max_results=results_per_keyword)

        for r in results:
            # 去重：同一个 URL 只保留一次
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)

    return all_results


# ============================================================
# Step 3: 抓取网页内容
# ============================================================

def fetch_pages(search_results: list[dict], max_pages: int = 5) -> list[dict]:
    """
    抓取搜索结果的网页内容。

    不是每个结果都抓 — 太慢而且有些网页打不开。
    """
    pages = []
    for i, result in enumerate(search_results[:max_pages]):
        print(f"  📄 抓取 [{i+1}/{min(len(search_results), max_pages)}]: {result['title'][:50]}...")
        content = fetch_page(result["url"])

        if content and not content.startswith("[抓取失败"):
            pages.append({
                "title": result["title"],
                "url": result["url"],
                "snippet": result.get("snippet", ""),
                "content": content,
            })

    return pages


# ============================================================
# Step 4: 提取重点
# ============================================================

def extract_key_points(pages: list[dict], topic: str) -> list[dict]:
    """
    让 LLM 从每个网页中提取和主题相关的关键信息。

    这一步很重要 — 网页内容很长，但我们需要的只是其中几句话。
    """
    results = []

    for i, page in enumerate(pages):
        print(f"  📝 提取重点 [{i+1}/{len(pages)}]: {page['title'][:50]}...")

        prompt = f"""请从以下网页内容中，提取和"{topic}"相关的关键信息。

网页标题：{page['title']}
网页内容：
{page['content'][:3000]}

要求：
1. 提取 3-5 个关键要点
2. 每个要点用一句话概括
3. 只提取和主题相关的内容
4. 忽略广告、导航等无关内容

返回 JSON 格式：
{{"key_points": ["要点1", "要点2", "要点3"], "relevance": "high/medium/low"}}
"""

        result = call_llm_json(
            prompt,
            system="You are a research assistant. Extract key points from web content. Return only valid JSON.",
        )

        if isinstance(result, dict) and "key_points" in result:
            results.append({
                "title": page["title"],
                "url": page["url"],
                "key_points": result["key_points"],
                "relevance": result.get("relevance", "unknown"),
            })
        else:
            # 提取失败，用摘要代替
            results.append({
                "title": page["title"],
                "url": page["url"],
                "key_points": [page.get("snippet", "无法提取")],
                "relevance": "unknown",
            })

    return results


# ============================================================
# Step 5: 生成最终报告
# ============================================================

def generate_report(topic: str, extractions: list[dict]) -> str:
    """
    汇总所有提取的重点，生成最终调研报告。
    """
    # 拼装参考资料
    sources_text = ""
    for ext in extractions:
        points = "\n".join(f"  - {p}" for p in ext["key_points"])
        sources_text += f"\n来源：{ext['title']}\n链接：{ext['url']}\n相关度：{ext['relevance']}\n要点：\n{points}\n"

    prompt = f"""请根据以下调研资料，写一份关于"{topic}"的调研报告。

调研资料：
{sources_text}

报告格式要求：
1. 标题：# {topic} 调研报告
2. 简介：一两句话说明主题
3. 核心发现：列出 3-5 个最重要的发现
4. 详细内容：分点展开说明
5. 来源：列出参考的网页链接
6. 总结：一段话概括

用中文写，保持客观，不要编造信息。
"""

    return call_llm(
        prompt,
        system="You are a research report writer. Write clear, well-structured reports in Chinese.",
        max_tokens=3000,
    )


# ============================================================
# 完整 Pipeline
# ============================================================

def run_research(topic: str) -> str:
    """
    执行完整的调研流程。

    这就是 Agent 的"多步骤规划"。
    每一步都是独立的函数，可以单独测试和替换。
    """
    print(f"\n{'='*60}")
    print(f"开始调研: {topic}")
    print(f"{'='*60}")

    # Step 1: 生成关键词
    print("\n📌 Step 1/5: 生成搜索关键词...")
    keywords = generate_keywords(topic)
    print(f"  关键词: {keywords}")

    # Step 2: 搜索
    print("\n📌 Step 2/5: 搜索网页...")
    search_results = search_multiple_keywords(keywords)
    print(f"  找到 {len(search_results)} 个结果（已去重）")

    if not search_results:
        return "搜索没有找到相关结果，请换个关键词试试。"

    # Step 3: 抓取内容
    print("\n📌 Step 3/5: 抓取网页内容...")
    pages = fetch_pages(search_results, max_pages=5)
    print(f"  成功抓取 {len(pages)} 个网页")

    if not pages:
        return "所有网页都抓取失败了，请检查网络连接。"

    # Step 4: 提取重点
    print("\n📌 Step 4/5: 提取关键信息...")
    extractions = extract_key_points(pages, topic)

    # Step 5: 生成报告
    print("\n📌 Step 5/5: 生成调研报告...")
    report = generate_report(topic, extractions)

    print(f"\n{'='*60}")
    print("调研完成！")
    print(f"{'='*60}")

    return report
