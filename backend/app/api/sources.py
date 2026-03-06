"""Connected sources API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.user import ConnectedAccount, User
from app.schemas.source import ConnectedSourceResponse, ConnectSourceRequest, SyncResponse

router = APIRouter()

SUPPORTED_SOURCES = {"gmail", "calendar", "notion", "notes", "meeting"}


@router.get("/", response_model=list[ConnectedSourceResponse])
async def list_sources(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> list[ConnectedAccount]:
    """List all connected accounts for the current user."""
    result = await db.execute(
        select(ConnectedAccount).where(
            ConnectedAccount.user_id == current_user.id,
            ConnectedAccount.is_active == True,  # noqa: E712
        )
    )
    return list(result.scalars().all())


@router.post("/connect", response_model=ConnectedSourceResponse, status_code=status.HTTP_201_CREATED)
async def connect_source(
    payload: ConnectSourceRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> ConnectedAccount:
    """Connect a new external source."""
    if payload.source_type not in SUPPORTED_SOURCES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported source type. Supported: {SUPPORTED_SOURCES}",
        )

    account = ConnectedAccount(
        user_id=current_user.id,
        source_type=payload.source_type,
        credentials=payload.credentials,
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    return account


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect_source(
    source_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> None:
    """Disconnect (deactivate) a connected source."""
    result = await db.execute(
        select(ConnectedAccount).where(
            ConnectedAccount.id == source_id,
            ConnectedAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    account.is_active = False
    await db.flush()


@router.post("/{source_id}/sync", response_model=SyncResponse)
async def sync_source(
    source_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> SyncResponse:
    """Trigger an asynchronous sync for a connected source."""
    result = await db.execute(
        select(ConnectedAccount).where(
            ConnectedAccount.id == source_id,
            ConnectedAccount.user_id == current_user.id,
            ConnectedAccount.is_active == True,  # noqa: E712
        )
    )
    account = result.scalar_one_or_none()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    # Enqueue the sync task if Celery workers are available
    try:
        from app.workers.ingestion_tasks import sync_source_task  # noqa: PLC0415

        sync_source_task.delay(str(current_user.id), str(source_id))
    except Exception:
        pass  # Worker may not be running; fire-and-forget

    return SyncResponse(message="Sync queued", source_id=source_id)
