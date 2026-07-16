"""Refresh-token records — the state that makes refresh tokens revocable.

Each issued refresh token has a row (id = the token's `jti` claim). Rotation
issues a new row in the same `family_id` and marks the old one revoked +
`replaced_by_id`. Presenting an already-revoked token is reuse (theft/replay)
→ the whole family is revoked, forcing a fresh login. Logout revokes the
family; a password reset revokes every family for the user.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, generate_uuid


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)  # = jti
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    family_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    replaced_by_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
