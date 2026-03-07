"""Memory Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.memory import MemoryType


class MemoryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    memory_type: MemoryType
    content: str
    summary: Optional[str] = None
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    confidence: float
    salience_score: float
    is_active: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MemoryCreate(BaseModel):
    model_config = {"extra": "ignore"}

    memory_type: MemoryType = MemoryType.fact
    content: str = Field(min_length=1)
    summary: Optional[str] = None
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    salience_score: float = Field(default=0.5, ge=0.0, le=1.0)


class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    summary: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    salience_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    is_archived: Optional[bool] = None


class MemorySearchRequest(BaseModel):
    query: str = Field(min_length=1)
    filters: Optional[dict[str, Any]] = None
    limit: int = Field(default=20, ge=1, le=100)


class MemorySearchResponse(BaseModel):
    memories: list[MemoryResponse]
    total: int
