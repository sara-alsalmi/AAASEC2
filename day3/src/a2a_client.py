"""
A2A discovery + delegation client.

Usage:
    uv run python src/a2a_client.py http://<peer> "task for their agent"
"""

import sys
import httpx


def discover(peer_base_url: str) -> dict:
    """Fetch the agent card and print name + skills."""
    url = peer_base_url.rstrip("/") + "/.well-known/agent-card.json"
    card = httpx.get(url, timeout=10).raise_for_status().json()
    print(f"Agent : {card['name']}")
    print(f"URL   : {card['url']}")
    print("Skills:")
    for skill in card.get("skills", []):
        print(f"  - {skill['name']}: {skill['description']}")
    return card


def delegate(card: dict, task: str) -> str:
    """POST task to the endpoint from the card — never hardcode the URL."""
    endpoint = card["url"]  # read from card; that indirection IS the protocol
    resp = httpx.post(endpoint, json={"input": task}, timeout=300).raise_for_status().json()
    return resp["output"][0]["content"][0]["text"]


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python src/a2a_client.py <peer_base_url> <task>")
        sys.exit(1)

    peer_url, task = sys.argv[1], sys.argv[2]
    card = discover(peer_url)
    print("\nDelegating task...")
    result = delegate(card, task)
    print("\n=== AGENT REPLY ===")
    print(result)
