from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_session
from app.repo.user import UsersRepository
from app.services.users import UsersService
from app.core.exeptions import (
    UserNotFoundError,
    InvalidCredentialsError,
)
from app.services.security import SecurityManager
from app.schemas.users import UserInfoResponse, LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ---------- Зависимость: UsersService ----------

async def get_users_service(
    session: AsyncSession = Depends(get_session),
) -> UsersService:
    repo = UsersRepository(session)
    return UsersService(repo)


# ---------- Зависимость: текущий пользователь ----------

async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    users_service: UsersService = Depends(get_users_service),
):
    """
    Достаём пользователя из JWT.

    1. Берём заголовок Authorization: Bearer <token>
    2. Декодируем JWT через SecurityManager.decode_access_token()
    3. Достаём user_id из sub и ищем пользователя через UsersService
    4. При любой проблеме -> 403 "JWT not found"
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT not found",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT not found",
        )

    token = parts[1]

    try:
        payload = SecurityManager.decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="JWT not found",
            )
        user_id = int(sub)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT not found",
        )

    try:
        user = await users_service.get_user_by_id(user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT not found",
        )

    return user


# ---------- Эндпоинты ----------

@router.post(
    "/login",
    status_code=status.HTTP_201_CREATED,
    response_model=TokenResponse,
)
async def login(
    credentials: LoginRequest,
    users_service: UsersService = Depends(get_users_service),
):
    """
    POST /api/auth/login

    body:
    {
        "login": "login",
        "password": "password"
    }

    201:
    {
        "token": "token"
    }

    404: "NOT FOUND"
    401: "wrong login or password"
    """
    # Сначала проверяем, что пользователь с таким логином существует
    try:
        await users_service.get_user_by_login(credentials.login)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )

    # Теперь проверяем пароль через сервис
    try:
        user = await users_service.authenticate_user(
            login=credentials.login,
            password=credentials.password,
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="wrong login or password",
        )

    token = SecurityManager.create_access_token(subject=str(user.id))
    return TokenResponse(token=token)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=UserInfoResponse,
)
async def get_me(
    user=Depends(get_current_user),
):
    """
    GET /api/auth/

    Header:
    Authorization: Bearer <token>

    200:
    {
        "username": "username",
        "login": "login"
    }

    403: "JWT not found"
    """
    return UserInfoResponse(
        username=user.username,
        login=user.login,
    )


@router.get(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    user=Depends(get_current_user),
):
    """
    GET /api/auth/logout

    Header:
    Authorization: Bearer <token>

    200: {}
    403: "JWT not found"

    Здесь просто «забываем» JWT на стороне клиента.
    """
    return {}
