"""Privacy API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.common import BaseResponse
from app.services.privacy_service import PrivacyService

router = APIRouter()
_service = PrivacyService()


@router.post("/delete-all-data", response_model=BaseResponse)
async def delete_all_data(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    """Permanently delete all data belonging to the current user."""
    success = await _service.delete_all_user_data(user_id=current_user.id, db=db)
    return BaseResponse(success=success, message="All user data deleted" if success else "Deletion failed")


@router.post("/export-data")
async def export_data(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Export all user data as a JSON object."""
    return await _service.export_user_data(user_id=current_user.id, db=db)


@router.get("/audit-log")
async def audit_log(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict:
    """Return the paginated audit log for the current user."""
    from app.models.audit_log import AuditLog  # noqa: PLC0415
    from sqlalchemy import select  # noqa: PLC0415

    stmt = (
        select(AuditLog)
        .where(AuditLog.user_id == current_user.id)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return {
        "items": [
            {
                "id": str(log.id),
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "created_at": log.created_at.isoformat(),
                "ip_address": log.ip_address,
            }
            for log in logs
        ],
        "page": page,
        "page_size": page_size,
    }
