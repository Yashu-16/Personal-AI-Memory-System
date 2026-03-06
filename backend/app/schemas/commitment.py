"""Commitment Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.commitment import CommitmentStatus


class CommitmentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    memory_id: Optional[uuid.UUID] = None
    subject: str
    action: str
    person_id: Optional[uuid.UUID] = None
    deadline: Optional[datetime] = None
    status: CommitmentStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommitmentUpdate(BaseModel):
    status: CommitmentStatus


class CommitmentFilter(BaseModel):
    status: Optional[CommitmentStatus] = None
    person_id: Optional[uuid.UUID] = None
    deadline_before: Optional[datetime] = None
    deadline_after: Optional[datetime] = None
