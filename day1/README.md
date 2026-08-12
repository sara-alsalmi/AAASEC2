# Day 1 — Enterprise Research Agent with LangGraph

## Overview

This lab implements a single autonomous research agent using [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview). The agent accepts a topic, collects information from the web, stores it in vector memory, analyzes it using a language model, and iteratively refines its research until a quality threshold is met before generating a final report.

The implemented system (`my_agent.py`) follows this pipeline:

```
START → collect → store_memory → analyze → evaluate
           ↑                                  │
           └── quality < 7 (max 3 tries) ─────┤
                                              └ quality >= 7
                                                    ↓
                                       report → audit → END
```

## Implementation Summary

The agent was built step-by-step through the following components:

**State (`AgentState`)** — A `TypedDict` representing the shared state across all nodes. `execution_logs` uses an `operator.add` reducer so each node appends its log entries rather than overwriting them.

**Nodes:**
- `collect_node` — Queries the web via Tavily. The search query is varied on each retry to avoid receiving identical results in repeated iterations.
- `store_memory_node` — Saves collected source text into an `InMemoryVectorStore` with `DeterministicFakeEmbedding`, enabling retrieval-augmented generation (RAG) in subsequent iterations.
- `analyze_node` — For each source, retrieves related past content from the vector store and uses the LLM to produce a structured analysis covering relevance, key findings, and insights.
- `evaluate_node` — Scores overall research quality (1–10) using `llm.with_structured_output(QualityScore)`, ensuring a typed response rather than parsing free text.
- `report_node` — Generates a professional enterprise research report from all analyzed sources.
- `audit_node` — Records final workflow statistics (total iterations and quality score).

**Routing (`quality_router`)** — A conditional edge that routes back to `collect` if the quality score is below 7 and the iteration count is under 3; otherwise proceeds to `report`. Both conditions are required to guarantee termination.

**Compilation** — The graph is compiled with `InMemorySaver` as a checkpointer, enabling state persistence across nodes and support for time-travel debugging. The graph structure is visualized using `draw_mermaid()`.

## Files

| File | Description |
|---|---|
| `my_agent.py` | Complete agent implementation |
| `pyproject.toml` | Project dependencies managed by **uv** |
| `.env.example` | Template for API keys |

## Running the Agent

```bash
uv sync
cp .env.example .env   # add your OpenRouter key (and optionally Tavily key)

# Offline test — no API keys required
USE_FAKE=1 uv run python my_agent.py

# Full run with real LLM and web search
uv run python my_agent.py
```




