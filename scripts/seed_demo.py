#!/usr/bin/env python3
"""
scripts/seed_demo.py
────────────────────────────────────────────────────────────────────────────
Seeds the running Memora API with rich demo data so you can immediately
explore the system without connecting any external services.

Requirements:
  pip install httpx

Usage:
  # Make sure the API is running first:
  #   make start          (Docker)  or
  #   make local-demo     (local SQLite mode)

  python scripts/seed_demo.py [--base-url http://localhost:8000]
"""

import argparse
import sys

try:
    import httpx
except ImportError:
    print("  httpx is required:  pip install httpx")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# Demo data
# ─────────────────────────────────────────────────────────────────────────────

DEMO_USER = {
    "email": "demo@example.com",
    "password": "Demo1234!",
    "full_name": "Alex Demo",
}

DEMO_MEMORIES = [
    {
        "content": (
            "Had a 1-on-1 with Sarah from the platform team. She mentioned that the new "
            "CI/CD pipeline rollout is blocked on the security review from DevSecOps. "
            "She'll follow up with Marcus by end of week."
        ),
        "source_type": "meeting",
        "metadata": {"participants": ["Sarah", "Marcus"], "project": "CI/CD"},
    },
    {
        "content": (
            "Committed to delivering the Q2 product roadmap presentation to the board on "
            "March 15. Need to include: revenue projections, top-3 feature priorities, "
            "headcount ask, and competitive landscape analysis."
        ),
        "source_type": "note",
        "metadata": {"deadline": "2024-03-15", "project": "Q2 Roadmap"},
    },
    {
        "content": (
            "Read through the LangChain docs on agents. Key insight: tool-calling agents "
            "are more reliable than ReAct-style string parsing. Plan to refactor the "
            "memory retrieval module to use structured tool calls instead of prompt-only."
        ),
        "source_type": "note",
        "metadata": {"topic": "ai/ml", "project": "Memory System"},
    },
    {
        "content": (
            "Gym session notes: starting a 12-week strength programme. "
            "Week 1 targets – squat: 80 kg, bench: 60 kg, deadlift: 100 kg. "
            "Training 4x per week (Mon/Tue/Thu/Fri)."
        ),
        "source_type": "note",
        "metadata": {"category": "health", "programme": "strength"},
    },
    {
        "content": (
            "Client call with Priya at Acme Corp. She confirmed they're ready to move "
            "forward with the enterprise contract – she needs the updated SoW and pricing "
            "by Friday.  Deal size approx $120k ARR. Assigned to Jordan on our end."
        ),
        "source_type": "meeting",
        "metadata": {"client": "Acme Corp", "owner": "Jordan", "deal_size": "$120k"},
    },
    {
        "content": (
            "Personal goal for 2024: read 24 books (2 per month). Currently on "
            "book 4 – 'Thinking in Systems' by Donella Meadows. Key concept so far: "
            "feedback loops and stocks vs. flows determine system behaviour."
        ),
        "source_type": "note",
        "metadata": {"category": "personal", "goal": "24 books 2024"},
    },
    {
        "content": (
            "Sprint retrospective: team agreed to reduce WIP limit from 6 to 4 items "
            "per developer. Velocity was down 20% last sprint due to context-switching. "
            "Starting Kanban-style swim lanes next sprint to make this visible."
        ),
        "source_type": "meeting",
        "metadata": {"team": "Engineering", "type": "retro"},
    },
    {
        "content": (
            "Idea for a startup: AI-powered personal finance coach that ingests bank "
            "statements, investment accounts, and spending history to give personalised "
            "weekly recommendations. MVP: simple CSV upload + GPT-4 analysis. "
            "Potential co-founder: David (ex-fintech)."
        ),
        "source_type": "note",
        "metadata": {"category": "ideas", "stage": "concept"},
    },
]

DEMO_QUERIES = [
    "What commitments do I have coming up?",
    "What are my key projects right now?",
    "What did I learn about AI this week?",
    "What are my fitness goals?",
]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _print_header(text: str) -> None:
    bar = "─" * (len(text) + 4)
    print(f"\n  ╭{bar}╮")
    print(f"  │  {text}  │")
    print(f"  ╰{bar}╯\n")


