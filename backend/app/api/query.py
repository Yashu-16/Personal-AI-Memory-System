"""Query endpoint – natural language question answering over memories."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import QueryService

router = APIRouter()
_service = QueryService()


@router.post("/", response_model=QueryResponse)
async def query(
    payload: QueryRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    """Process a natural language query and return a grounded answer."""
    return await _service.process_query(
        user_id=current_user.id,
        query_text=payload.query,
        db=db,
        max_results=payload.max_results or 10,
    )
