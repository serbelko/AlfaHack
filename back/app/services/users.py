from typing import Optional, List

from app.repo.user import UsersRepository
from app.core.db import UsersORM
from app.core.exeptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
)
from app.services.security import SecurityManager


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
        user = await self.users_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id={user_id} not found")
        return user

    async def get_user_by_login(self, login: str) -> UsersORM:
        user = await self.users_repo.get_by_login(login)
        if not user:
            raise UserNotFoundError(f"User with login={login} not found")
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
        # Проверяем, что логин свободен
        existing = await self.users_repo.get_by_login(login)
        if existing:
            raise UserAlreadyExistsError(
                f"User with login={login} already exists"
            )

        hashed = SecurityManager.hash_password(password)
        user = await self.users_repo.create(
            username=username,
            login=login,
            hash_password=hashed,
        )
        return user

    async def authenticate_user(
        self,
        *,
        login: str,
        password: str,
    ) -> UsersORM:
        user = await self.users_repo.get_by_login(login)
        if not user:
            # логин не существует
            raise InvalidCredentialsError("Invalid login or password")

        if not SecurityManager.verify_password(password, user.hash_password):
            # пароль не совпал
            raise InvalidCredentialsError("Invalid login or password")

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
        # Можно добавить отдельные проверки, например уникальность login
        new_hash: Optional[str] = None
        if password is not None:
            new_hash = SecurityManager.hash_password(password)

        user = await self.users_repo.update(
            user_id=user_id,
            username=username,
            login=login,
            hash_password=new_hash,
        )
        if not user:
            raise UserNotFoundError(f"User with id={user_id} not found")
        return user

    # ---------- Удаление ----------

    async def delete_user(self, user_id: int) -> None:
        ok = await self.users_repo.delete(user_id)
        if not ok:
            raise UserNotFoundError(f"User with id={user_id} not found")
