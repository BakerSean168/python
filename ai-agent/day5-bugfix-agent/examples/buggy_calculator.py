"""
一个有 bug 的计算器模块。

故意埋了 3 个 bug，让 Agent 来找并修复。
Bug 难度从明显到隐蔽。
"""


def add(a, b):
    """加法"""
    return a + b


def subtract(a, b):
    """减法"""
    # Fixed Bug 1: 正确实现减法
    return a - b


def multiply(a, b):
    """乘法"""
    return a * b


def divide(a, b):
    """除法"""
    # Fixed Bug 2: 处理除以零的情况，抛出 ValueError
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b


def average(numbers):
    """计算平均值"""
    # Fixed Bug 3: 正确累计求和
    total = 0
    for n in numbers:
        total += n  # 使用 += 而不是 =+
    return total / len(numbers)