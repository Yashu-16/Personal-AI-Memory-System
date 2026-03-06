"""Conflict scanner – detect schedule conflicts in calendar/event memories."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insight import Insight, InsightType
from app.models.memory import Memory, MemoryType


class ConflictScanner:
    """Scan event memories for scheduling conflicts."""

    async def scan(
        self, user_id: uuid.UUID, db: AsyncSession
    ) -> list[Insight]:
        """Return insights for detected schedule conflicts."""
        result = await db.execute(
            select(Memory).where(
                Memory.user_id == user_id,
                Memory.memory_type == MemoryType.event,
                Memory.is_active == True,  # noqa: E712
                Memory.expires_at != None,  # noqa: E711
            ).limit(100)
        )
        events = result.scalars().all()

        insights: list[Insight] = []
        # Simple conflict detection: events with the same expires_at (datetime) overlap
        ts_map: dict[datetime, list[Memory]] = {}
        for ev in events:
            if ev.expires_at:
                key_hour = ev.expires_at.replace(minute=0, second=0, microsecond=0)
                ts_map.setdefault(key_hour, []).append(ev)

        for hour, evs in ts_map.items():
            if len(evs) >= 2:
                insight = Insight(
                    user_id=user_id,
                    insight_type=InsightType.schedule_conflict,
                    title=f"Schedule conflict at {hour.strftime('%Y-%m-%d %H:%M')}",
                    content=(
                        f"You have {len(evs)} events at the same time: "
                        + ", ".join(e.content[:50] for e in evs[:3])
                    ),
                    supporting_memory_ids=[str(e.id) for e in evs],
                    urgency="high",
                )
                insights.append(insight)

        return insights
