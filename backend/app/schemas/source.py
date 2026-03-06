"""Source / connector Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ConnectedSourceResponse(BaseModel):
    id: uuid.UUID
    source_type: str
    is_active: bool
    last_sync_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConnectSourceRequest(BaseModel):
    source_type: str
    credentials: dict[str, Any]


class SyncResponse(BaseModel):
    message: str
    source_id: uuid.UUID
