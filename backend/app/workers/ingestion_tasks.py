"""Ingestion Celery tasks."""

import asyncio
import logging
import uuid

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="sync_source_task", bind=True, max_retries=3)
def sync_source_task(self, user_id_str: str, source_id_str: str) -> dict:
    """Sync a connected source, then ingest new documents."""
    return asyncio.get_event_loop().run_until_complete(
        _sync_source_async(user_id_str, source_id_str)
    )


async def _sync_source_async(user_id_str: str, source_id_str: str) -> dict:
    from app.database import AsyncSessionLocal  # noqa: PLC0415
    from app.models.user import ConnectedAccount  # noqa: PLC0415
    from sqlalchemy import select  # noqa: PLC0415

    user_id = uuid.UUID(user_id_str)
    source_id = uuid.UUID(source_id_str)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ConnectedAccount).where(
                ConnectedAccount.id == source_id,
                ConnectedAccount.user_id == user_id,
                ConnectedAccount.is_active,
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            return {"status": "not_found"}

        # Dispatch connector
        connector = _get_connector(account.source_type)
        if connector is None:
            return {"status": "unsupported_source"}

        await connector.connect(account.credentials or {})
        documents, new_cursor = await connector.sync(user_id, account.sync_cursor)

        # Ingest documents
        from app.services.ingestion_service import IngestionService  # noqa: PLC0415

        svc = IngestionService()
        total_memories = 0
        for doc in documents:
            memories = await svc.ingest_document(doc, user_id, db)
            total_memories += len(memories)

        # Update cursor
        from datetime import datetime, timezone  # noqa: PLC0415

        account.sync_cursor = new_cursor
        account.last_sync_at = datetime.now(timezone.utc)
        await db.commit()

    return {"status": "ok", "documents": len(documents), "memories": total_memories}


def _get_connector(source_type: str):
    from app.connectors.calendar import GoogleCalendarConnector  # noqa: PLC0415
    from app.connectors.gmail import GmailConnector  # noqa: PLC0415
    from app.connectors.meeting import MeetingConnector  # noqa: PLC0415
    from app.connectors.notes import LocalNotesConnector  # noqa: PLC0415
    from app.connectors.notion import NotionConnector  # noqa: PLC0415

    mapping = {
        "gmail": GmailConnector,
        "calendar": GoogleCalendarConnector,
        "notion": NotionConnector,
        "notes": LocalNotesConnector,
        "meeting": MeetingConnector,
    }
    cls = mapping.get(source_type)
    return cls() if cls else None


@celery_app.task(name="ingest_document_task", bind=True, max_retries=3)
def ingest_document_task(self, source_document_id_str: str) -> dict:
    """Process a SourceDocument that is already persisted."""
    return asyncio.get_event_loop().run_until_complete(
        _ingest_document_async(source_document_id_str)
    )


async def _ingest_document_async(source_document_id_str: str) -> dict:
    import uuid  # noqa: PLC0415

    from app.database import AsyncSessionLocal  # noqa: PLC0415
    from app.models.source_document import SourceDocument  # noqa: PLC0415
    from app.services.ingestion_service import IngestionService  # noqa: PLC0415
    from sqlalchemy import select  # noqa: PLC0415

    doc_id = uuid.UUID(source_document_id_str)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SourceDocument).where(SourceDocument.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return {"status": "not_found"}

        svc = IngestionService()
        memories = await svc.ingest_document(doc, doc.user_id, db)
        await db.commit()
    return {"status": "ok", "memories": len(memories)}
