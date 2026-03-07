"""Memories API endpoints."""

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.memory import Memory, MemoryType
from app.models.user import User
from app.schemas.memory import (
    MemoryCreate,
    MemoryResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryUpdate,
)

router = APIRouter()


@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    payload: MemoryCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Memory:
    """Create a new memory for the current user."""
    memory = Memory(
        user_id=current_user.id,
        memory_type=payload.memory_type,
        content=payload.content,
        summary=payload.summary,
        source_type=payload.source_type,
        source_ref=payload.source_ref,
        confidence=payload.confidence,
        salience_score=payload.salience_score,
    )
    db.add(memory)
    await db.flush()
    await db.refresh(memory)
    return memory


@router.get("/", response_model=list[MemoryResponse])
async def list_memories(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    memory_type: Optional[MemoryType] = Query(default=None),
    source_type: Optional[str] = Query(default=None),
    is_archived: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[Memory]:
    """List memories for the current user with optional filters."""
    stmt = select(Memory).where(
        Memory.user_id == current_user.id,
        Memory.is_active == True,  # noqa: E712
        Memory.is_archived == is_archived,
    )
    if memory_type:
        stmt = stmt.where(Memory.memory_type == memory_type)
    if source_type:
        stmt = stmt.where(Memory.source_type == source_type)

    stmt = stmt.order_by(Memory.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Memory:
    """Retrieve a single memory by ID."""
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == current_user.id,
            Memory.is_active == True,  # noqa: E712
        )
    )
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
    return memory


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: uuid.UUID,
    payload: MemoryUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> Memory:
    """Update a memory's content or metadata."""
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == current_user.id,
            Memory.is_active == True,  # noqa: E712
        )
    )
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(memory, field, value)

    await db.flush()
    await db.refresh(memory)
    return memory


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete a memory (sets is_active=False)."""
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == current_user.id,
            Memory.is_active == True,  # noqa: E712
        )
    )
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")

    memory.is_active = False
    await db.flush()


@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(
    payload: MemorySearchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> MemorySearchResponse:
    """Keyword-based memory search (simplified semantic search fallback)."""
    query_lower = payload.query.lower()
    stmt = select(Memory).where(
        Memory.user_id == current_user.id,
        Memory.is_active == True,  # noqa: E712
        Memory.content.ilike(f"%{query_lower}%"),
    ).order_by(Memory.salience_score.desc()).limit(payload.limit)

    result = await db.execute(stmt)
    memories = list(result.scalars().all())
    return MemorySearchResponse(memories=memories, total=len(memories))
