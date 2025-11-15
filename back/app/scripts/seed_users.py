# app/scripts/seed_users.py

import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.session import engine
from app.core.db import Base
from app.repo.user import UsersRepository
from app.services.users import UsersService
from app.core.exeptions import UserAlreadyExistsError


async def init_db() -> None:
    """На всякий случай создаём таблицы (идемпотентно)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_users() -> None:
    """Создаёт тестовых пользователей через UsersService."""
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session_maker() as session:
        users_repo = UsersRepository(session)
        users_service = UsersService(users_repo)

        users_data = [
            {
                "username": "Admin",
                "login": "admin",
                "password": "admin12345",
            },
            {
                "username": "Test User",
                "login": "test",
                "password": "test12345",
            },
        ]

        for data in users_data:
            try:
                user = await users_service.register_user(
                    username=data["username"],
                    login=data["login"],
                    password=data["password"],
                )
                print(f"✅ Created user: id={user.id}, login={user.login}")
            except UserAlreadyExistsError:
                print(f"⚠ User with login={data['login']} already exists, skip")


async def main() -> None:
    await init_db()
    await seed_users()


if __name__ == "__main__":
    asyncio.run(main())
