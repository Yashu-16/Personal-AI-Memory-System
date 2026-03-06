"""Query request / response schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.memory import MemoryResponse


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, description="Natural language query")
    max_results: Optional[int] = Field(default=10, ge=1, le=50)


class QueryResponse(BaseModel):
    answer: str
    supporting_memories: list[MemoryResponse]
    confidence: float = Field(ge=0.0, le=1.0)
    suggested_actions: list[str]
    query_intent: str
