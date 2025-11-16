from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import UsersORM
from app.core.logger import get_logger

logger = get_logger(__name__)


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
        logger.debug(f"Creating user in database: login={login}")
        try:
            user = UsersORM(
                username=username,
                login=login,
                hash_password=hash_password,
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            logger.debug(f"User created in database: id={user.id}, login={login}")
            return user
        except Exception as e:
            logger.error(f"Failed to create user in database: login={login}, error={e}", exc_info=True)
            await self.session.rollback()
            raise

    # ---------- Обновление ----------

    async def update(
        self,
        user_id: int,
        *,
        username: Optional[str] = None,
        login: Optional[str] = None,
        hash_password: Optional[str] = None,
    ) -> Optional[UsersORM]:
        logger.debug(f"Updating user in database: id={user_id}")
        try:
            user = await self.get_by_id(user_id)
            if not user:
                logger.debug(f"User not found for update: id={user_id}")
                return None

            if username is not None:
                user.username = username
            if login is not None:
                user.login = login
            if hash_password is not None:
                user.hash_password = hash_password

            await self.session.commit()
            await self.session.refresh(user)
            logger.debug(f"User updated in database: id={user_id}")
            return user
        except Exception as e:
            logger.error(f"Failed to update user in database: id={user_id}, error={e}", exc_info=True)
            await self.session.rollback()
            raise

    # ---------- Удаление ----------

    async def delete(self, user_id: int) -> bool:
        logger.debug(f"Deleting user from database: id={user_id}")
        try:
            user = await self.get_by_id(user_id)
            if not user:
                logger.debug(f"User not found for deletion: id={user_id}")
                return False

            await self.session.delete(user)
            await self.session.commit()
            logger.debug(f"User deleted from database: id={user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user from database: id={user_id}, error={e}", exc_info=True)
            await self.session.rollback()
            raise
