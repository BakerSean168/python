"""
计算器模块的测试用例。

运行: python -m pytest test_calculator.py -v
"""

from buggy_calculator import add, subtract, multiply, divide, average


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2
    assert subtract(0, 0) == 0


def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6
    assert multiply(0, 100) == 0


def test_divide():
    assert divide(10, 2) == 5
    assert divide(7, 2) == 3.5
    assert divide(0, 5) == 0


def test_divide_by_zero():
    """除以零应该抛出 ValueError"""
    try:
        divide(10, 0)
        assert False, "应该抛出异常"
    except ValueError:
        pass  # 预期行为


def test_average():
    assert average([1, 2, 3, 4, 5]) == 3.0
    assert average([10, 20]) == 15.0
    assert average([0]) == 0.0
