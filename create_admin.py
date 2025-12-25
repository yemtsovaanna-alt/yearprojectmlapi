import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker, initialize_database
from app.models import User
from app.auth import get_password_hash


async def create_admin_user(username: str, password: str):
    await initialize_database()

    async with async_session_maker() as session:
        admin_user = User(
            username=username,
            hashed_password=get_password_hash(password),
            is_admin=True
        )
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        print(f"Admin user created successfully!")
        print(f"Username: {admin_user.username}")
        print(f"ID: {admin_user.id}")
        print(f"Is Admin: {admin_user.is_admin}")


if __name__ == "__main__":
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")

    asyncio.run(create_admin_user(username, password))
