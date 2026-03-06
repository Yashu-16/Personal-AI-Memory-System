"""Commitment SQLAlchemy model."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CommitmentStatus(str, PyEnum):
    pending = "pending"
    completed = "completed"
    overdue = "overdue"
    cancelled = "cancelled"


class Commitment(Base):
    """A commitment or promise extracted from a memory."""

    __tablename__ = "commitments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    memory_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("memories.id", ondelete="SET NULL"), nullable=True
    )
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    person_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entities.id", ondelete="SET NULL"), nullable=True
    )
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[CommitmentStatus] = mapped_column(
        Enum(CommitmentStatus, name="commitmentstatus"),
        default=CommitmentStatus.pending,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    memory: Mapped["app.models.memory.Memory | None"] = relationship("Memory")  # type: ignore[name-defined]
    person: Mapped["app.models.entity.Entity | None"] = relationship("Entity")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<Commitment id={self.id} status={self.status}>"
