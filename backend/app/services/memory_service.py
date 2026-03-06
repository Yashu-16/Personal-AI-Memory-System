"""Memory service – CRUD and search operations on memories."""

import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory, MemoryType
from app.schemas.memory import MemoryCreate, MemoryUpdate


class MemoryService:
    """Application-level memory operations."""

    async def create_memory(
        self,
        user_id: uuid.UUID,
        memory_data: MemoryCreate,
        db: AsyncSession,
    ) -> Memory:
        """Create and persist a memory."""
        memory = Memory(
            user_id=user_id,
            memory_type=memory_data.memory_type,
            content=memory_data.content,
            summary=memory_data.summary,
            source_type=memory_data.source_type,
            source_ref=memory_data.source_ref,
            confidence=memory_data.confidence,
            salience_score=memory_data.salience_score,
        )
        db.add(memory)
        await db.flush()
        await db.refresh(memory)
        return memory

    async def get_memories(
        self,
        user_id: uuid.UUID,
        filters: Optional[dict[str, Any]],
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
    ) -> list[Memory]:
        """Return paginated memories with optional filters."""
        stmt = select(Memory).where(
            Memory.user_id == user_id,
            Memory.is_active == True,  # noqa: E712
        )
        if filters:
            if filters.get("memory_type"):
                stmt = stmt.where(Memory.memory_type == filters["memory_type"])
            if filters.get("source_type"):
                stmt = stmt.where(Memory.source_type == filters["source_type"])
        stmt = stmt.order_by(Memory.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_memory(
        self,
        memory_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> Optional[Memory]:
        """Return a single memory or None."""
        result = await db.execute(
            select(Memory).where(
                Memory.id == memory_id,
                Memory.user_id == user_id,
                Memory.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def update_memory(
        self,
        memory_id: uuid.UUID,
        user_id: uuid.UUID,
        update_data: MemoryUpdate,
        db: AsyncSession,
    ) -> Optional[Memory]:
        """Update a memory's fields."""
        memory = await self.get_memory(memory_id, user_id, db)
        if memory is None:
            return None
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(memory, field, value)
        await db.flush()
        await db.refresh(memory)
        return memory

    async def soft_delete_memory(
        self,
        memory_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> bool:
        """Soft-delete a memory. Returns True if deleted."""
        memory = await self.get_memory(memory_id, user_id, db)
        if memory is None:
            return False
        memory.is_active = False
        await db.flush()
        return True

    async def search_memories(
        self,
        user_id: uuid.UUID,
        query: str,
        db: AsyncSession,
        limit: int = 20,
    ) -> list[Memory]:
        """Keyword search over memory content."""
        from sqlalchemy import or_  # noqa: PLC0415

        keywords = query.lower().split()
        if not keywords:
            return []
        conditions = [Memory.content.ilike(f"%{kw}%") for kw in keywords]
        stmt = (
            select(Memory)
            .where(
                Memory.user_id == user_id,
                Memory.is_active == True,  # noqa: E712
                or_(*conditions),
            )
            .order_by(Memory.salience_score.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
