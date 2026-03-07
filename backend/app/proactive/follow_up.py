"""Follow-up generator – suggest follow-ups for pending commitments."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment, CommitmentStatus
from app.models.insight import Insight, InsightType


class FollowUpGenerator:
    """Generate follow-up insights for commitments that need attention."""

    async def generate(
        self, user_id: uuid.UUID, db: AsyncSession
    ) -> list[Insight]:
        """Return follow-up suggestions for pending commitments without deadlines."""
        result = await db.execute(
            select(Commitment).where(
                Commitment.user_id == user_id,
                Commitment.status == CommitmentStatus.pending,
                Commitment.deadline == None,  # noqa: E711
            ).order_by(Commitment.created_at.asc()).limit(10)
        )
        commitments = result.scalars().all()

        insights: list[Insight] = []
        for c in commitments:
            insight = Insight(
                user_id=user_id,
                insight_type=InsightType.follow_up,
                title=f"Follow up: {c.action[:80]}",
                content=(
                    f"You have a pending commitment with no deadline: '{c.action}'. "
                    f"Consider setting a deadline or completing it."
                ),
                supporting_memory_ids=[str(c.memory_id)] if c.memory_id else [],
                urgency="low",
            )
            insights.append(insight)

        return insights
