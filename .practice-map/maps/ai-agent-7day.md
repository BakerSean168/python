---
id: ai-agent-7day
title: AI Agent 7-Day Practice Plan
status: active
level: beginner
language: python
llm_provider: google_ai_studio
frameworks:
  - hand-written
  - openai-agents-sdk
  - langgraph
  - pydantic-ai
created_at: 2026-06-05
updated_at: 2026-06-05
---

# AI Agent 7-Day Practice Plan

## Goal

Build 7 small projects to learn core Agent skills. Compare 3 frameworks (OpenAI Agents SDK, LangGraph, Pydantic AI) by implementing the same project in different frameworks to feel the differences.

## Why

Agent frameworks change fast. The fundamentals don't. By building each project by hand first, then re-implementing in frameworks, you learn what the framework adds — and when it gets in the way.

## LLM Provider

Google AI Studio (free plan) — Gemini API.
SDK: `google-genai` (official Google GenAI Python SDK).

## Milestones

| # | Project | Core Skill | Framework Focus | Status |
|---|---------|-----------|----------------|--------|
| 1 | CLI Chatbot | LLM calls, conversation history | Hand-written (no framework) | **done** |
| 2 | Tool Agent | Tool/function calling | Hand-written → OpenAI Agents SDK | **active** |
| 3 | File Q&A (RAG) | Embedding, vector search, context injection | Hand-written → LangGraph | planned |
| 4 | Web Research Agent | Multi-step planning | LangGraph vs Pydantic AI | planned |
| 5 | Bug Fix Agent | Execute-observe-fix loop | OpenAI Agents SDK | planned |
| 6 | Multi-Agent Writing Team | Agent collaboration | LangGraph | planned |
| 7 | FastAPI Agent Service | Deployment, logging, API | Any framework | planned |

## Current Focus

Day 2: Tool Agent — add function calling. Model decides WHEN to call a tool, tool returns result, model continues.

## Exercises

### Day 1: CLI Chatbot (Hand-Written)

**Goal:** Understand that an Agent is just `LLM + instructions + tools + loop`.

**Task:**
1. Install `google-genai` SDK
2. Set up API key from Google AI Studio
3. Build a CLI chatbot that:
   - Reads user input in a loop
   - Sends messages to Gemini API
   - Maintains conversation history
   - Prints the response
4. Add a system instruction ("You are a helpful Python tutor")

**What good looks like:**
- `main.py` under 80 lines
- Conversation history persists across turns in the same session
- Clean exit on `quit` or `Ctrl+C`

**Key code patterns to learn:**
```python
# This is the skeleton — you fill it in
from google import genai

client = genai.Client(api_key="...")
history = []

while True:
    user_input = input("You: ")
    # append to history
    # call API
    # print response
    # append response to history
```

**After hand-written version, compare with:**
- (none for Day 1 — just feel the raw API)

---

### Day 2: Tool Agent (Hand-Written → OpenAI Agents SDK)

**Goal:** Understand function calling — the model decides WHEN to call a tool.

**Task:**
1. Build 3 mock tools: `get_weather`, `calculate`, `search_notes`
2. Hand-written version: use Gemini's function calling API directly
3. Then re-implement using OpenAI Agents SDK (with Gemini via compatibility layer)
4. Compare: what did the framework handle for you?

**Mock tools:**
```python
def get_weather(city: str) -> str:
    return f"Weather in {city}: 25°C, sunny"

def calculate(expression: str) -> str:
    return str(eval(expression))  # safe for practice

def search_notes(keyword: str) -> str:
    return f"Found 3 notes containing '{keyword}'"
```

---

### Day 3: RAG File Q&A (Hand-Written → LangGraph)

**Goal:** Learn chunking, embedding, vector search, context injection.

**Task:**
1. Read a local .txt or .md file
2. Split into chunks
3. Embed with Gemini embedding API
4. Store in ChromaDB (local, no server needed)
5. On user query: retrieve top-k chunks → inject into prompt → answer
6. Then re-implement the flow as a LangGraph state graph

**Key concepts:**
- Chunk size & overlap matter
- Embedding = turning text into a vector of numbers
- Vector search = find similar chunks by distance
- Context injection = put retrieved chunks into the prompt

---

### Day 4: Web Research Agent (LangGraph vs Pydantic AI)

**Goal:** Multi-step planning — plan → search → read → summarize.

**Task:**
1. LangGraph version: define nodes (plan, search, read, summarize) as a state graph
2. Pydantic AI version: same flow, different abstractions
3. Compare: state management, tool definition, error handling

---

### Day 5: Bug Fix Agent (OpenAI Agents SDK)

**Goal:** Execute-observe-fix loop — the Agent runs code, sees output, corrects itself.

**Task:**
1. Given a Python file with a bug + an error message
2. Agent reads code, proposes fix, runs tests, retries if failed
3. Max 5 iterations

---

### Day 6: Multi-Agent Team (LangGraph)

**Goal:** Role separation + passing intermediate results.

**Task:**
1. Researcher agent → finds info
2. Writer agent → drafts article from info
3. Reviewer agent → checks facts & structure
4. Writer revises based on feedback

---

### Day 7: FastAPI Agent Service (Deployment)

**Goal:** Wrap an Agent as an API with logging, error handling, auth.

**Task:**
1. `POST /chat` — send message, get response
2. `POST /research` — trigger research agent
3. Add API key auth, logging, timeout

---

## Session Log

### 2026-06-05 — Plan Created
- Set up 7-day practice map
- LLM provider: Google AI Studio (free plan, Gemini)
- Frameworks to compare: OpenAI Agents SDK, LangGraph, Pydantic AI
- User is a Python beginner
- Starting with Day 1: hand-written CLI chatbot

### 2026-06-06 — Day 1 Done
- Switched from Google AI Studio to OpenRouter (more models, OpenAI-compatible format)
- Built CLI chatbot with streaming, conversation history, error handling
- Learned: SSE streaming, .env config, uv package manager, len() vs __len__()
- Code reviewed twice, fixed bugs (printf typo, done flag, type annotations)

---

## Next Step

Day 1, Step 1: Install `google-genai` SDK, get API key, run a single API call to confirm it works.
