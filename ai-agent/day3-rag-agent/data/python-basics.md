# Python 基础知识

## 变量和数据类型

Python 是动态类型语言，变量不需要声明类型。

```python
name = "Alice"      # 字符串 str
age = 25            # 整数 int
height = 1.75       # 浮点数 float
is_student = True   # 布尔值 bool
```

Python 有四种基本数据类型：str、int、float、bool。
可以用 `type()` 查看变量类型。

## 列表 (list)

列表是 Python 最常用的数据结构，用方括号定义。

```python
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")    # 添加元素
fruits.remove("banana")    # 删除元素
first = fruits[0]          # 索引从 0 开始
```

列表支持切片操作：`fruits[1:3]` 取第 2 到第 3 个元素。
`len(fruits)` 获取列表长度。

## 字典 (dict)

字典是键值对集合，用花括号定义。

```python
person = {
    "name": "Alice",
    "age": 25,
    "city": "Beijing"
}
print(person["name"])        # 通过键取值
person["email"] = "a@b.com"  # 添加新键值对
```

字典的键必须是不可变类型（str、int、tuple）。
用 `person.get("phone", "N/A")` 可以安全取值，键不存在时返回默认值。

## 函数

用 `def` 定义函数。

```python
def greet(name, greeting="Hello"):
    """问候函数"""
    return f"{greeting}, {name}!"

result = greet("Alice")                    # "Hello, Alice!"
result = greet("Bob", greeting="Hi")       # "Hi, Bob!"
```

函数可以有默认参数。用 `*args` 接收任意数量位置参数，用 `**kwargs` 接收任意数量关键字参数。

## 类和面向对象

```python
class Dog:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed

    def bark(self):
        return f"{self.name} says: Woof!"

my_dog = Dog("Buddy", "Golden Retriever")
print(my_dog.bark())  # "Buddy says: Woof!"
```

`__init__` 是构造函数，`self` 代表实例本身。
Python 支持继承：`class Puppy(Dog): ...`

## 装饰器

装饰器是一个接收函数并返回新函数的函数。用 `@` 语法使用。

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时 {time.time() - start:.2f} 秒")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "done"
```

装饰器常用于日志、权限检查、缓存、计时等场景。

## 异常处理

用 `try/except` 捕获异常。

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零")
except Exception as e:
    print(f"发生了错误: {e}")
else:
    print("没有错误")
finally:
    print("无论如何都会执行")
```

`finally` 块无论是否发生异常都会执行，常用于清理资源。

## 文件操作

```python
# 读文件
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 写文件
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, World!")

# 逐行读取
with open("data.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

`with` 语句会自动关闭文件。`encoding="utf-8"` 防止中文乱码。

## 列表推导式

```python
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

evens = [x for x in range(20) if x % 2 == 0]
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

列表推导式比 for 循环更简洁，但太复杂的逻辑应该用普通循环。

## 虚拟环境

Python 项目应该使用虚拟环境隔离依赖。

```bash
# 使用 uv（推荐）
uv init my-project
cd my-project
uv add requests
uv run python main.py

# 使用 venv（标准库）
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install requests
```

`uv` 比 `pip` 快 10-100 倍，是现代 Python 的推荐工具。
