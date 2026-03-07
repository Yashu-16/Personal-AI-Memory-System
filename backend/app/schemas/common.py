"""Common reusable Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class PaginationParams(BaseModel):
    """Standard pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def offset(self) -> int:
        """Compute the SQL offset from page and page_size."""
        return (self.page - 1) * self.page_size


class DateRangeFilter(BaseModel):
    """Filter by a date/time range."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BaseResponse(BaseModel):
    """Minimal success/failure wrapper."""

    success: bool = True
    message: str = ""
