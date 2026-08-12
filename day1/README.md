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

## Using uv

[uv](https://docs.astral.sh/uv/) replaces pip + venv + pip-tools in one fast tool. The commands you need today:

```bash
uv sync                        # create/update .venv from pyproject.toml + uv.lock
uv run python script.py        # run anything inside the project venv (no activate needed)
uv run jupyter lab             # same, for Jupyter
uv add <package>               # add a dependency (updates pyproject.toml + lockfile)
uv sync --group embeddings     # optional: local HuggingFace embeddings for the RAG bonus
                               # (≈500 MB download — only if you want the bonus)
```

Never `pip install` into this project directly — always `uv add`, so `pyproject.toml` and `uv.lock` stay the single source of truth and everyone in the room has identical environments.

## Windows users: use WSL

Everything in this course assumes a Linux shell. On Windows, use **WSL 2 (Ubuntu)** — do not fight PowerShell.

1. Open **PowerShell as Administrator** and run:
   ```powershell
   wsl --install
   ```
   Reboot when asked, then create your Ubuntu username/password.
2. Open the **Ubuntu** app (or Windows Terminal → Ubuntu tab). You are now in Linux.
3. Install uv **inside Ubuntu** (the Linux command above, not the Windows installer):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc
   ```
4. Clone/copy this repo **into the Linux filesystem** (e.g. `~/labs/`), not `/mnt/c/...` — the Windows-mounted drives are painfully slow for `.venv` folders.
5. VS Code users: install the **"WSL"** extension, then `code .` from the Ubuntu terminal opens the project natively.
6. Jupyter started with `uv run jupyter lab` inside WSL prints a `http://localhost:8888/...` link — it opens fine in your normal Windows browser.

## OpenRouter setup (your LLM provider for this course)

We use [OpenRouter](https://openrouter.ai) because it gives you **free frontier-class models behind an OpenAI-compatible API** — same `ChatOpenAI` class, just a different `base_url` and model name. No credit card needed for the `:free` models.

**1. Create an account and key**

1. Sign up at <https://openrouter.ai> (Google/GitHub login works).
2. Go to <https://openrouter.ai/keys> → **Create Key**. It starts with `sk-or-`.
3. In <https://openrouter.ai/settings/privacy>, make sure free-model usage is allowed (free endpoints may log prompts — that's the trade; **don't paste anything sensitive**).

**2. Put the key in `.env`**

```bash
cp .env.example .env
# then edit .env:
OPENAI_API_KEY=sk-or-your-key-here
```

Yes, the variable is named `OPENAI_API_KEY` — `ChatOpenAI` reads it automatically; the code only overrides `base_url`:

```python
llm = ChatOpenAI(
    model="nvidia/nemotron-3-super-120b-a12b:free",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
)
```

**3. Models to use** (the `:free` suffix is **required** — without it you'll be billed):

| Model | When |
|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | default — use this |
| `nvidia/nemotron-3-nano-30b-a3b:free` | fallback when rate-limited |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | biggest, often congested |

Full list: <https://openrouter.ai/collections/free-models>

**4. Verify your key works** before starting the lab:

```bash
uv run python -c "
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model='nvidia/nemotron-3-nano-30b-a3b:free', base_url='https://openrouter.ai/api/v1')
print(llm.invoke('Say OK').content)"
```

**5. Know the limits.** Free models allow roughly 20 requests/min plus a small daily cap. This lab makes 5–10 LLM calls per run, so you have plenty — but don't run the graph in a tight loop. If you hit **HTTP 429**: wait a minute, or switch to the nano model. If `with_structured_output()` errors on a free model, try another `:free` model or pass `method="json_schema"`.

**6. No embeddings on OpenRouter.** For the RAG bonus, use local HuggingFace embeddings (`uv sync --group embeddings`) — the solution falls back to deterministic fake embeddings automatically if they're not installed.

## Other keys

- `TAVILY_API_KEY` — web search, free tier at <https://tavily.com>.
- No keys at all? `USE_FAKE=1` runs the whole graph offline with deterministic fakes — you still see the retry loop fire.

`.env` is git-ignored. **Never commit keys.** If a key ever lands in a commit, revoke it immediately — deleting the commit is not enough.

## Version-control your work with git

You are expected to commit as you go — one commit per completed step is a good rhythm. This is how real agent development works, and it lets the instructors see your process, not just your endpoint.

**Important — notebooks and git don't mix well.** `.ipynb` files are JSON blobs full of outputs and cell IDs; their diffs are unreadable and they merge badly. So:

- **Do the lab in the notebook** if you like, but **keep the `.py` version as your committed artifact.** After each step, export your notebook and commit the script:
  ```bash
  uv run jupyter nbconvert --to script day1_lab_skeleton.ipynb --output my_agent
  git add my_agent.py
  git commit -m "Step 5: quality router with iteration cap"
  ```
- Or simply work directly in `day1_lab_skeleton.py` (copy it to `my_agent.py` first) and skip the export step.
- If you insist on committing the notebook, clear outputs first: `uv run jupyter nbconvert --clear-output --inplace <notebook>.ipynb`.

Minimal daily workflow:

```bash
git status                        # what changed?
git add my_agent.py               # stage the .py, not the .ipynb
git commit -m "Step 3: structured output evaluator"
git log --oneline                 # your progress trail
git diff                          # what did I just change?
```

By end of day your `git log --oneline` should read like the lab's step list. That log is part of your deliverable.

## Self-check before opening the solution

- [ ] My nodes return partial dicts, never the whole mutated state
- [ ] `execution_logs` uses a reducer, and I can explain why
- [ ] My router has BOTH a quality exit AND an iteration cap
- [ ] Retried searches use a different query than the first attempt
- [ ] I saw the Mermaid diagram and it matches the intended flow
- [ ] I know what `GraphRecursionError` is and how to trigger it
- [ ] The quality score comes from `with_structured_output`, not `int()`

## 📱 WhatsApp group

Join the course WhatsApp group for announcements, Q&A, and sharing your Mermaid diagrams:

<!-- TODO: replace with the real QR image and invite link -->
![WhatsApp group QR](assets/whatsapp_qr.png)

Invite link: _(to be added)_
