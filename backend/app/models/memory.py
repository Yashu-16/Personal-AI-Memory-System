"""Memory SQLAlchemy model with optional pgvector support."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Attempt to import Vector from pgvector; fall back to Text for test environments
try:
    from pgvector.sqlalchemy import Vector  # type: ignore

    _VECTOR_TYPE = Vector(1536)
    _VECTOR_COLUMN_TYPE = None
except ImportError:
    _VECTOR_TYPE = Text  # type: ignore
    _VECTOR_COLUMN_TYPE = Text


class MemoryType(str, PyEnum):
    fact = "fact"
    commitment = "commitment"
    task = "task"
    event = "event"
    preference = "preference"
    goal = "goal"
    insight = "insight"


class Memory(Base):
    """A single unit of extracted memory."""

    __tablename__ = "memories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    memory_type: Mapped[MemoryType] = mapped_column(
        Enum(MemoryType, name="memorytype"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    salience_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    # Vector embedding – stored as Vector(1536) when pgvector is available,
    # otherwise as Text (JSON-serialised list) for test compatibility.
    embedding: Mapped[str | None] = mapped_column(
        _VECTOR_TYPE if _VECTOR_COLUMN_TYPE is None else _VECTOR_COLUMN_TYPE,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["app.models.user.User"] = relationship("User", back_populates="memories")  # type: ignore[name-defined]
    entity_links: Mapped[list["app.models.entity.MemoryEntityLink"]] = relationship(  # type: ignore[name-defined]
        "MemoryEntityLink", back_populates="memory", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Memory id={self.id} type={self.memory_type}>"
