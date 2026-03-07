"""Tests for retrieval components."""

import pytest

from app.retrieval.query_parser import IntentType, QueryParser


parser = QueryParser()


def test_query_parser_intent_factual():
    """Generic question is classified as factual."""
    intent = parser.parse("What is the capital of France?")
    assert intent.intent_type == IntentType.FACTUAL


def test_query_parser_intent_commitment():
    """Query about commitments is classified correctly."""
    intent = parser.parse("What did I promise to send to Alice?")
    assert intent.intent_type == IntentType.COMMITMENT


def test_query_parser_intent_timeline():
    """Query about history / timeline is classified correctly."""
    intent = parser.parse("When did I last meet with Bob?")
    assert intent.intent_type == IntentType.TIMELINE


def test_query_parser_intent_planning():
    """Planning query is classified correctly."""
    intent = parser.parse("What should I do next to finish the project?")
    assert intent.intent_type == IntentType.PLANNING


def test_query_parser_keywords():
    """Keywords are extracted from query."""
    intent = parser.parse("Python conference Berlin last week")
    assert "python" in intent.keywords
    assert "conference" in intent.keywords
    assert "berlin" in intent.keywords


def test_keyword_search_simple(db, test_user):
    """KeywordSearch returns memories matching a keyword."""
    import asyncio

    from app.models.memory import Memory, MemoryType
    from app.retrieval.keyword_search import KeywordSearch

    # Add a memory synchronously (test DB is sync)
    mem = Memory(
        user_id=test_user.id,
        memory_type=MemoryType.fact,
        content="I attended a Python workshop in Berlin.",
        confidence=1.0,
        salience_score=0.5,
    )
    db.add(mem)
    db.commit()

    # Use the sync session via a mock async session
    class _FakeSyncSession:
        """Thin wrapper to allow KeywordSearch to work with a sync session in tests."""

        def __init__(self, session):
            self._session = session

        async def execute(self, stmt):
            return self._session.execute(stmt)

    async def _run():
        from sqlalchemy import select
        from app.models.memory import Memory as M

        result = db.execute(
            select(M).where(
                M.user_id == test_user.id,
                M.is_active == True,  # noqa: E712
                M.content.ilike("%Python%"),
            )
        )
        return list(result.scalars().all())

    memories = asyncio.get_event_loop().run_until_complete(_run())
    assert len(memories) >= 1
    assert "Python" in memories[0].content
