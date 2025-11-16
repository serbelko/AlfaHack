from typing import Optional, List

from app.repo.user import UsersRepository
from app.core.db import UsersORM
from app.core.logger import get_logger
from app.core.exeptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
)
from app.services.security import SecurityManager

logger = get_logger(__name__)


class UsersService:
    """
    Сервис для работы с пользователями.
    Здесь бизнес-логика, проверки, ошибки.
    К базе ходит только через UsersRepository.
    """

    def __init__(self, users_repo: UsersRepository) -> None:
        self.users_repo = users_repo

    # ---------- Чтение ----------

    async def get_user_by_id(self, user_id: int) -> UsersORM:
        logger.debug(f"Getting user by id: {user_id}")
        user = await self.users_repo.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found by id: {user_id}")
            raise UserNotFoundError(f"User with id={user_id} not found")
        logger.debug(f"User found: id={user_id}, login={user.login}")
        return user

    async def get_user_by_login(self, login: str) -> UsersORM:
        logger.debug(f"Getting user by login: {login}")
        user = await self.users_repo.get_by_login(login)
        if not user:
            logger.warning(f"User not found by login: {login}")
            raise UserNotFoundError(f"User with login={login} not found")
        logger.debug(f"User found: id={user.id}, login={login}")
        return user

    async def list_users(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> List[UsersORM]:
        return await self.users_repo.list(offset=offset, limit=limit)

    # ---------- Регистрация / аутентификация ----------

    async def register_user(
        self,
        *,
        username: str,
        login: str,
        password: str,
    ) -> UsersORM:
        logger.info(f"Registering new user: login={login}, username={username}")
        # Проверяем, что логин свободен
        existing = await self.users_repo.get_by_login(login)
        if existing:
            logger.warning(f"User registration failed: Login already exists - login={login}")
            raise UserAlreadyExistsError(
                f"User with login={login} already exists"
            )

        hashed = SecurityManager.hash_password(password)
        user = await self.users_repo.create(
            username=username,
            login=login,
            hash_password=hashed,
        )
        logger.info(f"User registered successfully: id={user.id}, login={login}")
        return user

    async def authenticate_user(
        self,
        *,
        login: str,
        password: str,
    ) -> UsersORM:
        logger.debug(f"Authenticating user: login={login}")
        user = await self.users_repo.get_by_login(login)
        if not user:
            # логин не существует
            logger.warning(f"Authentication failed: User not found - login={login}")
            raise InvalidCredentialsError("Invalid login or password")

        if not SecurityManager.verify_password(password, user.hash_password):
            # пароль не совпал
            logger.warning(f"Authentication failed: Invalid password - login={login}")
            raise InvalidCredentialsError("Invalid login or password")

        logger.debug(f"User authenticated successfully: id={user.id}, login={login}")
        return user

    # ---------- Обновление ----------

    async def update_user(
        self,
        user_id: int,
        *,
        username: Optional[str] = None,
        login: Optional[str] = None,
        password: Optional[str] = None,
    ) -> UsersORM:
        logger.info(f"Updating user: id={user_id}, username={username}, login={login}")
        # Можно добавить отдельные проверки, например уникальность login
        new_hash: Optional[str] = None
        if password is not None:
            new_hash = SecurityManager.hash_password(password)
            logger.debug(f"Password hash generated for user: id={user_id}")

        user = await self.users_repo.update(
            user_id=user_id,
            username=username,
            login=login,
            hash_password=new_hash,
        )
        if not user:
            logger.warning(f"User update failed: User not found - id={user_id}")
            raise UserNotFoundError(f"User with id={user_id} not found")
        logger.info(f"User updated successfully: id={user_id}")
        return user

    # ---------- Удаление ----------

    async def delete_user(self, user_id: int) -> None:
        logger.info(f"Deleting user: id={user_id}")
        ok = await self.users_repo.delete(user_id)
        if not ok:
            logger.warning(f"User deletion failed: User not found - id={user_id}")
            raise UserNotFoundError(f"User with id={user_id} not found")
        logger.info(f"User deleted successfully: id={user_id}")
