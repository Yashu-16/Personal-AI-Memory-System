"""Vector similarity search using pgvector."""

import json
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory

logger = logging.getLogger(__name__)


class VectorSearch:
    """Perform cosine-similarity search with pgvector."""

    async def search(
        self,
        user_id: uuid.UUID,
        query_embedding: list[float],
        db: AsyncSession,
        top_k: int = 50,
    ) -> list[Memory]:
        """Return the *top_k* most similar memories by cosine distance."""
        try:
            from pgvector.sqlalchemy import Vector  # type: ignore
            from sqlalchemy import select, text  # noqa: PLC0415

            embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
            stmt = text(
                """
                SELECT id FROM memories
                WHERE user_id = :user_id AND is_active = true
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
                """
            )
            result = await db.execute(
                stmt,
                {"user_id": str(user_id), "embedding": embedding_str, "top_k": top_k},
            )
            ids = [row[0] for row in result.fetchall()]
            if not ids:
                return []

            memories_result = await db.execute(
                select(Memory).where(Memory.id.in_(ids))
            )
            return list(memories_result.scalars().all())
        except Exception as exc:
            logger.debug("Vector search unavailable, falling back: %s", exc)
            return []
