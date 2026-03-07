"""Local notes connector – accepts markdown/text content directly."""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.connectors.base import BaseConnector
from app.models.source_document import SourceDocument
from app.utils.text_processing import clean_html


class LocalNotesConnector(BaseConnector):
    """Accept file paths or raw text content and convert to SourceDocuments."""

    source_type = "notes"  # type: ignore[override]

    def __init__(self) -> None:
        self._notes: list[dict[str, Any]] = []

    async def connect(self, credentials: dict[str, Any]) -> bool:
        """Load notes from *credentials['notes']* (list of {title, content}) or a single string."""
        raw = credentials.get("notes", [])
        if isinstance(raw, str):
            self._notes = [{"title": "Note", "content": raw}]
        elif isinstance(raw, list):
            self._notes = raw
        return True

    async def sync(
        self, user_id: uuid.UUID, cursor: str | None
    ) -> tuple[list[SourceDocument], str | None]:
        """Return all loaded notes as SourceDocuments."""
        documents: list[SourceDocument] = []
        for i, note in enumerate(self._notes):
            raw_content: str = note.get("content", "")
            clean_content = clean_html(raw_content)
            doc = SourceDocument(
                user_id=user_id,
                source_type=self.source_type,
                source_item_id=f"note-{i}",
                content=clean_content,
                title=note.get("title", f"Note {i + 1}"),
                metadata_={"format": note.get("format", "text")},
                timestamp=datetime.now(timezone.utc),
            )
            documents.append(doc)
        return documents, None

    async def disconnect(self) -> None:
        self._notes = []
