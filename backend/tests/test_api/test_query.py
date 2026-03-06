"""Tests for query endpoint."""

import pytest

from app.models.memory import Memory, MemoryType


def test_query_empty_memories(client, auth_headers):
    """Query with no memories returns a 'no memories' answer."""
    response = client.post(
        "/api/query/",
        json={"query": "What did I do yesterday?", "max_results": 5},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["confidence"] == 0.0
    assert data["supporting_memories"] == []


def test_query_with_memories(client, auth_headers, db, test_user):
    """Query against existing memories returns relevant results."""
    mem = Memory(
        user_id=test_user.id,
        memory_type=MemoryType.fact,
        content="I attended a Python conference in Berlin last week.",
        confidence=1.0,
        salience_score=0.8,
    )
    db.add(mem)
    db.commit()

    response = client.post(
        "/api/query/",
        json={"query": "Python conference", "max_results": 5},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["supporting_memories"]) >= 1
    assert data["confidence"] > 0
