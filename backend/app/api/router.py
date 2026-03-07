"""Central API router – aggregates all sub-routers."""

from fastapi import APIRouter

from app.api import (
    auth,
    commitments,
    dashboard,
    insights,
    memories,
    privacy,
    query,
    sources,
    tasks,
)

router = APIRouter()

router.include_router(auth.router, prefix="/api/auth", tags=["auth"])
router.include_router(memories.router, prefix="/api/memories", tags=["memories"])
router.include_router(query.router, prefix="/api/query", tags=["query"])
router.include_router(sources.router, prefix="/api/sources", tags=["sources"])
router.include_router(commitments.router, prefix="/api/commitments", tags=["commitments"])
router.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
router.include_router(insights.router, prefix="/api/insights", tags=["insights"])
router.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
router.include_router(privacy.router, prefix="/api/privacy", tags=["privacy"])
