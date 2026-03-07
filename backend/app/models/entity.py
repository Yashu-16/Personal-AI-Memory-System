"""Entity and MemoryEntityLink SQLAlchemy models."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EntityType(str, PyEnum):
    person = "person"
    organization = "organization"
    place = "place"
    topic = "topic"


class Entity(Base):
    """A named entity extracted from memories."""

    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_type: Mapped[EntityType] = mapped_column(
        Enum(EntityType, name="entitytype"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False, server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    memory_links: Mapped[list["MemoryEntityLink"]] = relationship(
        "MemoryEntityLink", back_populates="entity", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Entity id={self.id} name={self.name} type={self.entity_type}>"


class MemoryEntityLink(Base):
    """Association between a Memory and an Entity."""

    __tablename__ = "memory_entity_links"

    memory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("memories.id", ondelete="CASCADE"),
        primary_key=True,
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    relationship_type: Mapped[str | None] = mapped_column(String(128), nullable=True)

    memory: Mapped["app.models.memory.Memory"] = relationship(  # type: ignore[name-defined]
        "Memory", back_populates="entity_links"
    )
    entity: Mapped["Entity"] = relationship("Entity", back_populates="memory_links")
