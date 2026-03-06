"""Insight SQLAlchemy model."""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class InsightType(str, PyEnum):
    overdue_commitment = "overdue_commitment"
    stale_task = "stale_task"
    schedule_conflict = "schedule_conflict"
    pattern = "pattern"
    weekly_review = "weekly_review"
    follow_up = "follow_up"


class Insight(Base):
    """A proactively generated insight for the user."""

    __tablename__ = "insights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    insight_type: Mapped[InsightType] = mapped_column(
        Enum(InsightType, name="insighttype"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    supporting_memory_ids: Mapped[list] = mapped_column(
        JSONB, default=list, nullable=False, server_default="[]"
    )
    urgency: Mapped[str] = mapped_column(String(32), default="low", nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Insight id={self.id} type={self.insight_type}>"
