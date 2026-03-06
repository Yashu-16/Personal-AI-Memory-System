"""Proactive engine – orchestrates all insight generators."""

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.insight import Insight
from app.proactive.conflict_scanner import ConflictScanner
from app.proactive.follow_up import FollowUpGenerator
from app.proactive.overdue_detector import OverdueDetector
from app.proactive.weekly_review import WeeklyReviewGenerator

logger = logging.getLogger(__name__)


class ProactiveEngine:
    """Orchestrate all proactive insight generators."""

    def __init__(self) -> None:
        self._overdue = OverdueDetector()
        self._conflict = ConflictScanner()
        self._weekly = WeeklyReviewGenerator()
        self._follow_up = FollowUpGenerator()

    async def generate_insights(
        self, user_id: uuid.UUID, db: AsyncSession
    ) -> list[Insight]:
        """Run all detectors and return a combined list of Insight objects."""
        insights: list[Insight] = []

        try:
            insights.extend(await self._overdue.detect(user_id, db))
        except Exception as exc:
            logger.warning("Overdue detection failed: %s", exc)

        try:
            insights.extend(await self._conflict.scan(user_id, db))
        except Exception as exc:
            logger.warning("Conflict scan failed: %s", exc)

        try:
            insights.extend(await self._follow_up.generate(user_id, db))
        except Exception as exc:
            logger.warning("Follow-up generation failed: %s", exc)

        # Persist new insights
        for insight in insights:
            db.add(insight)

        try:
            await db.flush()
        except Exception as exc:
            logger.error("Failed to persist insights: %s", exc)
            await db.rollback()
            insights = []

        return insights
