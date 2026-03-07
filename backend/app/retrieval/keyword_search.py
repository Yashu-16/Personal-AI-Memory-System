"""Keyword-based memory search using PostgreSQL ILIKE."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory

if TYPE_CHECKING:
    pass


class KeywordSearch:
    """Simple keyword search against memory content."""

    async def search(
        self,
        user_id: uuid.UUID,
        query: str,
        db: AsyncSession,
        limit: int = 20,
    ) -> list[Memory]:
        """Return memories whose content contains any keyword in *query*."""
        keywords = [kw.strip() for kw in query.split() if len(kw.strip()) >= 3]
        if not keywords:
            # Fallback: return recent memories
            stmt = (
                select(Memory)
                .where(Memory.user_id == user_id, Memory.is_active == True)  # noqa: E712
                .order_by(Memory.created_at.desc())
                .limit(limit)
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())

        from sqlalchemy import or_  # noqa: PLC0415

        conditions = [Memory.content.ilike(f"%{kw}%") for kw in keywords]
        stmt = (
            select(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.is_active == True,  # noqa: E712
                or_(*conditions),
            )
            .order_by(Memory.salience_score.desc(), Memory.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
