"""
Create or update an admin account in the database.

Usage:
    python backend/scripts/create_admin.py --email admin@example.com --password "strong-pass"
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv
from sqlalchemy import select

# Add project root to sys.path for direct script execution.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.security import AuthService
from backend.database.models import User, UserRole
from backend.database.session import async_session


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or update admin user")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password (min 8 chars)")
    return parser.parse_args()


async def create_or_update_admin(email: str, password: str) -> tuple[str, User]:
    auth = AuthService()
    normalized_email = email.strip().lower()

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    async with async_session() as session:
        stmt = select(User).where(User.email == normalized_email)
        existing = (await session.execute(stmt)).scalars().first()

        if existing:
            existing.password_hash = auth.hash_password(password)
            existing.role = UserRole.ADMIN
            existing.token_version = (existing.token_version or 0) + 1
            action = "updated"
            user = existing
        else:
            user = User(
                email=normalized_email,
                password_hash=auth.hash_password(password),
                role=UserRole.ADMIN,
            )
            session.add(user)
            action = "created"

        await session.commit()
        await session.refresh(user)
        return action, user


async def main() -> None:
    load_dotenv()
    args = parse_args()
    action, user = await create_or_update_admin(args.email, args.password)
    print(f"Admin {action}: id={user.id} email={user.email} role={user.role.value}")


if __name__ == "__main__":
    asyncio.run(main())
