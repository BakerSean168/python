> [!info] related notes
> - 前置笔记: [[03-rag-file-qa-agent|RAG 文件问答 Agent]]
> - 后续笔记: [[05-bugfix-agent|Bug 修复 Agent]]
> - 所属 MOC: [[learn-ai-agent-moc|学习 AI Agent MOC]]
> - 相关概念: [[pipeline-pattern|Pipeline 模式]]
> - 相关资源: [[open-router|OpenRouter]]

# 网页调研 Agent — 多步骤 Pipeline

## 目标

实现一个自动调研 Agent：输入研究主题，自动完成 **生成关键词 → 搜索网页 → 抓取内容 → 提取重点 → 生成报告** 的完整流程。

## 和前两天的区别

| | Day 3（RAG Agent） | Day 4（Research Agent） |
|---|---|---|
| 知识来源 | 本地文档（预先加载） | 互联网（实时搜索） |
| 核心能力 | embedding + 向量搜索 | 多步骤 Pipeline |
| 数据流向 | 检索 → 注入 prompt → 回答 | 搜索 → 抓取 → 提取 → 汇总 |
| 适用场景 | 文档问答 | 主动调研、信息收集 |

## 前置条件

```bash
uv add requests beautifulsoup4 python-dotenv
uv run python main.py
```

项目结构：

```
day4-research-agent/
├── main.py        # 入口，CLI 循环
├── pipeline.py    # 核心：5 步 Pipeline
├── search.py      # 网页搜索 + 抓取
├── llm.py         # LLM 调用封装（含 JSON 解析）
└── .env
```

## 核心理解：Pipeline 模式

### 什么是 Pipeline？

**每一步的输出是下一步的输入，串成一条链。**

```
用户: "Python 异步编程"
  ↓
Step 1: LLM 生成关键词 → ["python asyncio tutorial", "Python异步入门", ...]
  ↓
Step 2: DuckDuckGo 搜索 → [{title, url, snippet}, ...]
  ↓
Step 3: 抓取网页内容 → [{title, url, content}, ...]
  ↓
Step 4: LLM 提取重点 → [{title, url, key_points}, ...]
  ↓
Step 5: LLM 生成报告 → "## 调研报告\n..."
```

### Pipeline vs 简单聊天

| | 简单聊天（Day 1） | Pipeline（Day 4） |
|---|---|---|
| 步骤数 | 1（问 → 答） | 5（关键词 → 搜索 → 抓取 → 提取 → 报告） |
| 中间结果 | 无 | 每步都有，可检查、可调试 |
| 失败处理 | 整体失败 | 某步失败可跳过，继续执行 |
| 可扩展性 | 差 | 好（加一步只需加一个函数） |

### 为什么让 LLM 生成搜索关键词？

用户的提问方式 ≠ 搜索引擎的关键词。

```
用户问: "Python 异步编程怎么学"
LLM 生成: ["python asyncio tutorial", "Python async await 入门", "python concurrency guide"]
```

LLM 的价值之一：**把人类的自然语言转换成工具能理解的格式。**

## 完整代码

### llm.py — LLM 调用封装

