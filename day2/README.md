# Day 2 — Multi-Agent Research Team (Supervisor Pattern)

## Overview

This lab extends Day 1's single research agent into a coordinated multi-agent team using the **supervisor pattern** in LangGraph. A supervisor LLM dynamically decides which specialist agent acts next, enabling a more modular and scalable research pipeline.

```
             ┌──────────── supervisor ─────────────┐
             │       (LLM decides who's next)      │
    ┌────────┼───────────┬───────────┬─────────────┤
    ↓        ↓           ↓           ↓             ↓
 researcher  analyst    writer     critic       FINISH
    │        │           │           │             ↓
    └────────┴───────────┴───────────┘            END
         (every worker reports back to the supervisor)
```

## Implementation Summary

**State (`TeamState`)** — A shared blackboard where all agents read the full state but write only their own section. `research_notes` and `execution_logs` use `operator.add` reducers for append-only updates; `draft` uses plain overwrite so each revision replaces the previous one.

**Structured routing (`RouterDecision`)** — The supervisor's routing decision is produced via `llm.with_structured_output(RouterDecision)`, where `next_agent` is constrained to `Literal["researcher", "analyst", "writer", "critic", "FINISH"]`. This prevents the LLM from inventing non-existent agents.

**Personas** — Four distinct system prompts define each agent's scope and strict boundaries:
- `researcher` — searches the web via Tavily; does not analyze or interpret
- `analyst` — interprets research notes into structured insights; does not search
- `writer` — writes or revises the draft from the analysis; adds no new facts
- `critic` — reviews the draft and returns either `APPROVED` or `REVISE: <fixes>`; does not rewrite

**Supervisor node** — Builds a concise status summary of the blackboard (not the full content), invokes `supervisor_llm` for a routing decision, and enforces two hard guardrails:
- Turn cap: if `turn_count > MAX_TURNS` → force `FINISH`
- Revision cap: if `revision_count >= MAX_REVISIONS` and a draft exists → force `FINISH`

**Worker nodes** — Each node reads from the blackboard, acts in persona, and returns a partial state update. Only `researcher_node` has access to `search_tool` (tool scoping by design).

**Graph wiring** — Hub-and-spoke topology: `START → supervisor → [worker] → supervisor → … → END`. The routing function simply reads `state["next_agent"]`; all decision logic lives inside the supervisor node, not the edge.

**Compilation** — Graph compiled with `InMemorySaver`, visualized with `draw_mermaid()` (produces a star shape), and executed with `stream_mode="values"`.

## Files

| File | Description |
|---|---|
| `day2_lab_skeleton.py` | Complete multi-agent implementation |
| `pyproject.toml` | Project dependencies managed by **uv** |
| `.env.example` | Template for API keys |

## Running the Agent

```bash
uv sync
cp .env.example .env   # add your OpenRouter key (and optionally Tavily key)

# Offline test — no API keys required
USE_FAKE=1 uv run python day2_lab_skeleton.py

# Full run with real LLM and web search
uv run python day2_lab_skeleton.py
```
