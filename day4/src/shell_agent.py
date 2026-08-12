"""
DAY 4 — Deep Agent with shell access.

READ FIRST:  ../00-deep-agent-shell.md
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend

load_dotenv()

WORK_DIR = Path(__file__).resolve().parent.parent / "work"

llm = ChatOpenAI(
    model="nvidia/nemotron-3-super-120b-a12b:free",
    temperature=0,
    base_url="https://openrouter.ai/api/v1",
)

SYSTEM_PROMPT = (
    "You are a Python coding assistant with shell access. "
    "Write files with your filesystem tools and run them with execute. "
    "If a command fails, read the error and fix your code."
)


def make_backend():
    """Return (backend, cleanup_fn). Runs on THIS machine."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    backend = LocalShellBackend(
        root_dir=str(WORK_DIR),
        virtual_mode=True,
        env={"PATH": os.environ["PATH"]},
    )
    return backend, lambda: None


CALCULATOR_TASK = (
    "1. Create calculator.py with add, sub, mul, div functions "
    "(div raises ZeroDivisionError on zero). "
    "2. Write test_calculator.py with pytest tests including the zero case. "
    "3. Run them with execute using `python -m pytest`; pip install pytest first if missing. "
    "4. Fix any failures until all tests are green. "
    "5. Report the final pytest output."
)

if __name__ == "__main__":
    backend, cleanup = make_backend()
    try:
        agent = create_deep_agent(
            model=llm,
            system_prompt=SYSTEM_PROMPT,
            backend=backend,
        )
        result = agent.invoke({"messages": [{"role": "user", "content": CALCULATOR_TASK}]})
        print(result["messages"][-1].content)
    finally:
        cleanup()
