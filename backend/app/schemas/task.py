"""Task Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.medium
    deadline: Optional[datetime] = None
    project_id: Optional[uuid.UUID] = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    memory_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    deadline: Optional[datetime] = None
    project_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    deadline: Optional[datetime] = None
    project_id: Optional[uuid.UUID] = None
