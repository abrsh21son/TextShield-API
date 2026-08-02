"""API key authentication helpers."""

from __future__ import annotations

from flask import Request
from sqlmodel import Session, select

import config
from utility.database.model import APIKey, User


def resolve_user_from_api_key(db: Session, request: Request) -> tuple[User | None, str | None]:
    api_key = request.headers.get("x-api-key", "").strip()
    if not api_key:
        return None, "Missing x-api-key header"

    if config.DEMO_API_KEY and api_key == config.DEMO_API_KEY:
        demo_user = db.exec(select(User).order_by(User.createdat)).first()
        if demo_user:
            return demo_user, None
        return None, "Demo user not configured"

    row = db.exec(
        select(APIKey, User)
        .join(User, APIKey.userid == User.id)
        .where(APIKey.thekey == api_key, APIKey.isactive == True)  # noqa: E712
    ).first()

    if not row:
        return None, "Invalid or inactive API key"

    _, user = row
    if user.credits <= 0:
        return None, "Insufficient credits"

    return user, None
