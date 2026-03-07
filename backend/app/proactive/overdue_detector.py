"""Overdue detector – find overdue commitments and tasks."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment, CommitmentStatus
from app.models.insight import Insight, InsightType
from app.models.task import Task, TaskStatus


class OverdueDetector:
    """Detect overdue commitments and stale tasks."""

    async def detect(
        self, user_id: uuid.UUID, db: AsyncSession
    ) -> list[Insight]:
        """Return insights for overdue items."""
        now = datetime.now(timezone.utc)
        insights: list[Insight] = []

        # Overdue commitments
        result = await db.execute(
            select(Commitment).where(
                Commitment.user_id == user_id,
                Commitment.status == CommitmentStatus.pending,
                Commitment.deadline != None,  # noqa: E711
                Commitment.deadline < now,
            ).limit(20)
        )
        commitments = result.scalars().all()

        for c in commitments:
            days_overdue = (now - c.deadline.replace(tzinfo=timezone.utc if c.deadline.tzinfo is None else c.deadline.tzinfo)).days
            insight = Insight(
                user_id=user_id,
                insight_type=InsightType.overdue_commitment,
                title=f"Overdue commitment: {c.action[:80]}",
                content=(
                    f"You have an overdue commitment: '{c.action}'. "
                    f"It was due {days_overdue} day(s) ago."
                ),
                supporting_memory_ids=[str(c.memory_id)] if c.memory_id else [],
                urgency="high" if days_overdue > 7 else "medium",
            )
            insights.append(insight)

        # Stale tasks
        result = await db.execute(
            select(Task).where(
                Task.user_id == user_id,
                Task.status == TaskStatus.todo,
                Task.deadline != None,  # noqa: E711
                Task.deadline < now,
            ).limit(20)
        )
        tasks = result.scalars().all()
        for t in tasks:
            insight = Insight(
                user_id=user_id,
                insight_type=InsightType.stale_task,
                title=f"Overdue task: {t.title[:80]}",
                content=f"Task '{t.title}' is past its deadline.",
                supporting_memory_ids=[str(t.memory_id)] if t.memory_id else [],
                urgency="medium",
            )
            insights.append(insight)

        return insights
