"""
API 测试脚本。

运行方式：
  1. 先启动服务: uv run uvicorn main:app --reload --port 8000
  2. 再运行测试: uv run python test_api.py
"""

import requests

BASE_URL = "http://localhost:8000"
API_KEY = "dev-key-change-in-production"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
}


def test_health():
    """测试健康检查"""
    print("=" * 50)
    print("测试: GET /health")
    r = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")
    print()


def test_chat():
    """测试聊天"""
    print("=" * 50)
    print("测试: POST /chat")
    r = requests.post(
        f"{BASE_URL}/chat",
        headers=headers,
        json={"message": "用一句话介绍 Python"},
    )
    print(f"状态码: {r.status_code}")
    data = r.json()
    print(f"回复: {data.get('reply', 'N/A')[:200]}")
    print()


def test_research():
    """测试调研"""
    print("=" * 50)
    print("测试: POST /research")
    r = requests.post(
        f"{BASE_URL}/research",
        headers=headers,
        json={"topic": "Python 虚拟环境"},
    )
    print(f"状态码: {r.status_code}")
    data = r.json()
    print(f"报告: {data.get('report', 'N/A')[:300]}...")
    print()


def test_auth():
    """测试认证失败"""
    print("=" * 50)
    print("测试: 认证失败（无 API Key）")
    r = requests.post(
        f"{BASE_URL}/chat",
        json={"message": "你好"},
    )
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")
    print()

    print("测试: 认证失败（错误的 API Key）")
    r = requests.post(
        f"{BASE_URL}/chat",
        headers={"X-API-Key": "wrong-key", "Content-Type": "application/json"},
        json={"message": "你好"},
    )
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")
    print()


if __name__ == "__main__":
    print("Agent API 测试")
    print(f"目标: {BASE_URL}")
    print()

    try:
        test_health()
        test_auth()
        test_chat()
        # test_research()  # 取消注释以测试调研（较慢）
    except requests.ConnectionError:
        print("错误: 无法连接到 API 服务")
        print("请先启动服务: uv run uvicorn main:app --reload --port 8000")
