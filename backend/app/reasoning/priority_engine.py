"""Priority engine – suggest next actions based on overdue items and patterns."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment, CommitmentStatus
from app.models.memory import Memory
from app.models.task import Task, TaskPriority, TaskStatus


class PriorityEngine:
    """Generate prioritised suggestions for the user."""

    async def suggest(
        self,
        user_id: uuid.UUID,
        memories: list[Memory],
        tasks: list[Task],
        commitments: list[Commitment],
    ) -> list[str]:
        """Return a list of suggestion strings."""
        suggestions: list[str] = []
        now = datetime.now(timezone.utc)

        # Overdue commitments
        overdue_c = [
            c for c in commitments
            if c.status == CommitmentStatus.pending
            and c.deadline
            and c.deadline.replace(tzinfo=timezone.utc if c.deadline.tzinfo is None else c.deadline.tzinfo) < now
        ]
        for c in overdue_c[:3]:
            suggestions.append(f"⚠️ Overdue commitment: {c.action}")

        # High-priority tasks
        urgent_tasks = [
            t for t in tasks
            if t.status == TaskStatus.todo and t.priority in (TaskPriority.urgent, TaskPriority.high)
        ]
        for t in urgent_tasks[:3]:
            suggestions.append(f"🔴 High-priority task: {t.title}")

        # Tasks with upcoming deadlines
        upcoming = [
            t for t in tasks
            if t.status == TaskStatus.todo
            and t.deadline
            and 0 <= (t.deadline.replace(tzinfo=timezone.utc if t.deadline.tzinfo is None else t.deadline.tzinfo) - now).days <= 3
        ]
        for t in upcoming[:2]:
            suggestions.append(f"📅 Task due soon: {t.title}")

        if not suggestions:
            suggestions.append("✅ No urgent items – you're up to date!")

        return suggestions
