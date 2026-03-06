"""Query service – answer natural language questions using memories."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.reasoning.engine import ReasoningEngine
from app.retrieval.engine import RetrievalEngine
from app.retrieval.query_parser import QueryParser
from app.schemas.memory import MemoryResponse
from app.schemas.query import QueryResponse


class QueryService:
    """Process natural language queries against the user's memory store."""

    def __init__(self) -> None:
        self._retrieval = RetrievalEngine()
        self._reasoning = ReasoningEngine()
        self._parser = QueryParser()

    async def process_query(
        self,
        user_id: uuid.UUID,
        query_text: str,
        db: AsyncSession,
        max_results: int = 10,
    ) -> QueryResponse:
        """Retrieve relevant memories, reason over them, and return an answer."""
        intent = self._parser.parse(query_text)

        memories = await self._retrieval.search(
            user_id=user_id,
            query=query_text,
            db=db,
            limit=max_results,
        )

        result = await self._reasoning.reason(
            query=query_text,
            memories=memories,
            intent=intent,
        )

        supporting = [
            MemoryResponse.model_validate(m) for m in result.supporting_memories
        ]

        return QueryResponse(
            answer=result.answer,
            supporting_memories=supporting,
            confidence=result.confidence,
            suggested_actions=result.suggested_actions,
            query_intent=intent.intent_type,
        )
