import asyncio
import getpass
import sys

from sqlalchemy import select

from app.database.session import AsyncSessionLocal
from app.models.user import User
from app.services.auth import hash_password


async def create_user(email: str, password: str, full_name: str) -> None:
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(User).where(User.email == email))
        if existing.scalar_one_or_none() is not None:
            print(f"User '{email}' already exists.")
            return
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )
        db.add(user)
        await db.commit()
        print(f"User '{email}' created successfully.")


def main() -> None:
    email = input("Email: ").strip()
    if not email:
        print("Email is required.")
        sys.exit(1)
    password = getpass.getpass("Password: ")
    if len(password) < 8:
        print("Password must be at least 8 characters.")
        sys.exit(1)
    full_name = input("Full name: ").strip()
    if not full_name:
        print("Full name is required.")
        sys.exit(1)
    asyncio.run(create_user(email, password, full_name))


if __name__ == "__main__":
    main()
