"""Memory updater – find stale memories and update them."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory


class MemoryUpdater:
    """Utility for identifying and updating stale memories."""

    async def find_stale(
        self,
        user_id: uuid.UUID,
        days_threshold: int,
        db: AsyncSession,
    ) -> list[Memory]:
        """Return active memories older than *days_threshold* days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_threshold)
        result = await db.execute(
            select(Memory).where(
                Memory.user_id == user_id,
                Memory.is_active == True,  # noqa: E712
                Memory.is_archived == False,  # noqa: E712
                Memory.updated_at < cutoff,
            ).limit(100)
        )
        return list(result.scalars().all())

    async def update_from_context(
        self,
        memory_id: uuid.UUID,
        new_info: str,
        db: AsyncSession,
    ) -> Optional[Memory]:
        """Append *new_info* to an existing memory's content."""
        result = await db.execute(select(Memory).where(Memory.id == memory_id))
        memory = result.scalar_one_or_none()
        if memory is None:
            return None
        memory.content = f"{memory.content}\n\n[Updated] {new_info}"
        await db.flush()
        await db.refresh(memory)
        return memory


# Re-export Optional so the method annotation above resolves
from typing import Optional  # noqa: E402
