> [!info] related notes
> - 前置笔记: [[04-web-research-agent|网页调研 Agent]]
> - 后续笔记: [[06-multi-agent-writing-team|多 Agent 写作团队]]
> - 所属 MOC: [[learn-ai-agent-moc|学习 AI Agent MOC]]
> - 相关概念: [[reflection-pattern|Reflection 模式]]、[[self-correction|自我修正]]
> - 相关资源: [[open-router|OpenRouter]]

# Bug 修复 Agent — 执行-观察-修正循环

## 目标

实现一个能自我修正的 Bug 修复 Agent：**修改代码 → 运行测试 → 看结果 → 失败就再改 → 直到成功或用完重试次数。**

## 和前两天的区别

| | Day 4（Research Agent） | Day 5（Bugfix Agent） |
|---|---|---|
| 核心模式 | Pipeline（串行步骤） | Reflection（执行-观察-修正循环） |
| 步骤数 | 固定 5 步 | 动态（1-5 次迭代） |
| 关键能力 | 多步骤规划 | 看到自己的执行结果并自我修正 |
| 适用场景 | 信息收集、报告生成 | 代码修复、调试、迭代优化 |

## 前置条件

```bash
uv add requests python-dotenv pytest
uv run python main.py examples/buggy_calculator.py examples/test_calculator.py
```

项目结构：

```
day5-bugfix-agent/
├── main.py                      # Agent 主程序
├── examples/
│   ├── buggy_calculator.py      # 有 bug 的代码
│   └── test_calculator.py       # 测试用例
└── .env
```

## 核心理解：Reflection 模式

### 什么是 Reflection？

**Agent 能看到自己行动的结果，然后自我修正。**

这是 Agent 区别于普通 LLM 的关键能力：
- 普通 LLM：一次性回答，答错了也不知道
- Agent + Reflection：执行 → 观察结果 → 分析错误 → 修正 → 再执行

### 流程图

```
输入: 有 bug 的代码 + 测试文件
          ↓
┌─→ Step 1: 运行测试
│         ↓
│   测试通过？──→ 是 → 输出最终代码 ✅
│         ↓
│         否 → 收集错误信息
│         ↓
│   Step 2: LLM 分析错误，提出修复方案
│         ↓
│   Step 3: 应用修改
│         ↓
│   回到 Step 1 ─┘
│
└── 最多循环 5 次 → 仍然失败则放弃 ❌
```

### 和 Pipeline 的区别

| | Pipeline（Day 4） | Reflection（Day 5） |
|---|---|---|
| 步骤数 | 固定 | 动态（取决于何时成功） |
| 控制流 | 线性，A → B → C → D | 循环，A → B → C → A → B → C → ... |
| 终止条件 | 跑完所有步骤 | 测试通过 或 达到最大次数 |
| 数据传递 | 每步输出传给下一步 | 每轮的错误信息传给下一轮 |

## 完整代码

### 示例：有 Bug 的代码

> [!note]- 展开查看 buggy_calculator.py
> ```python
> """
> 一个有 bug 的计算器模块。
> 故意埋了 3 个 bug：
>   1. subtract 写成了加法
>   2. divide 没有处理除以零
>   3. average 里 =+ 写反了（应该是 +=）
> """
>
> def add(a, b):
>     return a + b
>
> def subtract(a, b):
>     # Bug 1: 减法写成了加法
>     return a + b
>
> def multiply(a, b):
>     return a * b
>
> def divide(a, b):
>     # Bug 2: 没有处理除以零
>     return a / b
>
> def average(numbers):
>     # Bug 3: =+ 写反了，应该是 +=
>     total = 0
>     for n in numbers:
>         total =+ n
>     return total / len(numbers)
> ```

### 示例：测试用例

> [!note]- 展开查看 test_calculator.py
> ```python
> from buggy_calculator import add, subtract, multiply, divide, average
>
> def test_add():
>     assert add(2, 3) == 5
>
> def test_subtract():
>     assert subtract(5, 3) == 2      # 会失败：返回 8 而不是 2
>     assert subtract(3, 5) == -2
>
> def test_multiply():
>     assert multiply(3, 4) == 12
>
> def test_divide():
>     assert divide(10, 2) == 5
>
> def test_divide_by_zero():
>     """除以零应该抛出 ValueError"""
>     try:
>         divide(10, 0)
>         assert False, "应该抛出异常"
>     except ValueError:
>         pass
>
> def test_average():
>     assert average([1, 2, 3, 4, 5]) == 3.0  # 会失败：返回 1.0 而不是 3.0
> ```

