"""Memory linker – link memories to entities and find related memories."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.extraction.entity_extractor import ExtractedEntity
from app.models.entity import Entity, EntityType, MemoryEntityLink
from app.models.memory import Memory


class MemoryLinker:
    """Create entity links for memories and find related memories."""

    async def link_entities(
        self,
        memory: Memory,
        entities: list[ExtractedEntity],
        db: AsyncSession,
    ) -> None:
        """Upsert entities and create MemoryEntityLink rows."""
        if not memory.id or not entities:
            return

        for extracted in entities:
            # Find or create entity
            result = await db.execute(
                select(Entity).where(
                    Entity.user_id == memory.user_id,
                    Entity.canonical_name == extracted.canonical_name,
                )
            )
            entity = result.scalar_one_or_none()
            if entity is None:
                entity = Entity(
                    user_id=memory.user_id,
                    entity_type=EntityType(extracted.entity_type.value),
                    name=extracted.name,
                    canonical_name=extracted.canonical_name,
                )
                db.add(entity)
                await db.flush()  # get entity.id

            # Avoid duplicate links
            link_result = await db.execute(
                select(MemoryEntityLink).where(
                    MemoryEntityLink.memory_id == memory.id,
                    MemoryEntityLink.entity_id == entity.id,
                )
            )
            if link_result.scalar_one_or_none() is None:
                link = MemoryEntityLink(
                    memory_id=memory.id,
                    entity_id=entity.id,
                    relationship_type="mentions",
                )
                db.add(link)

    async def find_related_memories(
        self,
        memory_id: uuid.UUID,
        user_id: uuid.UUID,
        db: AsyncSession,
        limit: int = 10,
    ) -> list[Memory]:
        """Return memories that share at least one entity with *memory_id*."""
        # Get entity ids for this memory
        entity_result = await db.execute(
            select(MemoryEntityLink.entity_id).where(
                MemoryEntityLink.memory_id == memory_id
            )
        )
        entity_ids = [row[0] for row in entity_result.fetchall()]
        if not entity_ids:
            return []

        # Find other memories with the same entities
        related_result = await db.execute(
            select(Memory)
            .join(MemoryEntityLink, Memory.id == MemoryEntityLink.memory_id)
            .where(
                MemoryEntityLink.entity_id.in_(entity_ids),
                Memory.id != memory_id,
                Memory.user_id == user_id,
                Memory.is_active == True,  # noqa: E712
            )
            .distinct()
            .limit(limit)
        )
        return list(related_result.scalars().all())
