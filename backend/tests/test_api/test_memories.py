"""Tests for memories endpoints."""

import uuid

import pytest

from app.models.memory import Memory, MemoryType


def test_list_memories_empty(client, auth_headers):
    """A new user has no memories."""
    response = client.get("/api/memories/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_memory_via_service(client, auth_headers, db, test_user):
    """Directly create a memory and verify it appears in list endpoint."""
    mem = Memory(
        user_id=test_user.id,
        memory_type=MemoryType.fact,
        content="I met Alice at the conference.",
        confidence=0.9,
        salience_score=0.7,
    )
    db.add(mem)
    db.commit()

    response = client.get("/api/memories/", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["content"] == "I met Alice at the conference."


def test_get_memory_not_found(client, auth_headers):
    """Requesting a non-existent memory returns 404."""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/memories/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


def test_soft_delete_memory(client, auth_headers, db, test_user):
    """Deleting a memory sets is_active=False."""
    mem = Memory(
        user_id=test_user.id,
        memory_type=MemoryType.task,
        content="TODO: write unit tests",
        confidence=1.0,
        salience_score=0.5,
    )
    db.add(mem)
    db.commit()
    db.refresh(mem)

    response = client.delete(f"/api/memories/{mem.id}", headers=auth_headers)
    assert response.status_code == 204

    db.refresh(mem)
    assert mem.is_active is False