### main.py — Agent 主程序

> [!note]- 展开查看 main.py
> ```python
> """
> Day 5: Bug 修复 Agent
> 修改代码 → 运行测试 → 看结果 → 失败就再改 → 直到成功或用完重试次数。
> """
>
> import os, sys, json, subprocess, requests
> from dotenv import load_dotenv
>
> load_dotenv()
> api_key = os.environ.get("OPENROUTER_API_KEY")
> API_URL = "https://openrouter.ai/api/v1/chat/completions"
> MODEL = "openai/gpt-oss-120b:free"
> MAX_ITERATIONS = 5
>
>
> def call_llm(prompt: str, system: str = "You are a Python expert.") -> str:
>     """调用 LLM"""
>     if not api_key:
>         return "Error: OPENROUTER_API_KEY not set"
>     headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
>     payload = {
>         "model": MODEL,
>         "messages": [
>             {"role": "system", "content": system},
>             {"role": "user", "content": prompt},
>         ],
>         "stream": False,
>     }
>     try:
>         r = requests.post(API_URL, headers=headers, json=payload, timeout=(10, 120))
>         if r.status_code != 200:
>             return f"API error: {r.status_code}"
>         return r.json()["choices"][0]["message"]["content"]
>     except requests.RequestException as e:
>         return f"Network error: {e}"
>
>
> def run_tests(test_file: str) -> tuple[bool, str]:
>     """
>     运行测试，返回 (是否通过, 输出信息)。
>     这就是 Agent 的"观察"能力 — 它能看到自己行动的结果。
>     """
>     try:
>         result = subprocess.run(
>             [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
>             capture_output=True, text=True, timeout=30,
>         )
>         return result.returncode == 0, result.stdout + result.stderr
>     except subprocess.TimeoutExpired:
>         return False, "测试超时（30 秒）"
>     except Exception as e:
>         return False, f"运行测试失败: {e}"
>
>
> def extract_code_block(text: str) -> str | None:
>     """从 LLM 响应中提取 Python 代码块。"""
>     if "```python" in text:
>         start = text.index("```python") + 9
>         end = text.index("```", start)
>         return text[start:end].strip()
>     elif "```" in text:
>         start = text.index("```") + 3
>         end = text.index("```", start)
>         return text[start:end].strip()
>     return None
>
>
> def fix_code(source_file: str, test_file: str, test_output: str, iteration: int) -> str:
>     """让 LLM 分析错误并给出修复方案。"""
>     with open(source_file, "r", encoding="utf-8") as f:
>         current_code = f.read()
>     with open(test_file, "r", encoding="utf-8") as f:
>         test_code = f.read()
>
>     prompt = f"""以下是一个 Python 模块和它的测试。测试失败了，请分析错误并修复代码。
> 这是第 {iteration} 次尝试修复。
>
> === 当前代码 ===
> ```python
> {current_code}
> ```
>
> === 测试代码 ===
> ```python
> {test_code}
> ```
>
> === 测试输出 ===
> {test_output}
>
> 要求：
> 1. 分析每个失败的测试，找出 root cause
> 2. 给出修复后的完整代码
> 3. 只修复 bug，不要改变正常的逻辑
> 4. 用 ```python ... ``` 包裹修复后的代码
> """
>     return call_llm(prompt, system=(
>         "You are a Python debugging expert. "
>         "Analyze test failures, identify root causes, and provide fixed code. "
>         "Always return the COMPLETE fixed file in a ```python code block."
>     ))
>
>
> def apply_fix(source_file: str, new_code: str) -> bool:
>     """把修复后的代码写入文件（先备份）。"""
>     with open(source_file, "r", encoding="utf-8") as f:
>         original = f.read()
>     with open(source_file + ".bak", "w", encoding="utf-8") as f:
>         f.write(original)
>     with open(source_file, "w", encoding="utf-8") as f:
>         f.write(new_code)
>     return True
>
>
> def run_bugfix_loop(source_file: str, test_file: str):
>     """Bug 修复的主循环 — execute-observe-fix。"""
>     print("=" * 60)
>     print("Bug 修复 Agent")
>     print(f"源代码: {source_file}")
>     print(f"测试文件: {test_file}")
>     print(f"最大重试: {MAX_ITERATIONS} 次")
>     print("-" * 60)
>
>     for iteration in range(1, MAX_ITERATIONS + 1):
>         print(f"\n🔄 第 {iteration} 次尝试...")
>
>         # Step 1: 运行测试
>         print("  📊 运行测试...")
>         passed, output = run_tests(test_file)
>
>         if passed:
>             print(f"\n✅ 所有测试通过！共尝试 {iteration} 次")
>             return True
>
>         # 显示错误
>         error_lines = [line for line in output.split("\n")
>                        if "FAILED" in line or "ERROR" in line or "assert" in line.lower() or "E " in line]
>         print(f"  ❌ 测试失败:")
>         for line in error_lines[:10]:
>             print(f"     {line.strip()}")
>
>         # Step 2: LLM 分析并修复
>         print("  🧠 分析错误并生成修复...")
>         response = fix_code(source_file, test_file, output, iteration)
>         if not response:
>             continue
>
>         # Step 3: 提取并应用修复
>         new_code = extract_code_block(response)
>         if not new_code:
>             print("  ⚠️ 无法从响应中提取代码块")
>             continue
>
>         print("  🔧 应用修复...")
>         apply_fix(source_file, new_code)
>
>     print(f"\n❌ {MAX_ITERATIONS} 次尝试后仍未修复")
>     return False
>
>
> if __name__ == "__main__":
>     if len(sys.argv) < 3:
>         print("用法: python main.py <源代码文件> <测试文件>")
>         sys.exit(1)
>     success = run_bugfix_loop(sys.argv[1], sys.argv[2])
>     sys.exit(0 if success else 1)
> ```

## 运行效果

```
============================================================
Bug 修复 Agent
============================================================
源代码: examples/buggy_calculator.py
测试文件: examples/test_calculator.py
最大重试: 5 次
------------------------------------------------------------

