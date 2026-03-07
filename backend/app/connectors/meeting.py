"""Meeting transcript connector."""

import uuid
from datetime import datetime, timezone
from typing import Any

from app.connectors.base import BaseConnector
from app.models.source_document import SourceDocument
from app.utils.text_processing import clean_html, normalize_whitespace


class MeetingConnector(BaseConnector):
    """Accept meeting transcript text and convert it to SourceDocuments."""

    source_type = "meeting"  # type: ignore[override]

    def __init__(self) -> None:
        self._transcripts: list[dict[str, Any]] = []

    async def connect(self, credentials: dict[str, Any]) -> bool:
        """Load transcripts from credentials.

        credentials should contain:
          - 'transcripts': list of {title, content, participants, timestamp}
        or
          - 'transcript': single transcript string
        """
        raw = credentials.get("transcripts")
        if raw is None:
            single = credentials.get("transcript", "")
            raw = [{"title": "Meeting", "content": single}]
        self._transcripts = raw if isinstance(raw, list) else []
        return True

    async def sync(
        self, user_id: uuid.UUID, cursor: str | None
    ) -> tuple[list[SourceDocument], str | None]:
        """Return all transcripts as SourceDocuments."""
        documents: list[SourceDocument] = []
        for i, transcript in enumerate(self._transcripts):
            raw_content = transcript.get("content", "")
            cleaned = normalize_whitespace(clean_html(raw_content))

            try:
                ts_str = transcript.get("timestamp")
                if ts_str:
                    from dateutil.parser import parse  # type: ignore

                    ts: datetime = parse(ts_str)
                else:
                    ts = datetime.now(timezone.utc)
            except Exception:
                ts = datetime.now(timezone.utc)

            participants = transcript.get("participants", [])
            doc = SourceDocument(
                user_id=user_id,
                source_type=self.source_type,
                source_item_id=f"meeting-{i}",
                content=cleaned,
                title=transcript.get("title", f"Meeting {i + 1}"),
                participants=participants,
                metadata_={
                    "duration_minutes": transcript.get("duration_minutes"),
                    "platform": transcript.get("platform"),
                },
                timestamp=ts,
            )
            documents.append(doc)
        return documents, None

    async def disconnect(self) -> None:
        self._transcripts = []
