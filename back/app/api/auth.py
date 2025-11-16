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
from app.core.logger import get_logger
from app.repo.user import UsersRepository
from app.services.users import UsersService
from app.core.exeptions import (
    UserNotFoundError,
    InvalidCredentialsError,
)
from app.services.security import SecurityManager
from app.schemas.users import UserInfoResponse, LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = get_logger(__name__)


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
        logger.warning("Authentication failed: Authorization header not found")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT not found",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("Authentication failed: Invalid Authorization header format")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT not found",
        )

    token = parts[1]

    try:
        payload = SecurityManager.decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            logger.warning("Authentication failed: JWT payload missing 'sub' field")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="JWT not found",
            )
        user_id = int(sub)
    except Exception as e:
        logger.warning(f"Authentication failed: Invalid JWT token - {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT not found",
        )

    try:
        user = await users_service.get_user_by_id(user_id)
        logger.debug(f"User authenticated successfully: user_id={user_id}")
        return user
    except UserNotFoundError:
        logger.warning(f"Authentication failed: User not found - user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT not found",
        )


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
    logger.info(f"Login attempt for user: {credentials.login}")
    
    # Сначала проверяем, что пользователь с таким логином существует
    try:
        await users_service.get_user_by_login(credentials.login)
    except UserNotFoundError:
        logger.warning(f"Login failed: User not found - login={credentials.login}")
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
        logger.info(f"User authenticated successfully: user_id={user.id}, login={credentials.login}")
    except InvalidCredentialsError:
        logger.warning(f"Login failed: Invalid credentials - login={credentials.login}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="wrong login or password",
        )

    token = SecurityManager.create_access_token(subject=str(user.id))
    logger.debug(f"Access token created for user_id={user.id}")
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
    logger.debug(f"User info requested: user_id={user.id}, login={user.login}")
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
    logger.info(f"User logged out: user_id={user.id}, login={user.login}")
    return {}
