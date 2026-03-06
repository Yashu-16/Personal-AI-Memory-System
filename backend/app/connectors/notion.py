"""Notion connector using notion-client."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app.connectors.base import BaseConnector
from app.models.source_document import SourceDocument

logger = logging.getLogger(__name__)


class NotionConnector(BaseConnector):
    """Fetch Notion pages and databases as SourceDocuments."""

    source_type = "notion"  # type: ignore[override]

    def __init__(self) -> None:
        self._api_key: str = ""

    async def connect(self, credentials: dict[str, Any]) -> bool:
        self._api_key = credentials.get("api_key", "")
        return bool(self._api_key)

    def _get_client(self) -> Any:
        try:
            from notion_client import Client  # type: ignore

            return Client(auth=self._api_key)
        except Exception as exc:
            logger.error("Failed to create Notion client: %s", exc)
            return None

    def _extract_text(self, rich_text: list[dict]) -> str:
        """Convert Notion rich_text array to plain string."""
        return "".join(block.get("plain_text", "") for block in rich_text)

    def _page_to_content(self, page: dict, blocks: list[dict]) -> str:
        """Build a plain-text representation of a Notion page."""
        lines: list[str] = []
        # Title from properties
        for prop in page.get("properties", {}).values():
            if prop.get("type") == "title":
                lines.append(self._extract_text(prop.get("title", [])))
                break

        for block in blocks:
            btype = block.get("type", "")
            inner = block.get(btype, {})
            rich = inner.get("rich_text", [])
            if rich:
                lines.append(self._extract_text(rich))

        return "\n".join(lines)

    async def sync(
        self, user_id: uuid.UUID, cursor: str | None
    ) -> tuple[list[SourceDocument], str | None]:
        """Fetch Notion pages modified since *cursor*."""
        client = self._get_client()
        if client is None:
            return [], cursor

        documents: list[SourceDocument] = []
        new_cursor: str | None = cursor

        try:
            search_params: dict[str, Any] = {
                "filter": {"value": "page", "property": "object"},
                "sort": {"direction": "descending", "timestamp": "last_edited_time"},
                "page_size": 50,
            }
            result = client.search(**search_params)
            pages = result.get("results", [])
        except Exception as exc:
            logger.error("Notion search failed: %s", exc)
            return [], cursor

        for page in pages:
            try:
                page_id = page["id"]
                last_edited = page.get("last_edited_time", "")

                if cursor and last_edited <= cursor:
                    continue

                # Fetch blocks
                blocks_result = client.blocks.children.list(block_id=page_id)
                blocks = blocks_result.get("results", [])

                content = self._page_to_content(page, blocks)
                if not content.strip():
                    continue

                # Derive title
                title = ""
                for prop in page.get("properties", {}).values():
                    if prop.get("type") == "title":
                        title = self._extract_text(prop.get("title", []))
                        break

                try:
                    from dateutil.parser import parse  # type: ignore

                    ts: datetime = parse(last_edited) if last_edited else datetime.now(timezone.utc)
                except Exception:
                    ts = datetime.now(timezone.utc)

                doc = SourceDocument(
                    user_id=user_id,
                    source_type=self.source_type,
                    source_item_id=page_id,
                    content=content,
                    title=title or page_id,
                    metadata_={"url": page.get("url"), "last_edited": last_edited},
                    timestamp=ts,
                )
                documents.append(doc)

                if not new_cursor or last_edited > new_cursor:
                    new_cursor = last_edited
            except Exception as exc:
                logger.warning("Failed to process Notion page: %s", exc)

        return documents, new_cursor

    async def disconnect(self) -> None:
        self._api_key = ""
