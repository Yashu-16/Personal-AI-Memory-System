"""Retrieval engine – orchestrates keyword search, vector search, and ranking."""

import logging
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory, MemoryType
from app.retrieval.filters import MemoryFilters
from app.retrieval.keyword_search import KeywordSearch
from app.retrieval.query_parser import IntentType, QueryParser
from app.retrieval.ranking import Ranker
from app.retrieval.vector_search import VectorSearch

logger = logging.getLogger(__name__)


class RetrievalEngine:
    """Orchestrate keyword + vector search with ranking."""

    def __init__(self) -> None:
        self._parser = QueryParser()
        self._keyword_search = KeywordSearch()
        self._vector_search = VectorSearch()
        self._ranker = Ranker()
        self._filters = MemoryFilters()

    async def search(
        self,
        user_id: uuid.UUID,
        query: str,
        db: AsyncSession,
        filters: Optional[dict[str, Any]] = None,
        limit: int = 20,
    ) -> list[Memory]:
        """Return ranked memories relevant to *query*."""
        intent = self._parser.parse(query)
        filters = filters or {}

        # Keyword search
        keyword_results = await self._keyword_search.search(
            user_id=user_id, query=query, db=db, limit=limit * 2
        )

        # Vector search (best-effort)
        vector_results: list[Memory] = []
        try:
            from app.utils.embeddings import EmbeddingService  # noqa: PLC0415

            svc = EmbeddingService()
            embedding = await svc.get_embedding(query)
            vector_results = await self._vector_search.search(
                user_id=user_id, query_embedding=embedding, db=db, top_k=limit * 2
            )
        except Exception as exc:
            logger.debug("Vector search skipped: %s", exc)

        # Merge and deduplicate
        seen: set[uuid.UUID] = set()
        merged: list[Memory] = []
        for mem in keyword_results + vector_results:
            if mem.id not in seen:
                seen.add(mem.id)
                merged.append(mem)

        # Rank and truncate
        ranked = self._ranker.rank(merged, query)
        return ranked[:limit]
