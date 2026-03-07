"""Authentication service."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate


class AuthService:
    """High-level authentication operations."""

    async def create_user(self, user_data: UserCreate, db: AsyncSession) -> User:
        """Create and persist a new user."""
        user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def authenticate_user(
        self, email: str, password: str, db: AsyncSession
    ) -> Optional[User]:
        """Verify credentials and return the User or None."""
        result = await db.execute(
            select(User).where(User.email == email, User.is_active == True)  # noqa: E712
        )
        user = result.scalar_one_or_none()
        if user is None or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_tokens(self, user_id: uuid.UUID) -> TokenResponse:
        """Create an access + refresh token pair."""
        return TokenResponse(
            access_token=create_access_token(str(user_id)),
            refresh_token=create_refresh_token(str(user_id)),
        )

    def verify_token(self, token: str) -> dict:
        """Decode and return token claims."""
        return decode_token(token)

    def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Exchange a refresh token for a new pair."""
        payload = decode_token(refresh_token)
        user_id_str: str = payload.get("sub", "")
        return TokenResponse(
            access_token=create_access_token(user_id_str),
            refresh_token=create_refresh_token(user_id_str),
        )
