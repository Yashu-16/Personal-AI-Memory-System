"""Privacy service – data deletion, export, and audit logging."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.commitment import Commitment
from app.models.entity import Entity, MemoryEntityLink
from app.models.feedback import FeedbackEvent
from app.models.insight import Insight
from app.models.memory import Memory
from app.models.reminder import Reminder
from app.models.source_document import SourceDocument
from app.models.task import Task
from app.models.user import ConnectedAccount, User


class PrivacyService:
    """Handle GDPR-style data operations."""

    async def delete_all_user_data(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> bool:
        """Delete all data associated with *user_id*."""
        try:
            # Delete child tables first (cascade should handle most, but be explicit)
            for model in [
                FeedbackEvent,
                Reminder,
                MemoryEntityLink,
                Insight,
                Commitment,
                Task,
                Memory,
                Entity,
                SourceDocument,
                ConnectedAccount,
                AuditLog,
            ]:
                await db.execute(
                    delete(model).where(getattr(model, "user_id", None) == user_id)  # type: ignore[arg-type]
                )
            # Finally delete user
            await db.execute(delete(User).where(User.id == user_id))
            await db.flush()
            return True
        except Exception:
            await db.rollback()
            return False

    async def export_user_data(
        self,
        user_id: uuid.UUID,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Export all user data as a JSON-serialisable dict."""

        async def fetch(model, attr: str = "user_id") -> list[dict]:
            result = await db.execute(
                select(model).where(getattr(model, attr) == user_id)
            )
            rows = result.scalars().all()
            return [
                {c.key: getattr(row, c.key) for c in model.__table__.columns}  # type: ignore[attr-defined]
                for row in rows
            ]

        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        export: dict[str, Any] = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "user": (
                {c.key: str(getattr(user, c.key)) for c in User.__table__.columns}  # type: ignore[attr-defined]
                if user
                else None
            ),
            "memories": await fetch(Memory),
            "source_documents": await fetch(SourceDocument),
            "commitments": await fetch(Commitment),
            "tasks": await fetch(Task),
            "insights": await fetch(Insight),
            "connected_accounts": await fetch(ConnectedAccount),
        }
        return export

    async def log_audit(
        self,
        user_id: uuid.UUID | None,
        action: str,
        resource_type: str,
        resource_id: str | None,
        details: dict[str, Any],
        db: AsyncSession,
        ip_address: str | None = None,
    ) -> None:
        """Append an audit log entry."""
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )
        db.add(log)
        await db.flush()
