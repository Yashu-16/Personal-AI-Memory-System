"""Models package – import all models so SQLAlchemy registers them."""

from app.models.audit_log import AuditLog  # noqa: F401
from app.models.commitment import Commitment, CommitmentStatus  # noqa: F401
from app.models.entity import Entity, EntityType, MemoryEntityLink  # noqa: F401
from app.models.feedback import FeedbackEvent, FeedbackType  # noqa: F401
from app.models.goal import Goal  # noqa: F401
from app.models.insight import Insight, InsightType  # noqa: F401
from app.models.memory import Memory, MemoryType  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.reminder import Reminder  # noqa: F401
from app.models.source_document import SourceDocument  # noqa: F401
from app.models.task import Task, TaskPriority, TaskStatus  # noqa: F401
from app.models.user import ConnectedAccount, User  # noqa: F401

__all__ = [
    "AuditLog",
    "Commitment",
    "CommitmentStatus",
    "ConnectedAccount",
    "Entity",
    "EntityType",
    "FeedbackEvent",
    "FeedbackType",
    "Goal",
    "Insight",
    "InsightType",
    "Memory",
    "MemoryEntityLink",
    "MemoryType",
    "Project",
    "Reminder",
    "SourceDocument",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "User",
]
