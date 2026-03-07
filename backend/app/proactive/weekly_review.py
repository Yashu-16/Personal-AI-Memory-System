"""Weekly review generator."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment, CommitmentStatus
from app.models.insight import Insight, InsightType
from app.models.memory import Memory
from app.models.task import Task, TaskStatus


class WeeklyReviewGenerator:
    """Generate a weekly review insight summarising the user's week."""

    async def generate(
        self, user_id: uuid.UUID, db: AsyncSession
    ) -> Insight:
        """Build and return a weekly review Insight."""
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)

        # Count memories this week
        mem_count_result = await db.execute(
            select(func.count()).select_from(Memory).where(
                Memory.user_id == user_id,
                Memory.is_active == True,  # noqa: E712
                Memory.created_at >= week_ago,
            )
        )
        mem_count: int = mem_count_result.scalar_one()

        # Completed commitments
        done_commits_result = await db.execute(
            select(func.count()).select_from(Commitment).where(
                Commitment.user_id == user_id,
                Commitment.status == CommitmentStatus.completed,
                Commitment.updated_at >= week_ago,
            )
        )
        done_commits: int = done_commits_result.scalar_one()

        # Completed tasks
        done_tasks_result = await db.execute(
            select(func.count()).select_from(Task).where(
                Task.user_id == user_id,
                Task.status == TaskStatus.done,
                Task.updated_at >= week_ago,
            )
        )
        done_tasks: int = done_tasks_result.scalar_one()

        # Open commitments
        open_result = await db.execute(
            select(func.count()).select_from(Commitment).where(
                Commitment.user_id == user_id,
                Commitment.status == CommitmentStatus.pending,
            )
        )
        open_commits: int = open_result.scalar_one()

        content = (
            f"Weekly Review ({week_ago.strftime('%b %d')} – {now.strftime('%b %d')}):\n"
            f"• Memories captured: {mem_count}\n"
            f"• Commitments completed: {done_commits}\n"
            f"• Tasks done: {done_tasks}\n"
            f"• Open commitments remaining: {open_commits}"
        )

        return Insight(
            user_id=user_id,
            insight_type=InsightType.weekly_review,
            title="Your Weekly Review",
            content=content,
            supporting_memory_ids=[],
            urgency="low",
        )
