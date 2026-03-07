"""Gmail connector using the Google API client library."""

import base64
import email as email_lib
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.connectors.base import BaseConnector
from app.models.source_document import SourceDocument

logger = logging.getLogger(__name__)


class GmailConnector(BaseConnector):
    """Fetch Gmail messages and convert them to SourceDocuments."""

    source_type = "gmail"  # type: ignore[override]

    def __init__(self) -> None:
        self._service: Any = None
        self._credentials: dict[str, Any] = {}

    async def connect(self, credentials: dict[str, Any]) -> bool:
        """Store OAuth2 credentials. Actual service initialisation is lazy."""
        self._credentials = credentials
        return True

    def _build_service(self) -> Any:
        """Build the Google API service object from stored credentials."""
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
            return build("gmail", "v1", credentials=creds, cache_discovery=False)
        except Exception as exc:
            logger.error("Failed to build Gmail service: %s", exc)
            return None

    def _decode_body(self, payload: dict) -> str:
        """Recursively extract plain-text body from a Gmail message payload."""
        mime_type: str = payload.get("mimeType", "")
        if mime_type == "text/plain":
            data = payload.get("body", {}).get("data", "")
            try:
                return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
            except Exception:
                return ""
        for part in payload.get("parts", []):
            text = self._decode_body(part)
            if text:
                return text
        return ""

    async def sync(
        self, user_id: uuid.UUID, cursor: str | None
    ) -> tuple[list[SourceDocument], str | None]:
        """Fetch emails since *cursor* (history ID or RFC date)."""
        service = self._build_service()
        if service is None:
            return [], cursor

        try:
            query = f"after:{cursor}" if cursor else "newer_than:30d"
            result = (
                service.users()
                .messages()
                .list(userId="me", q=query, maxResults=50)
                .execute()
            )
            messages = result.get("messages", [])
        except Exception as exc:
            logger.error("Gmail list messages failed: %s", exc)
            return [], cursor

        documents: list[SourceDocument] = []
        latest_ts: str | None = cursor

        for msg_ref in messages:
            try:
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=msg_ref["id"], format="full")
                    .execute()
                )
                headers = {
                    h["name"].lower(): h["value"]
                    for h in msg.get("payload", {}).get("headers", [])
                }
                subject = headers.get("subject", "(no subject)")
                sender = headers.get("from", "")
                date_str = headers.get("date", "")
                body = self._decode_body(msg.get("payload", {}))

                # Parse timestamp
                try:
                    ts = email_lib.utils.parsedate_to_datetime(date_str)
                except Exception:
                    ts = datetime.now(timezone.utc)

                doc = SourceDocument(
                    user_id=user_id,
                    source_type=self.source_type,
                    source_item_id=msg_ref["id"],
                    content=body or subject,
                    title=subject,
                    participants=[sender],
                    metadata_={"headers": headers},
                    timestamp=ts,
                )
                documents.append(doc)
                latest_ts = str(msg.get("internalDate", latest_ts))
            except Exception as exc:
                logger.warning("Failed to process Gmail message %s: %s", msg_ref["id"], exc)

        return documents, latest_ts

    async def disconnect(self) -> None:
        self._service = None
        self._credentials = {}
