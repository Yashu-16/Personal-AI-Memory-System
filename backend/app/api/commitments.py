"""Commitments API endpoints."""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.commitment import Commitment, CommitmentStatus
from app.models.user import User
from app.schemas.commitment import CommitmentResponse, CommitmentUpdate

router = APIRouter()


@router.get("/", response_model=list[CommitmentResponse])
async def list_commitments(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    commitment_status: Optional[CommitmentStatus] = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[Commitment]:
    """List commitments for the current user."""
    stmt = select(Commitment).where(Commitment.user_id == current_user.id)
    if commitment_status:
        stmt = stmt.where(Commitment.status == commitment_status)
    stmt = stmt.order_by(Commitment.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.put("/{commitment_id}", response_model=CommitmentResponse)
async def update_commitment(
    commitment_id: uuid.UUID,
    payload: CommitmentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Commitment:
    """Update the status of a commitment."""
    result = await db.execute(
        select(Commitment).where(
            Commitment.id == commitment_id,
            Commitment.user_id == current_user.id,
        )
    )
    commitment = result.scalar_one_or_none()
    if commitment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Commitment not found")

    commitment.status = payload.status
    await db.flush()
    await db.refresh(commitment)
    return commitment
