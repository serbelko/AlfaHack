# app/services/security.py

from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from app.core.config import settings  # откуда берёшь SECRET_KEY, ALGORITHM и т.д.
# если у тебя нет отдельного settings, импортируй оттуда, где лежит твой Settings

# если используешь passlib для паролей, например:
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """
    Отвечает ТОЛЬКО за:
    - хэширование / проверку паролей
    - создание / декодирование JWT

    Никаких импортов UsersService здесь быть не должно.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        # TODO: поставь свою реализацию
        # return pwd_context.hash(password)
        return password  # временная заглушка, если хэширование ещё не настроено

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # TODO: своя реализация
        # return pwd_context.verify(plain_password, hashed_password)
        return True  # заглушка

    @staticmethod
    def create_access_token(
        subject: str,
        expires_minutes: Optional[int] = None,
    ) -> str:
        if expires_minutes is None:
            expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        to_encode = {"sub": subject, "exp": expire}

        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

    @staticmethod
    def decode_access_token(token: str) -> dict:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