🔄 第 1 次尝试...
  📊 运行测试...
  ❌ 测试失败:
     examples/test_calculator.py::test_subtract FAILED
     assert subtract(5, 3) == 2
     E   assert 8 == 2
     examples/test_calculator.py::test_divide_by_zero FAILED
     ZeroDivisionError: division by zero
     examples/test_calculator.py::test_average FAILED
     assert 1.0 == 3.0
  🧠 分析错误并生成修复...
  🔧 应用修复...
  已写入修复代码，备份保存在 .bak 文件

🔄 第 2 次尝试...
  📊 运行测试...

✅ 所有测试通过！修复成功！
  共尝试 2 次
```

## 踩坑记录

### Agent 一次修了 3 个 Bug

LLM 的代码理解能力很强 — 它能同时处理多个错误，不需要一个一个修。第 1 轮看到了所有 3 个失败的测试，第 2 轮全部通过。

### `subprocess` 是关键

`run_tests()` 用 `subprocess` 运行 pytest，这实现了 Agent 的"观察"能力：
- 执行动作（运行测试）
- 看到结果（通过/失败 + 错误信息）
- 基于结果决策（修复/成功）

没有 `subprocess`，Agent 就无法"看到"自己行动的结果。

### 代码备份很重要

`apply_fix()` 会先备份原文件为 `.bak`。因为 LLM 可能把代码改坏，备份是安全网。

## 关键流程解析

### execute-observe-fix 循环

```
execute: apply_fix() → 写入修复后的代码
observe: run_tests() → 看到测试结果
fix:     fix_code()  → LLM 分析错误，生成新代码
```

这个循环是 Agent 最强大的模式。它让 Agent 不只是"一次性回答"，而是能迭代改进。

### 和 ReAct 模式的关系

这个循环本质上就是 ReAct（Reasoning + Acting）模式：
1. **Reason** — LLM 分析错误原因
2. **Act** — 应用修复代码
3. **Observe** — 运行测试看结果
4. 重复

### 最大重试次数的意义

`MAX_ITERATIONS = 5` 是一个安全阀：
- 防止 LLM 陷入死循环
- 防止 API 调用过多
- 强制在有限时间内给出结果

## 常见问题

1. **pytest 找不到**：`uv add pytest`
2. **测试超时**：`timeout=30` 可能太短，复杂测试需要更长时间
3. **LLM 改坏了代码**：`.bak` 文件是备份，可以恢复
4. **5 次都没修好**：可能是 bug 太隐蔽，或测试本身有问题
