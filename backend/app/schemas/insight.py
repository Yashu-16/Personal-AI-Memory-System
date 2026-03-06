"""Insight Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.insight import InsightType


class InsightResponse(BaseModel):
    id: uuid.UUID
    insight_type: InsightType
    title: str
    content: str
    urgency: str
    is_read: bool
    created_at: datetime
    supporting_memory_ids: list[Any]

    model_config = {"from_attributes": True}
