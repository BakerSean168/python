---
id: ai-agent-frameworks
title: AI Agent 框架对比练习
status: active
level: intermediate
language: python
created_at: 2026-06-07
updated_at: 2026-06-07
---

# AI Agent 框架对比练习

## Goal

用 3 个主流框架重写 Day 1-7 的核心项目，对比框架设计哲学、优缺点、适用场景。

## 框架对比

| 框架 | 定位 | 核心抽象 | 适合场景 |
|------|------|---------|---------|
| **LangChain** | 全能工具箱 | Chain（链） | 快速原型、RAG、工具调用 |
| **LangGraph** | 状态机编排 | Graph（图） | 复杂工作流、多 Agent、有状态任务 |
| **Pydantic AI** | 类型安全的 Agent | Agent + Tool | 生产级 Agent、强调类型安全 |

## 练习计划

| # | 项目 | LangChain | LangGraph | Pydantic AI |
|---|------|-----------|-----------|-------------|
| 1 | Tool Agent (Day 2) | ✅ LCEL + Tools | - | ✅ Agent + Tool |
| 2 | RAG (Day 3) | ✅ Retriever + Chain | - | - |
| 3 | Research Pipeline (Day 4) | - | ✅ StateGraph | - |
| 4 | Multi-Agent (Day 6) | - | ✅ Multi-agent Graph | - |
| 5 | 对比总结 | 设计哲学 | 状态管理 | 类型安全 |

## Current Focus

项目 1：用 LangChain 和 Pydantic AI 分别实现 Tool Agent（Day 2），对比手写版本。

## Session Log

### 2026-06-07 — 框架对比练习开始
- 完成 7 天手写 Agent 计划
- 开始框架对比：LangChain → LangGraph → Pydantic AI

## Next Step

用 LangChain 实现 Tool Agent，对比 Day 2 的手写版本。
