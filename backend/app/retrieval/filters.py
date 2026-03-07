"""Memory filter builder for SQLAlchemy queries."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Select, and_

from app.models.memory import Memory, MemoryType


class MemoryFilters:
    """Build SQLAlchemy filter conditions for memory queries."""

    @staticmethod
    def apply(
        stmt: Select,
        time_range: Optional[tuple[Optional[datetime], Optional[datetime]]] = None,
        source_types: Optional[list[str]] = None,
        memory_types: Optional[list[MemoryType]] = None,
        entity_ids: Optional[list] = None,
    ) -> Select:
        """Apply filters to *stmt* and return the updated statement."""
        conditions = []

        if time_range:
            start, end = time_range
            if start:
                conditions.append(Memory.created_at >= start)
            if end:
                conditions.append(Memory.created_at <= end)

        if source_types:
            conditions.append(Memory.source_type.in_(source_types))

        if memory_types:
            conditions.append(Memory.memory_type.in_(memory_types))

        if entity_ids:
            from app.models.entity import MemoryEntityLink  # noqa: PLC0415

            stmt = stmt.join(
                MemoryEntityLink,
                Memory.id == MemoryEntityLink.memory_id,
            ).where(MemoryEntityLink.entity_id.in_(entity_ids))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        return stmt
