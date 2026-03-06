"""Abstract base class for all source connectors."""

import uuid
from abc import ABC, abstractmethod
from typing import Any

from app.models.source_document import SourceDocument


class BaseConnector(ABC):
    """Interface that every source connector must implement."""

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Identifier for this connector (e.g. 'gmail')."""
        ...

    @abstractmethod
    async def connect(self, credentials: dict[str, Any]) -> bool:
        """Validate and store credentials. Returns True on success."""
        ...

    @abstractmethod
    async def sync(
        self, user_id: uuid.UUID, cursor: str | None
    ) -> tuple[list[SourceDocument], str | None]:
        """Fetch new documents since *cursor*.

        Returns a tuple of (documents, new_cursor).
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Revoke tokens / clean up state."""
        ...