> [!note]- 展开查看 llm.py
> ```python
> """
> LLM 调用模块。
> 封装 OpenRouter API 调用，提供简单的接口给 pipeline 使用。
> """
>
> import os
> import json
> import requests
> from dotenv import load_dotenv
>
> load_dotenv()
>
> api_key = os.environ.get("OPENROUTER_API_KEY")
> API_URL = "https://openrouter.ai/api/v1/chat/completions"
> MODEL = "openai/gpt-oss-120b:free"
>
>
> def call_llm(prompt: str, system: str = "You are a helpful assistant.", max_tokens: int = 2000) -> str:
>     """调用 LLM，返回文本响应。"""
>     if not api_key:
>         return "Error: OPENROUTER_API_KEY not set"
>
>     headers = {
>         "Authorization": f"Bearer {api_key}",
>         "Content-Type": "application/json",
>     }
>     payload = {
>         "model": MODEL,
>         "messages": [
>             {"role": "system", "content": system},
>             {"role": "user", "content": prompt},
>         ],
>         "max_tokens": max_tokens,
>         "stream": False,
>     }
>     try:
>         r = requests.post(API_URL, headers=headers, json=payload, timeout=(10, 120))
>         if r.status_code != 200:
>             return f"API error (HTTP {r.status_code}): {r.text[:200]}"
>         data = r.json()
>         return data["choices"][0]["message"]["content"]
>     except requests.RequestException as e:
>         return f"Network error: {e}"
>
>
> def call_llm_json(prompt: str, system: str = "You are a helpful assistant.") -> dict | list | None:
>     """
>     调用 LLM 并尝试解析返回的 JSON。
>     有些步骤需要结构化输出（如生成关键词列表）。
>     """
>     response = call_llm(prompt, system)
>
>     # 尝试直接解析
>     try:
>         return json.loads(response)
>     except json.JSONDecodeError:
>         pass
>
>     # 尝试从 ```json ... ``` 块中提取
>     if "```json" in response:
>         start = response.index("```json") + 7
>         end = response.index("```", start)
>         try:
>             return json.loads(response[start:end].strip())
>         except json.JSONDecodeError:
>             pass
>
>     # 尝试找 [ 或 { 开始的 JSON
>     for start_char, end_char in [("[", "]"), ("{", "}")]:
>         if start_char in response:
>             start = response.index(start_char)
>             end = response.rfind(end_char)
>             if end > start:
>                 try:
>                     return json.loads(response[start:end + 1])
>                 except json.JSONDecodeError:
>                     pass
>
>     return None
> ```

### search.py — 网页搜索和抓取

> [!note]- 展开查看 search.py
> ```python
> """
> 网页搜索和内容抓取模块。
> 用 DuckDuckGo 搜索（免费，不需要 API key）。
> """
>
> import requests
> from bs4 import BeautifulSoup
>
> SEARCH_URL = "https://html.duckduckgo.com/html/"
>
>
> def search_web(query: str, max_results: int = 5) -> list[dict]:
>     """用 DuckDuckGo 搜索网页。返回 [{title, url, snippet}, ...]"""
>     headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
>     try:
>         response = requests.post(SEARCH_URL, data={"q": query}, headers=headers, timeout=15)
>         response.raise_for_status()
>     except requests.RequestException as e:
>         print(f"  搜索失败: {e}")
>         return []
>
>     soup = BeautifulSoup(response.text, "html.parser")
>     results = []
>     for result in soup.select(".result"):
>         title_tag = result.select_one(".result__a")
>         snippet_tag = result.select_one(".result__snippet")
>         if not title_tag:
>             continue
>         title = title_tag.get_text(strip=True)
>         url = title_tag.get("href", "")
>         snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
>         if "duckduckgo.com" in url:
>             continue
>         results.append({"title": title, "url": url, "snippet": snippet})
>         if len(results) >= max_results:
>             break
>     return results
>
>
> def fetch_page(url: str, max_chars: int = 5000) -> str:
>     """抓取网页正文，返回纯文本。"""
>     headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
>     try:
>         response = requests.get(url, headers=headers, timeout=15)
>         response.raise_for_status()
>     except requests.RequestException as e:
>         return f"[抓取失败: {e}]"
>
>     soup = BeautifulSoup(response.text, "html.parser")
>     for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
>         tag.decompose()
>     text = soup.get_text(separator="\n", strip=True)
>     lines = [line for line in text.split("\n") if line.strip()]
>     text = "\n".join(lines)
>     if len(text) > max_chars:
>         text = text[:max_chars] + "\n...[内容已截断]"
>     return text
> ```

### pipeline.py — 5 步 Pipeline 核心

> [!note]- 展开查看 pipeline.py
> ```python
> """
> 调研流水线 (Pipeline)。
> 把多个步骤串起来，每一步的输出是下一步的输入。
> """
>
> from llm import call_llm, call_llm_json
> from search import search_web, fetch_page
>
>
> def generate_keywords(topic: str) -> list[str]:
>     """Step 1: 让 LLM 根据主题生成搜索关键词。"""
>     prompt = f"""请根据以下研究主题，生成 3-5 个搜索关键词。
> 主题：{topic}
> 要求：
> 1. 关键词要适合搜索引擎（简洁、精准）
> 2. 混合中英文关键词（英文结果通常更多更好）
> 3. 覆盖主题的不同方面
> 只返回 JSON 数组，例如：["python async await tutorial", "Python asyncio 入门"]
> """
>     result = call_llm_json(prompt, system="You are a search keyword generator. Return only valid JSON arrays.")
>     if isinstance(result, list) and all(isinstance(k, str) for k in result):
>         return result
>     print("  ⚠️ 关键词生成失败，使用主题作为搜索词")
>     return [topic]
>
>
> def search_multiple_keywords(keywords: list[str], results_per_keyword: int = 3) -> list[dict]:
>     """Step 2: 用多个关键词分别搜索，合并去重。"""
>     all_results = []
>     seen_urls = set()
>     for keyword in keywords:
>         print(f"  🔍 搜索: {keyword}")
>         results = search_web(keyword, max_results=results_per_keyword)
>         for r in results:
>             if r["url"] not in seen_urls:
>                 seen_urls.add(r["url"])
>                 all_results.append(r)
>     return all_results
>
>
> def fetch_pages(search_results: list[dict], max_pages: int = 5) -> list[dict]:
>     """Step 3: 抓取搜索结果的网页内容。"""
>     pages = []
>     for i, result in enumerate(search_results[:max_pages]):
>         print(f"  📄 抓取 [{i+1}/{min(len(search_results), max_pages)}]: {result['title'][:50]}...")
>         content = fetch_page(result["url"])
>         if content and not content.startswith("[抓取失败"):
>             pages.append({"title": result["title"], "url": result["url"], "content": content})
>     return pages
>
>
> def extract_key_points(pages: list[dict], topic: str) -> list[dict]:
>     """Step 4: 让 LLM 从每个网页中提取和主题相关的关键信息。"""
>     results = []
>     for i, page in enumerate(pages):
>         print(f"  📝 提取重点 [{i+1}/{len(pages)}]: {page['title'][:50]}...")
>         prompt = f"""请从以下网页内容中，提取和"{topic}"相关的关键信息。
> 网页标题：{page['title']}
> 网页内容：{page['content'][:3000]}
> 要求：提取 3-5 个关键要点，每个要点用一句话概括。
> 返回 JSON：{{"key_points": ["要点1", "要点2"], "relevance": "high/medium/low"}}
> """
>         result = call_llm_json(prompt, system="You are a research assistant. Return only valid JSON.")
>         if isinstance(result, dict) and "key_points" in result:
>             results.append({"title": page["title"], "url": page["url"],
>                            "key_points": result["key_points"], "relevance": result.get("relevance", "unknown")})
>         else:
>             results.append({"title": page["title"], "url": page["url"],
>                            "key_points": [page.get("snippet", "无法提取")], "relevance": "unknown"})
>     return results
>
>
> def generate_report(topic: str, extractions: list[dict]) -> str:
>     """Step 5: 汇总所有提取的重点，生成最终调研报告。"""
>     sources_text = ""
>     for ext in extractions:
>         points = "\n".join(f"  - {p}" for p in ext["key_points"])
>         sources_text += f"\n来源：{ext['title']}\n链接：{ext['url']}\n要点：\n{points}\n"
>     prompt = f"""请根据以下调研资料，写一份关于"{topic}"的调研报告。
> 调研资料：{sources_text}
> 报告格式：标题 → 简介 → 核心发现 → 详细内容 → 来源 → 总结
> 用中文写，保持客观。
> """
>     return call_llm(prompt, system="You are a research report writer.", max_tokens=3000)
>
>
> def run_research(topic: str) -> str:
>     """执行完整的 5 步调研流程。"""
>     print(f"\n{'='*60}")
>     print(f"开始调研: {topic}")
>
>     print("\n📌 Step 1/5: 生成搜索关键词...")
>     keywords = generate_keywords(topic)
>     print(f"  关键词: {keywords}")
>
>     print("\n📌 Step 2/5: 搜索网页...")
>     search_results = search_multiple_keywords(keywords)
>     print(f"  找到 {len(search_results)} 个结果（已去重）")
>     if not search_results:
>         return "搜索没有找到相关结果。"
>
>     print("\n📌 Step 3/5: 抓取网页内容...")
>     pages = fetch_pages(search_results, max_pages=5)
>     print(f"  成功抓取 {len(pages)} 个网页")
>     if not pages:
>         return "所有网页都抓取失败了。"
>
>     print("\n📌 Step 4/5: 提取关键信息...")
>     extractions = extract_key_points(pages, topic)
>
>     print("\n📌 Step 5/5: 生成调研报告...")
>     report = generate_report(topic, extractions)
>     return report
> ```

## 运行效果

```
研究主题: langChain和langGraph 的区别

