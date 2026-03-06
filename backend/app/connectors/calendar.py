"""Google Calendar connector."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.connectors.base import BaseConnector
from app.models.source_document import SourceDocument

logger = logging.getLogger(__name__)


class GoogleCalendarConnector(BaseConnector):
    """Fetch Google Calendar events as SourceDocuments."""

    source_type = "calendar"  # type: ignore[override]

    def __init__(self) -> None:
        self._credentials: dict[str, Any] = {}

    async def connect(self, credentials: dict[str, Any]) -> bool:
        self._credentials = credentials
        return True

    def _build_service(self) -> Any:
        try:
            from google.oauth2.credentials import Credentials  # type: ignore
            from googleapiclient.discovery import build  # type: ignore

            creds = Credentials(
                token=self._credentials.get("access_token"),
                refresh_token=self._credentials.get("refresh_token"),
                client_id=self._credentials.get("client_id"),
                client_secret=self._credentials.get("client_secret"),
                token_uri="https://oauth2.googleapis.com/token",
            )
            return build("calendar", "v3", credentials=creds, cache_discovery=False)
        except Exception as exc:
            logger.error("Failed to build Calendar service: %s", exc)
            return None

    async def sync(
        self, user_id: uuid.UUID, cursor: str | None
    ) -> tuple[list[SourceDocument], str | None]:
        """Fetch calendar events updated since *cursor* (RFC3339 timestamp)."""
        service = self._build_service()
        if service is None:
            return [], cursor

        try:
            kwargs: dict[str, Any] = {
                "calendarId": "primary",
                "maxResults": 100,
                "singleEvents": True,
                "orderBy": "startTime",
            }
            if cursor:
                kwargs["updatedMin"] = cursor

            result = service.events().list(**kwargs).execute()
            events = result.get("items", [])
        except Exception as exc:
            logger.error("Calendar list events failed: %s", exc)
            return [], cursor

        documents: list[SourceDocument] = []
        new_cursor = cursor

        for event in events:
            try:
                start = event.get("start", {})
                start_str = start.get("dateTime") or start.get("date", "")
                end = event.get("end", {})
                end_str = end.get("dateTime") or end.get("date", "")
                attendees = [
                    a.get("email", "") for a in event.get("attendees", [])
                ]
                title = event.get("summary", "(no title)")
                description = event.get("description", "")
                content = f"{title}\n{description}\nStart: {start_str}\nEnd: {end_str}"

                # Parse timestamp
                try:
                    from dateutil.parser import parse  # type: ignore

                    ts: datetime = parse(start_str) if start_str else datetime.now(timezone.utc)
                except Exception:
                    ts = datetime.now(timezone.utc)

                doc = SourceDocument(
                    user_id=user_id,
                    source_type=self.source_type,
                    source_item_id=event.get("id"),
                    content=content,
                    title=title,
                    participants=attendees,
                    metadata_={
                        "start": start_str,
                        "end": end_str,
                        "location": event.get("location"),
                        "status": event.get("status"),
                    },
                    timestamp=ts,
                )
                documents.append(doc)
                if event.get("updated"):
                    new_cursor = event["updated"]
            except Exception as exc:
                logger.warning("Failed to process calendar event: %s", exc)

        return documents, new_cursor

    async def disconnect(self) -> None:
        self._credentials = {}
