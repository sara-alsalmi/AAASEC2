import os
import time
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from src.agent import build_agent

load_dotenv()

app = FastAPI(title="AAASEC2 Agent API")
agent = build_agent()  # built once at startup, not per request


class ResponseRequest(BaseModel):
    input: str
    model: str | None = None


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/v1/responses")
async def create_response(req: ResponseRequest):
    result = await agent.ainvoke({"messages": [{"role": "user", "content": req.input}]})
    text = result["messages"][-1].content
    model_name = req.model or os.getenv("MODEL", "nvidia/nemotron-3-super-120b-a12b:free")
    return {
        "id": f"resp_{uuid.uuid4().hex[:24]}",
        "object": "response",
        "created_at": int(time.time()),
        "status": "completed",
        "model": model_name,
        "output": [
            {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": text}],
            }
        ],
    }


@app.get("/.well-known/agent-card.json")
def agent_card():
    # filled properly in 09-a2a.md
    return {"todo": True}
