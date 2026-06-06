"""
工具函数定义。

每个工具有两个部分：
1. 函数本身（Python 代码，真正执行逻辑）
2. 工具描述（JSON schema，告诉模型这个工具能做什么、需要什么参数）

模型靠"工具描述"来决定什么时候调用哪个工具。
所以描述写得好不好，直接影响模型的判断。
"""

# ============================================================
# 工具函数（真正执行的代码）
# ============================================================


def get_weather(city: str) -> str:
    """获取天气（模拟数据，实际项目会调用天气 API）"""
    # 模拟数据 — 不同城市返回不同结果
    mock_data = {
        "东京": "25°C，晴天，湿度 60%",
        "北京": "18°C，多云，空气质量 良",
        "上海": "22°C，小雨，记得带伞",
        "new york": "15°C，cloudy, wind 12mph",
        "london": "12°C，rainy, bring an umbrella",
    }
    city_lower = city.lower().strip()
    if city_lower in mock_data:
        return f"{city}的天气：{mock_data[city_lower]}"
    return f"{city}的天气数据暂不可用（这是模拟数据，只支持几个城市）"


def calculate(expression: str) -> str:
    """计算数学表达式"""
    # 安全检查：只允许数字和基本运算符
    allowed = set("0123456789+-*/.() ")
    if not all(c in allowed for c in expression):
        return f"错误：表达式 '{expression}' 包含不允许的字符"
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误：{e}"


def search_notes(keyword: str) -> str:
    """搜索本地笔记（模拟数据）"""
    # 模拟笔记数据
    notes = [
        {"title": "Python 装饰器", "content": "装饰器是一个接收函数并返回函数的函数..."},
        {"title": "Git 常用命令", "content": "git add . && git commit -m 'msg' && git push"},
        {"title": "Docker 入门", "content": "docker build -t myapp . && docker run -p 8080:80 myapp"},
        {"title": "FastAPI 教程", "content": "用 @app.get('/path') 定义路由..."},
        {"title": "Python 虚拟环境", "content": "uv init 创建项目，uv add 添加依赖..."},
    ]
    results = []
    for note in notes:
        if keyword.lower() in note["title"].lower() or keyword.lower() in note["content"].lower():
            results.append(f"  [{note['title']}] {note['content']}")
    if results:
        return f"找到 {len(results)} 条相关笔记：\n" + "\n".join(results)
    return f"没有找到包含 '{keyword}' 的笔记"

def get_current_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    now = datetime.now()
    return f"当前时间是 {now.strftime('%Y-%m-%d %H:%M:%S')}"

# ============================================================
# 工具描述（JSON schema，告诉模型有哪些工具可用）
# ============================================================
#
# 这个列表会原样传给 API 的 tools 参数。
# 每个工具描述包含：
#   - type: 固定是 "function"
#   - function.name: 函数名（要和上面的 Python 函数名对应）
#   - function.description: 用自然语言描述这个工具做什么
#   - function.parameters: 参数的 JSON schema
#
# description 写得越清楚，模型越容易判断什么时候该调用。
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的当前天气信息。当用户询问天气时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如 '东京'、'北京'、'New York'",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式。支持加减乘除和括号。当用户需要计算时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 '2 + 3 * 4' 或 '(10 - 2) / 4'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "搜索本地笔记库。当用户想找笔记、回忆某个知识点时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词，例如 '装饰器'、'docker'",
                    }
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间。当用户询问当前时间时使用。",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    }
]

# 工具名 → 函数的映射
# 当模型说"我要调用 get_weather"时，我们用这个映射找到真正的 Python 函数
TOOL_MAP = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_notes": search_notes,
    "get_current_time": get_current_time,
}
