"""Extraction Celery tasks."""

import asyncio

from app.workers.celery_app import celery_app


@celery_app.task(name="extract_memories_task", bind=True, max_retries=3)
def extract_memories_task(self, source_document_id_str: str) -> dict:
    """Re-run extraction pipeline on a source document."""
    return asyncio.get_event_loop().run_until_complete(
        _extract_async(source_document_id_str)
    )


async def _extract_async(source_document_id_str: str) -> dict:
    import uuid  # noqa: PLC0415

    from app.database import AsyncSessionLocal  # noqa: PLC0415
    from app.extraction.pipeline import ExtractionPipeline  # noqa: PLC0415
    from app.models.source_document import SourceDocument  # noqa: PLC0415
    from sqlalchemy import select  # noqa: PLC0415

    doc_id = uuid.UUID(source_document_id_str)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SourceDocument).where(SourceDocument.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return {"status": "not_found"}

        pipeline = ExtractionPipeline()
        memories = await pipeline.process_document(doc)
        for mem in memories:
            db.add(mem)
        await db.commit()
    return {"status": "ok", "memories": len(memories)}


@celery_app.task(name="generate_embeddings_task", bind=True, max_retries=3)
def generate_embeddings_task(self, memory_id_str: str) -> dict:
    """Generate and store an embedding for a single memory."""
    return asyncio.get_event_loop().run_until_complete(
        _embed_async(memory_id_str)
    )


async def _embed_async(memory_id_str: str) -> dict:
    import json  # noqa: PLC0415
    import uuid  # noqa: PLC0415

    from app.database import AsyncSessionLocal  # noqa: PLC0415
    from app.models.memory import Memory  # noqa: PLC0415
    from app.utils.embeddings import EmbeddingService  # noqa: PLC0415
    from sqlalchemy import select  # noqa: PLC0415

    mem_id = uuid.UUID(memory_id_str)
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Memory).where(Memory.id == mem_id))
        memory = result.scalar_one_or_none()
        if not memory:
            return {"status": "not_found"}

        svc = EmbeddingService()
        embedding = await svc.get_embedding(memory.content)
        memory.embedding = json.dumps(embedding)
        await db.commit()
    return {"status": "ok"}
