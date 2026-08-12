"""
DAY 4 — Authenticated MCP server.

READ FIRST:  ../02-mcp-auth.md
"""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth import StaticTokenVerifier, require_scopes

load_dotenv()

STUDENT_TOKEN = os.getenv("MCP_STUDENT_TOKEN", "student-secret-token")
ADMIN_TOKEN = os.getenv("MCP_ADMIN_TOKEN", "admin-secret-token")

verifier = StaticTokenVerifier(
    tokens={
        STUDENT_TOKEN: {"client_id": "student", "scopes": ["read:public"]},
        ADMIN_TOKEN: {"client_id": "admin", "scopes": ["read:public", "read:internal"]},
    }
)

mcp = FastMCP("Secure Tools", auth=verifier)


@mcp.tool
def get_server_time() -> str:
    """Return the current UTC time. Public tool — any valid token."""
    return datetime.now(timezone.utc).isoformat()


@mcp.tool(auth=require_scopes("read:internal"))
def get_internal_report() -> dict:
    """Return the quarterly financial report. Protected — requires read:internal scope."""
    return {
        "report": "Q2 2026 Financial Report",
        "months": [
            {"month": "April",  "revenue": 120000, "costs": 85000},
            {"month": "May",    "revenue": 135000, "costs": 90000},
            {"month": "June",   "revenue": 148000, "costs": 95000},
        ],
    }


@mcp.tool(auth=require_scopes("read:internal"))
def get_lab_inventory() -> dict:
    """Return current lab sensor readings. Protected — requires read:internal scope."""
    return {
        "lab": "AAASEC2 Research Lab",
        "sensors": [
            {"id": "S01", "location": "Room A", "temperature_c": 22.4, "humidity_pct": 45.2},
            {"id": "S02", "location": "Room B", "temperature_c": 24.1, "humidity_pct": 51.7},
            {"id": "S03", "location": "Server Room", "temperature_c": 18.9, "humidity_pct": 38.5},
            {"id": "S04", "location": "Room D", "temperature_c": 23.6, "humidity_pct": 47.0},
        ],
    }


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8002)
