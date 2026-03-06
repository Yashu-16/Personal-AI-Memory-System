"""Consolidation Celery tasks."""

import asyncio

from app.workers.celery_app import celery_app


@celery_app.task(name="consolidate_memories_task", bind=True, max_retries=2)
def consolidate_memories_task(self, user_id_str: str) -> dict:
    """Run stale memory detection and optional archival."""
    return asyncio.get_event_loop().run_until_complete(_consolidate_async(user_id_str))


async def _consolidate_async(user_id_str: str) -> dict:
    import uuid  # noqa: PLC0415

    from app.consolidation.updater import MemoryUpdater  # noqa: PLC0415
    from app.database import AsyncSessionLocal  # noqa: PLC0415

    user_id = uuid.UUID(user_id_str)
    async with AsyncSessionLocal() as db:
        updater = MemoryUpdater()
        stale = await updater.find_stale(user_id, days_threshold=90, db=db)
        # Archive very stale memories
        for mem in stale:
            mem.is_archived = True
        await db.commit()
    return {"status": "ok", "archived": len(stale)}


@celery_app.task(name="deduplicate_task", bind=True, max_retries=2)
def deduplicate_task(self, user_id_str: str) -> dict:
    """Find and soft-delete duplicate memories for a user."""
    return asyncio.get_event_loop().run_until_complete(_dedup_async(user_id_str))


async def _dedup_async(user_id_str: str) -> dict:
    import uuid  # noqa: PLC0415

    from app.consolidation.deduplicator import Deduplicator  # noqa: PLC0415
    from app.database import AsyncSessionLocal  # noqa: PLC0415
    from app.models.memory import Memory  # noqa: PLC0415
    from sqlalchemy import select  # noqa: PLC0415

    user_id = uuid.UUID(user_id_str)
    removed = 0

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Memory).where(Memory.user_id == user_id, Memory.is_active).limit(500)
        )
        memories = result.scalars().all()
        deduplicator = Deduplicator()
        seen_contents: set[str] = set()
        for mem in memories:
            content_key = mem.content[:200].strip().lower()
            if content_key in seen_contents:
                mem.is_active = False
                removed += 1
            else:
                seen_contents.add(content_key)
        await db.commit()
    return {"status": "ok", "removed": removed}
