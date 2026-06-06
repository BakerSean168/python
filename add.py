import json
from openai import OpenAI 

client = OpenAI()

def add(a: float, b: float) -> float:
    return a + b

tools = [
    {
        "type": "function",
        "name": "add",
        "description": "Add two numbers and return the sum.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "The first number"
                },
                "b": {
                    "type": "number",
                    "description": "The second number"
                }
            },
            "required": ["a", "b"],
            "additionalProperties": False
        }
    }
]
