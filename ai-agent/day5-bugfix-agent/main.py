"""
Day 5: Bug 修复 Agent

核心思想：
  Agent 不只是"想"，还要"做"。
  修改代码 → 运行测试 → 看结果 → 失败就再改 → 直到成功或用完重试次数。

这个模式叫 Reflection（反思）或 Self-Correction（自我修正）。
它是 Agent 区别于普通 LLM 的关键能力之一。

流程：
  1. 读取源代码和测试文件
  2. 运行测试，收集错误信息
  3. 把代码 + 错误信息发给 LLM，让它分析并给出修复
  4. 应用修复
  5. 再次运行测试
  6. 如果还有错误，回到第 3 步（最多重试 5 次）

Setup:
  uv add requests python-dotenv
  uv run python main.py examples/buggy_calculator.py examples/test_calculator.py
"""

import os
import sys
import json
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-120b:free"

MAX_ITERATIONS = 5


def call_llm(prompt: str, system: str = "You are a Python expert.") -> str:
    """调用 LLM"""
    if not api_key:
        return "Error: OPENROUTER_API_KEY not set"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=(10, 120))
        if r.status_code != 200:
            return f"API error: {r.status_code}"
        return r.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        return f"Network error: {e}"


def run_tests(test_file: str) -> tuple[bool, str]:
    """
    运行测试，返回 (是否通过, 输出信息)。

    用 subprocess 运行 pytest，捕获输出。
    这就是 Agent 的"观察"能力 — 它能看到自己行动的结果。
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr
        passed = result.returncode == 0
        return passed, output
    except subprocess.TimeoutExpired:
        return False, "测试超时（30 秒）"
    except Exception as e:
        return False, f"运行测试失败: {e}"


def extract_code_block(text: str) -> str | None:
    """
    从 LLM 响应中提取 Python 代码块。

    LLM 通常会在 ```python ... ``` 中返回代码。
    """
    if "```python" in text:
        start = text.index("```python") + 9
        end = text.index("```", start)
        return text[start:end].strip()
    elif "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        return text[start:end].strip()
    return None


def fix_code(source_file: str, test_file: str, test_output: str, iteration: int) -> str | None:
    """
    让 LLM 分析错误并给出修复方案。

    参数:
        source_file: 源代码文件路径
        test_file: 测试文件路径
        test_output: 测试运行的输出（包含错误信息）
        iteration: 当前是第几次尝试

    返回:
        修复后的代码，如果无法修复返回 None
    """
    # 读取当前代码
    with open(source_file, "r", encoding="utf-8") as f:
        current_code = f.read()

    # 读取测试代码
    with open(test_file, "r", encoding="utf-8") as f:
        test_code = f.read()

    prompt = f"""以下是一个 Python 模块和它的测试。测试失败了，请分析错误并修复代码。

这是第 {iteration} 次尝试修复。

=== 当前代码 ({source_file}) ===
```python
{current_code}
```

=== 测试代码 ({test_file}) ===
```python
{test_code}
```

=== 测试输出 ===
{test_output}

=== 要求 ===
1. 分析每个失败的测试，找出 root cause
2. 给出修复后的完整代码
3. 只修复 bug，不要改变正常的逻辑
4. 用 ```python ... ``` 包裹修复后的代码

请先分析错误原因，然后给出修复后的完整代码。
"""

    response = call_llm(
        prompt,
        system=(
            "You are a Python debugging expert. "
            "Analyze test failures, identify root causes, and provide fixed code. "
            "Always return the COMPLETE fixed file in a ```python code block."
        ),
    )

    return response


def apply_fix(source_file: str, new_code: str) -> bool:
    """
    把修复后的代码写入文件。

    先备份原文件（加 .bak 后缀），再写入新代码。
    """
    # 备份
    backup_file = source_file + ".bak"
    with open(source_file, "r", encoding="utf-8") as f:
        original = f.read()
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(original)

    # 写入修复后的代码
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(new_code)

    return True


def run_bugfix_loop(source_file: str, test_file: str):
    """
    Bug 修复的主循环。

    这就是 Agent 的 execute-observe-fix 循环。
    """
    print("=" * 60)
    print("Bug 修复 Agent")
    print("=" * 60)
    print(f"源代码: {source_file}")
    print(f"测试文件: {test_file}")
    print(f"最大重试: {MAX_ITERATIONS} 次")
    print("-" * 60)

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n🔄 第 {iteration} 次尝试...")

        # Step 1: 运行测试
        print("  📊 运行测试...")
        passed, output = run_tests(test_file)

        if passed:
            print("\n✅ 所有测试通过！修复成功！")
            print(f"  共尝试 {iteration} 次")
            return True

        # 显示测试失败信息（只显示关键部分）
        # 提取 FAILED 和 ERROR 行
        error_lines = [
            line for line in output.split("\n")
            if "FAILED" in line or "ERROR" in line or "assert" in line.lower() or "E " in line
        ]
        print(f"  ❌ 测试失败:")
        for line in error_lines[:10]:
            print(f"     {line.strip()}")

        # Step 2: 让 LLM 分析并修复
        print("  🧠 分析错误并生成修复...")
        response = fix_code(source_file, test_file, output, iteration)

        if not response:
            print("  ⚠️ LLM 没有返回有效响应")
            continue

        # Step 3: 提取修复后的代码
        new_code = extract_code_block(response)

        if not new_code:
            print("  ⚠️ 无法从响应中提取代码块")
            print("  LLM 的分析:")
            print(f"  {response[:300]}...")
            continue

        # Step 4: 应用修复
        print("  🔧 应用修复...")
        apply_fix(source_file, new_code)
        print("  已写入修复代码，备份保存在 .bak 文件")

    print(f"\n❌ {MAX_ITERATIONS} 次尝试后仍未修复")
    return False


# --- 主程序 ---
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python main.py <源代码文件> <测试文件>")
        print("示例: python main.py examples/buggy_calculator.py examples/test_calculator.py")
        sys.exit(1)

    source_file = sys.argv[1]
    test_file = sys.argv[2]

    if not os.path.exists(source_file):
        print(f"错误: 源代码文件不存在: {source_file}")
        sys.exit(1)
    if not os.path.exists(test_file):
        print(f"错误: 测试文件不存在: {test_file}")
        sys.exit(1)

    success = run_bugfix_loop(source_file, test_file)
    sys.exit(0 if success else 1)
