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
    student = os.getenv("STUDENT_NAME", "unknown")
    public_url = os.getenv("PUBLIC_URL", "http://localhost:8000")
    return {
        "protocolVersion": "1.0",
        "name": f"{student}-agent",
        "description": (
            "A research and analysis agent that can produce structured research briefs, "
            "perform code review, and answer analytical questions using web search and tools."
        ),
        "url": f"{public_url}/v1/responses",
        "version": "0.1.0",
        "capabilities": {"streaming": False},
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": [
            {
                "id": "research-brief",
                "name": "Research Brief",
                "description": "Write a one-page executive research brief on a technical topic with a fixed structure.",
                "tags": ["research", "analysis", "brief"],
            },
            {
                "id": "code-review-notes",
                "name": "Code Review Notes",
                "description": "Produce structured code review notes covering correctness, security, and readability.",
                "tags": ["code-review", "security", "analysis"],
            },
        ],
    }
