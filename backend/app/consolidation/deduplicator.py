"""Deduplicator – detect near-duplicate memories."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory


class Deduplicator:
    """Check whether a memory is too similar to an existing one."""

    _SIMILARITY_THRESHOLD = 0.85

    async def check_duplicate(
        self,
        content: str,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> tuple[bool, Optional[uuid.UUID]]:
        """Return (is_duplicate, existing_id).

        Uses simple Jaccard similarity on word sets as a lightweight proxy.
        """
        result = await db.execute(
            select(Memory.id, Memory.content).where(
                Memory.user_id == user_id,
                Memory.is_active == True,  # noqa: E712
            ).limit(200)
        )
        rows = result.fetchall()

        new_words = set(content.lower().split())

        for row_id, row_content in rows:
            if not row_content:
                continue
            existing_words = set(row_content.lower().split())
            if not new_words or not existing_words:
                continue
            intersection = new_words & existing_words
            union = new_words | existing_words
            similarity = len(intersection) / len(union)
            if similarity >= self._SIMILARITY_THRESHOLD:
                return True, row_id

        return False, None
