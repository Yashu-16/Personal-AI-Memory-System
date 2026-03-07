"""Ingestion service – process source documents into memories."""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.consolidation.deduplicator import Deduplicator
from app.consolidation.linker import MemoryLinker
from app.extraction.entity_extractor import EntityExtractor
from app.extraction.pipeline import ExtractionPipeline
from app.models.memory import Memory
from app.models.source_document import SourceDocument

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrate document ingestion: extraction, deduplication, persistence."""

    def __init__(self) -> None:
        self._pipeline = ExtractionPipeline()
        self._deduplicator = Deduplicator()
        self._linker = MemoryLinker()
        self._entity_extractor = EntityExtractor()

    async def ingest_document(
        self,
        source_document: SourceDocument,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> list[Memory]:
        """Extract memories from *source_document*, deduplicate, and save."""
        # Ensure the document is persisted so it has an ID
        if not source_document.id:
            db.add(source_document)
            await db.flush()
            await db.refresh(source_document)

        # Run extraction pipeline
        try:
            extracted = await self._pipeline.process_document(source_document)
        except Exception as exc:
            logger.error("Extraction pipeline failed: %s", exc)
            return []

        saved: list[Memory] = []
        for memory in extracted:
            # Deduplicate
            is_dup, existing_id = await self._deduplicator.check_duplicate(
                memory.content, user_id, db
            )
            if is_dup:
                logger.debug("Skipping duplicate memory (existing=%s)", existing_id)
                continue

            db.add(memory)
            await db.flush()
            await db.refresh(memory)

            # Link entities
            entities = self._entity_extractor.extract(memory.content)
            await self._linker.link_entities(memory, entities, db)

            saved.append(memory)

        # Mark document as processed
        source_document.is_processed = True
        await db.flush()

        logger.info("Ingested %d memories from document %s", len(saved), source_document.id)
        return saved