def _ok(msg: str) -> None:
    print(f"  ✅  {msg}")


def _info(msg: str) -> None:
    print(f"  ℹ️   {msg}")


def _warn(msg: str) -> None:
    print(f"  ⚠️   {msg}")


def _err(msg: str) -> None:
    print(f"  ❌  {msg}")


# ─────────────────────────────────────────────────────────────────────────────
# Seed functions
# ─────────────────────────────────────────────────────────────────────────────

def check_server(base_url: str, client: httpx.Client) -> bool:
    try:
        r = client.get(f"{base_url}/health", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def register_or_login(base_url: str, client: httpx.Client) -> str:
    """Return a valid access token for the demo user."""
    # Try register first
    r = client.post(f"{base_url}/api/auth/register", json=DEMO_USER)
    if r.status_code == 201:
        _ok(f"Registered demo user:  {DEMO_USER['email']}")
    elif r.status_code == 400:
        _info(f"Demo user already exists – logging in.")
    else:
        _warn(f"Register returned {r.status_code}: {r.text}")

    # Login (JSON body, not form data)
    r = client.post(
        f"{base_url}/api/auth/login",
        json={"email": DEMO_USER["email"], "password": DEMO_USER["password"]},
    )
    if r.status_code != 200:
        _err(f"Login failed ({r.status_code}): {r.text}")
        sys.exit(1)

    token = r.json()["access_token"]
    _ok("Login successful.")
    return token


def seed_memories(base_url: str, client: httpx.Client, token: str) -> int:
    headers = {"Authorization": f"Bearer {token}"}
    created = 0
    for mem in DEMO_MEMORIES:
        r = client.post(
            f"{base_url}/api/memories/",
            json=mem,
            headers=headers,
        )
        if r.status_code in (200, 201):
            created += 1
        else:
            _warn(f"Could not create memory ({r.status_code}): {r.text[:120]}")
    return created


def run_sample_queries(base_url: str, client: httpx.Client, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    for q in DEMO_QUERIES:
        r = client.post(
            f"{base_url}/api/query/",
            json={"query": q},
            headers=headers,
            timeout=30,
        )
        if r.status_code == 200:
            data = r.json()
            answer = data.get("answer", "(no answer field)")
            conf = data.get("confidence", 0)
            _ok(f"Q: {q}")
            print(f"       A: {answer[:200]}")
            print(f"       Confidence: {conf:.0%}")
        else:
            _warn(f"Query failed ({r.status_code}): {r.text[:120]}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Memora with demo data.")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the running Memora API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--skip-queries",
        action="store_true",
        help="Skip running the sample queries after seeding.",
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")

    _print_header("Memora Demo Data Seeder")

    with httpx.Client(timeout=15) as client:
        # 1. Health check
        if not check_server(base, client):
            _err(f"Cannot reach the API at {base}/health")
            print()
            print("  Make sure the server is running:")
            print("    Docker:     make start")
            print("    Local:      make local-demo")
            print()
            sys.exit(1)
        _ok(f"API is reachable at {base}")

        # 2. Auth
        token = register_or_login(base, client)

        # 3. Seed memories
        print()
        _info("Seeding demo memories…")
        n = seed_memories(base, client, token)
        _ok(f"Created {n}/{len(DEMO_MEMORIES)} memories.")

        # 4. Sample queries
        if not args.skip_queries:
            print()
            _info("Running sample natural-language queries…")
            run_sample_queries(base, client, token)

    _print_header("Done!")
    print(f"  Demo user credentials:")
    print(f"    Email:    {DEMO_USER['email']}")
    print(f"    Password: {DEMO_USER['password']}")
    print()
    print(f"  Explore the system:")
    print(f"    API Docs  → {base}/docs")
    print(f"    Frontend  → http://localhost:3000  (if running)")
    print()


if __name__ == "__main__":
    main()
