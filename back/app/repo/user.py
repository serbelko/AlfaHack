from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import UsersORM 


class UsersRepository:
    """Репозиторий для работы с таблицей users"""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------- Чтение ----------

    async def get_by_id(self, user_id: int) -> Optional[UsersORM]:
        return await self.session.get(UsersORM, user_id)

    async def get_by_login(self, login: str) -> Optional[UsersORM]:
        stmt = select(UsersORM).where(UsersORM.login == login)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, offset: int = 0, limit: int = 100) -> List[UsersORM]:
        stmt = (
            select(UsersORM)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ---------- Создание ----------

    async def create(
        self,
        *,
        username: str,
        login: str,
        hash_password: str,
    ) -> UsersORM:
        user = UsersORM(
            username=username,
            login=login,
            hash_password=hash_password,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    # ---------- Обновление ----------

    async def update(
        self,
        user_id: int,
        *,
        username: Optional[str] = None,
        login: Optional[str] = None,
        hash_password: Optional[str] = None,
    ) -> Optional[UsersORM]:
        user = await self.get_by_id(user_id)
        if not user:
            return None

        if username is not None:
            user.username = username
        if login is not None:
            user.login = login
        if hash_password is not None:
            user.hash_password = hash_password

        await self.session.commit()
        await self.session.refresh(user)
        return user

    # ---------- Удаление ----------

    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True
