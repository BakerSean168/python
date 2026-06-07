"""
网页搜索和内容抓取模块。

功能：
1. 用 DuckDuckGo 搜索（免费，不需要 API key）
2. 抓取网页内容
3. 从 HTML 中提取正文
"""

import requests
from bs4 import BeautifulSoup

# DuckDuckGo 搜索用的 URL
SEARCH_URL = "https://html.duckduckgo.com/html/"


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    用 DuckDuckGo 搜索网页。

    参数:
        query: 搜索关键词
        max_results: 最多返回几条结果

    返回:
        [{"title": "标题", "url": "链接", "snippet": "摘要"}, ...]
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.post(
            SEARCH_URL,
            data={"q": query},
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  搜索失败: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    # DuckDuckGo HTML 版的结果结构
    for result in soup.select(".result"):
        title_tag = result.select_one(".result__a")
        snippet_tag = result.select_one(".result__snippet")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        url = title_tag.get("href", "")
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

        # 过滤掉 DuckDuckGo 的重定向链接
        if "duckduckgo.com" in url:
            continue

        results.append({
            "title": title,
            "url": url,
            "snippet": snippet,
        })

        if len(results) >= max_results:
            break

    return results


def fetch_page(url: str, max_chars: int = 5000) -> str:
    """
    抓取网页正文。

    参数:
        url: 网页地址
        max_chars: 最多返回多少字符（防止网页太长）

    返回:
        网页正文的纯文本
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"[抓取失败: {e}]"

    # 解析 HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # 删除不需要的标签
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # 提取正文
    text = soup.get_text(separator="\n", strip=True)

    # 清理多余空行
    lines = [line for line in text.split("\n") if line.strip()]
    text = "\n".join(lines)

    # 截断
    if len(text) > max_chars:
        text = text[:max_chars] + "\n...[内容已截断]"

    return text
