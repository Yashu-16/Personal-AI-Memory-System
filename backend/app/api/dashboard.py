"""Dashboard API endpoints."""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.commitment import Commitment, CommitmentStatus
from app.models.insight import Insight
from app.models.memory import Memory
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.memory import MemoryResponse

router = APIRouter()


@router.get("/summary")
async def daily_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return a daily dashboard summary."""
    now = datetime.now(timezone.utc)

    # Overdue commitments
    overdue_result = await db.execute(
        select(func.count()).select_from(Commitment).where(
            Commitment.user_id == current_user.id,
            Commitment.status == CommitmentStatus.pending,
            Commitment.deadline < now,
        )
    )
    overdue_count: int = overdue_result.scalar_one()

    # Pending tasks
    pending_tasks_result = await db.execute(
        select(func.count()).select_from(Task).where(
            Task.user_id == current_user.id,
            Task.status == TaskStatus.todo,
        )
    )
    pending_tasks_count: int = pending_tasks_result.scalar_one()

    # Unread insights
    unread_insights_result = await db.execute(
        select(func.count()).select_from(Insight).where(
            Insight.user_id == current_user.id,
            Insight.is_read == False,  # noqa: E712
        )
    )
    unread_insights_count: int = unread_insights_result.scalar_one()

    # Recent memories (last 5)
    recent_result = await db.execute(
        select(Memory)
        .where(Memory.user_id == current_user.id, Memory.is_active == True)  # noqa: E712
        .order_by(Memory.created_at.desc())
        .limit(5)
    )
    recent_memories = [MemoryResponse.model_validate(m) for m in recent_result.scalars().all()]

    return {
        "overdue_commitments": overdue_count,
        "pending_tasks": pending_tasks_count,
        "unread_insights": unread_insights_count,
        "recent_memories": recent_memories,
        "generated_at": now.isoformat(),
    }


@router.get("/weekly-review")
async def weekly_review(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return a weekly review summary."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    # Memories created this week
    mem_result = await db.execute(
        select(func.count()).select_from(Memory).where(
            Memory.user_id == current_user.id,
            Memory.is_active == True,  # noqa: E712
            Memory.created_at >= week_ago,
        )
    )
    memories_count: int = mem_result.scalar_one()

    # Completed commitments
    completed_result = await db.execute(
        select(func.count()).select_from(Commitment).where(
            Commitment.user_id == current_user.id,
            Commitment.status == CommitmentStatus.completed,
            Commitment.updated_at >= week_ago,
        )
    )
    completed_commitments: int = completed_result.scalar_one()

    # Completed tasks
    done_tasks_result = await db.execute(
        select(func.count()).select_from(Task).where(
            Task.user_id == current_user.id,
            Task.status == TaskStatus.done,
            Task.updated_at >= week_ago,
        )
    )
    done_tasks: int = done_tasks_result.scalar_one()

    return {
        "period_start": week_ago.isoformat(),
        "period_end": now.isoformat(),
        "memories_created": memories_count,
        "commitments_completed": completed_commitments,
        "tasks_completed": done_tasks,
    }


@router.get("/timeline")
async def memory_timeline(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return memories grouped by date for a timeline view."""
    result = await db.execute(
        select(Memory)
        .where(Memory.user_id == current_user.id, Memory.is_active == True)  # noqa: E712
        .order_by(Memory.created_at.desc())
        .limit(100)
    )
    memories = result.scalars().all()

    # Group by date
    grouped: dict[str, list[MemoryResponse]] = {}
    for mem in memories:
        date_key = mem.created_at.date().isoformat() if mem.created_at else "unknown"
        if date_key not in grouped:
            grouped[date_key] = []
        grouped[date_key].append(MemoryResponse.model_validate(mem))

    return {"timeline": grouped}
