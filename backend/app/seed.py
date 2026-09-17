"""Idempotent seed: creates one ADMIN and one demo PLAYER if absent.

Run via `python -m app.seed` (the Docker entrypoint does this automatically).
"""
from __future__ import annotations

import asyncio

from app.core.logging import get_logger
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.repositories import user_repo
from app.core.config import settings

logger = get_logger("seed")


async def seed() -> None:
    accounts = [
        (settings.SEED_ADMIN_EMAIL, settings.SEED_ADMIN_PASSWORD, UserRole.ADMIN, "Case Administrator"),
        (settings.SEED_PLAYER_EMAIL, settings.SEED_PLAYER_PASSWORD, UserRole.PLAYER, "Demo Investigator"),
    ]
    async with AsyncSessionLocal() as db:
        created = 0
        for email, password, role, name in accounts:
            email = email.lower()
            if await user_repo.get_by_email(db, email) is not None:
                continue
            db.add(
                User(
                    email=email,
                    password_hash=hash_password(password),
                    role=role.value,
                    display_name=name,
                )
            )
            created += 1
        await db.commit()
    logger.info("Seed complete (%d new account(s)).", created)


if __name__ == "__main__":
    asyncio.run(seed())