📌 Step 1/5: 生成搜索关键词...
  关键词: ['LangChain vs LangGraph differences', 'LangChain 与 LangGraph 区别', ...]

📌 Step 2/5: 搜索网页...
  🔍 搜索: LangChain vs LangGraph differences
  🔍 搜索: LangChain 与 LangGraph 区别
  找到 14 个结果（已去重）

📌 Step 3/5: 抓取网页内容...
  📄 抓取 [1/5]: LangChain vs. LangGraph - GeeksforGeeks...
  📄 抓取 [2/5]: LangChain vs LangGraph vs LangSmith vs LangFlow...
  成功抓取 3 个网页

📌 Step 4/5: 提取关键信息...
  📝 提取重点 [1/3]: LangChain vs. LangGraph - GeeksforGeeks...

📌 Step 5/5: 生成调研报告...

# langChain和langGraph 的区别 调研报告
## 核心发现
1. 架构模型不同：LangChain 采用线性"链"结构，LangGraph 基于图模型...
2. 适用场景差异：LangChain 适合单轮工作流，LangGraph 更适合多代理协作...
```

## 踩坑记录

### 网页抓取有失败率

5 个搜索结果只成功抓取了 3 个。这是真实世界的常态：
- 有些网站防爬虫
- 有些页面加载超时
- 有些返回空内容

**关键教训：** 好的 Agent 能容忍局部失败，继续完成任务。代码用 `try/except` 优雅处理了失败，没有崩溃。

### `call_llm_json` 的 JSON 解析

LLM 返回的不一定是纯 JSON，可能前后有文字说明，或者用 ` ```json ``` ` 包裹。`call_llm_json` 函数尝试了 3 种解析策略：
1. 直接解析
2. 从 ` ```json ``` ` 块中提取
3. 找 `[` 或 `{` 开始的 JSON

这就是"和 LLM 交互的工程细节" — 模型的输出格式不可靠，需要防御性解析。

## 关键流程解析

### Pipeline 的本质

```
Pipeline = 一系列独立函数，串行执行，传递数据
```

每个函数：
- 有明确的输入类型
- 有明确的输出类型
- 可以单独测试
- 可以替换实现

这正是 LangGraph 等框架的底层思想。框架只是把这些函数画成图，加上条件分支和状态管理。

### 和 RAG 的对比

```
Day 3 (RAG):      本地文档 → 切块 → 向量搜索 → 注入 prompt → 回答
Day 4 (Pipeline): 互联网 → 搜索 → 抓取 → LLM 提取 → LLM 汇总
```

都是"先获取信息，再让 LLM 处理"，但知识来源和处理方式不同。

## 常见问题

1. **搜索没结果**：检查网络连接，或换个关键词试试
2. **抓取超时**：`timeout=15` 可能太短，复杂网页需要更长时间
3. **报告质量差**：可能是提取的重点不够好，检查 Step 4 的输出
4. **运行太慢**：要调 5 次 LLM + 抓网页，整个流程需要 1-2 分钟
