"""Insight Celery tasks."""

import asyncio

from app.workers.celery_app import celery_app


@celery_app.task(name="generate_insights_task", bind=True, max_retries=2)
def generate_insights_task(self, user_id_str: str) -> dict:
    """Generate proactive insights for a user."""
    return asyncio.get_event_loop().run_until_complete(_insights_async(user_id_str))


async def _insights_async(user_id_str: str) -> dict:
    import uuid  # noqa: PLC0415

    from app.database import AsyncSessionLocal  # noqa: PLC0415
    from app.proactive.engine import ProactiveEngine  # noqa: PLC0415

    user_id = uuid.UUID(user_id_str)
    async with AsyncSessionLocal() as db:
        engine = ProactiveEngine()
        insights = await engine.generate_insights(user_id, db)
        await db.commit()
    return {"status": "ok", "insights": len(insights)}


@celery_app.task(name="weekly_review_task", bind=True, max_retries=2)
def weekly_review_task(self, user_id_str: str) -> dict:
    """Generate and persist a weekly review insight."""
    return asyncio.get_event_loop().run_until_complete(_weekly_async(user_id_str))


async def _weekly_async(user_id_str: str) -> dict:
    import uuid  # noqa: PLC0415

    from app.database import AsyncSessionLocal  # noqa: PLC0415
    from app.proactive.weekly_review import WeeklyReviewGenerator  # noqa: PLC0415

    user_id = uuid.UUID(user_id_str)
    async with AsyncSessionLocal() as db:
        generator = WeeklyReviewGenerator()
        insight = await generator.generate(user_id, db)
        db.add(insight)
        await db.commit()
    return {"status": "ok"}
