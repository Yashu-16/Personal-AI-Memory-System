"""Extraction pipeline – orchestrates all extraction stages."""

import logging
import uuid
from datetime import datetime, timezone

from app.extraction.commitment_detector import CommitmentDetector
from app.extraction.date_extractor import DateExtractor
from app.extraction.entity_extractor import EntityExtractor
from app.extraction.salience_scorer import SalienceScorer
from app.extraction.task_extractor import TaskExtractor
from app.extraction.topic_classifier import TopicClassifier
from app.models.memory import Memory, MemoryType
from app.models.source_document import SourceDocument
from app.utils.text_processing import normalize_whitespace, truncate_text

logger = logging.getLogger(__name__)


class ExtractionPipeline:
    """Orchestrates all extraction stages for a source document."""

    def __init__(self) -> None:
        self._entity_extractor = EntityExtractor()
        self._commitment_detector = CommitmentDetector()
        self._task_extractor = TaskExtractor()
        self._date_extractor = DateExtractor()
        self._topic_classifier = TopicClassifier()
        self._salience_scorer = SalienceScorer()

    async def process_document(self, source_document: SourceDocument) -> list[Memory]:
        """Process a source document and return extracted Memory objects."""
        raw_text = normalize_whitespace(source_document.content or "")
        if not raw_text:
            return []

        user_id: uuid.UUID = source_document.user_id
        source_type: str = source_document.source_type
        source_ref: str = str(source_document.id) if source_document.id else ""

        # --- Stage 1: Extract components ---
        entities = self._entity_extractor.extract(raw_text)
        commitments = self._commitment_detector.detect(raw_text)
        tasks = self._task_extractor.extract(raw_text)
        dates = self._date_extractor.extract(raw_text)
        topics = self._topic_classifier.classify(raw_text)

        memories: list[Memory] = []

        # --- Stage 2: Create fact memory for the document itself ---
        summary = truncate_text(raw_text, 300)
        salience = self._salience_scorer.score(
            raw_text, entities, len(commitments), len(tasks), dates
        )
        fact_memory = Memory(
            user_id=user_id,
            memory_type=MemoryType.fact,
            content=truncate_text(raw_text, 4000),
            summary=summary,
            source_type=source_type,
            source_ref=source_ref,
            confidence=1.0,
            salience_score=salience,
        )
        await self._attach_embedding(fact_memory)
        memories.append(fact_memory)

        # --- Stage 3: Commitment memories ---
        for c in commitments:
            mem = Memory(
                user_id=user_id,
                memory_type=MemoryType.commitment,
                content=c.raw_text,
                summary=c.action,
                source_type=source_type,
                source_ref=source_ref,
                confidence=0.85,
                salience_score=min(salience + 0.2, 1.0),
            )
            await self._attach_embedding(mem)
            memories.append(mem)

        # --- Stage 4: Task memories ---
        for t in tasks:
            mem = Memory(
                user_id=user_id,
                memory_type=MemoryType.task,
                content=t.title,
                summary=t.title,
                source_type=source_type,
                source_ref=source_ref,
                confidence=0.9,
                salience_score=min(salience + 0.15, 1.0),
            )
            await self._attach_embedding(mem)
            memories.append(mem)

        # --- Stage 5: Event memories from dates with context ---
        for d in dates:
            if d.context:
                mem = Memory(
                    user_id=user_id,
                    memory_type=MemoryType.event,
                    content=d.context,
                    summary=d.context[:100],
                    source_type=source_type,
                    source_ref=source_ref,
                    confidence=0.75,
                    salience_score=0.4,
                    expires_at=d.date if d.is_deadline else None,
                )
                await self._attach_embedding(mem)
                memories.append(mem)

        logger.debug(
            "Extracted %d memories from document %s", len(memories), source_document.id
        )
        return memories

    @staticmethod
    async def _attach_embedding(memory: Memory) -> None:
        """Generate and attach an embedding to a memory object."""
        try:
            from app.utils.embeddings import EmbeddingService  # noqa: PLC0415

            svc = EmbeddingService()
            embedding = await svc.get_embedding(memory.content)
            # Store as JSON string if Vector type not available
            import json  # noqa: PLC0415

            memory.embedding = json.dumps(embedding)
        except Exception as exc:
            logger.debug("Embedding generation skipped: %s", exc)
