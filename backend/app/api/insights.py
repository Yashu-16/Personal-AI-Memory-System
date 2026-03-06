"""Insights API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.insight import Insight
from app.models.user import User
from app.schemas.insight import InsightResponse

router = APIRouter()


@router.get("/", response_model=list[InsightResponse])
async def list_insights(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> list[Insight]:
    """List all insights for the current user."""
    result = await db.execute(
        select(Insight)
        .where(Insight.user_id == current_user.id)
        .order_by(Insight.created_at.desc())
        .limit(50)
    )
    return list(result.scalars().all())


@router.put("/{insight_id}/read", response_model=InsightResponse)
async def mark_insight_read(
    insight_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Insight:
    """Mark an insight as read."""
    result = await db.execute(
        select(Insight).where(
            Insight.id == insight_id,
            Insight.user_id == current_user.id,
        )
    )
    insight = result.scalar_one_or_none()
    if insight is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found")

    insight.is_read = True
    await db.flush()
    await db.refresh(insight)
    return insight
