from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    status,
    Query,
    Security,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_mock_session
from app.core.logger import get_logger
from app.repo.amount import AmountRepository
from app.services.amount import AmountService
from app.core.exeptions import (
    AmountNotFoundError,
    AmountAlreadyExistsError,
    InvalidAmountDataError,
    InvalidTransactionDataError,
)
from app.schemas.amount import (
    AmountResponse,
    AmountListResponse,
    HistoryResponse,
    AmountCreateRequest,
    TransactionCreateRequest,
)
from app.services.security import SecurityManager

router = APIRouter(prefix="/api/amount", tags=["amount"])
logger = get_logger(__name__)

# Схема безопасности для Swagger UI
security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """
    Проверяет JWT токен из заголовка Authorization.
    Использует HTTPBearer для автоматической интеграции со Swagger UI.
    """
    token = credentials.credentials

    try:
        SecurityManager.decode_access_token(token)
        logger.debug("Token verified successfully")
    except Exception as e:
        logger.warning(f"Token verification failed: Invalid token - {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT NOT FOUND",
        )


# ---------- Зависимость: AmountService ----------

async def get_amount_service(
    session: AsyncSession = Depends(get_mock_session),
) -> AmountService:
    """
    Создаёт экземпляр AmountService с репозиторием.
    """
    repo = AmountRepository(session)
    return AmountService(repo)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=AmountResponse,
    dependencies=[Depends(verify_token)],
)
async def get_amount(
    name: str = Query(..., description="Имя счёта"),
    amount_service: AmountService = Depends(get_amount_service),
):
    """
    GET /api/amount?name=string - данные по счёту
    
    Authorization: Bearer 'token'
    
    Response 200:
    {
        "count": 123,
        "name": "string"
    }
    
    Response 403: JWT NOT FOUND
    Response 404: СЧЁТ НЕ НАЙДЕН
    """
    try:
        amount = await amount_service.get_amount_by_name(name)
        return AmountResponse(count=amount.count, name=amount.name)
    except AmountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="СЧЁТ НЕ НАЙДЕН",
        )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=AmountListResponse,
    dependencies=[Depends(verify_token)],
)
async def get_all_amounts(
    amount_service: AmountService = Depends(get_amount_service),
):
    """
    GET /api/amount/
    
    Authorization: Bearer 'token'
    
    Response 200:
    {
        "amounts": [
            {"count": 123, "name": "string"}
        ],
        "limit_data": 1
    }
    
    Response 403: JWT NOT FOUND
    """
    return await amount_service.get_all_amounts()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=AmountResponse,
    dependencies=[Depends(verify_token)],
)
async def create_amount(
    data: AmountCreateRequest,
    amount_service: AmountService = Depends(get_amount_service),
):
    """
    POST /api/amount - создать новый счёт
    
    Authorization: Bearer 'token'
    
    Body:
    {
        "name": "имя счёта",
        "count": 0.0  # начальный баланс (опционально, по умолчанию 0.0)
    }
    
    Response 201:
    {
        "count": 0.0,
        "name": "string"
    }
    
    Response 403: JWT NOT FOUND
    Response 401: Некорректные данные (если счёт с таким именем уже существует)
    """
    try:
        amount = await amount_service.create_amount(data.name, data.count)
        return AmountResponse(count=amount.count, name=amount.name)
    except AmountAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные",
        )
    except InvalidAmountDataError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные",
        )


@router.get(
    "/transaction",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_token)],
)
async def get_transaction(
    name: str = Query(..., description="Имя счёта"),
    amount_service: AmountService = Depends(get_amount_service),
):
    """
    GET /api/amount/transaction?name=string - данные об одной транзакции
    
    Authorization: Bearer 'token'
    
    Response 200: данные последней транзакции
    Response 403: JWT NOT FOUND
    Response 404: СЧЁТ НЕ НАЙДЕН
    """
    try:
        transaction = await amount_service.get_latest_transaction(name)
        return transaction if transaction else {}
    except AmountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="СЧЁТ НЕ НАЙДЕН",
        )


@router.get(
    "/history",
    status_code=status.HTTP_200_OK,
    response_model=HistoryResponse,
    dependencies=[Depends(verify_token)],
)
async def get_history(
    name: str = Query(..., description="Имя счёта"),
    from_date: Optional[str] = Query(None, description="Начало периода (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Конец периода (YYYY-MM-DD)"),
    type: Optional[str] = Query(None, description="Тип транзакции (input/outcome)"),
    amount_service: AmountService = Depends(get_amount_service),
):
    """
    GET /api/amount/history?name=string&from=date&to=date&type=string
    
    Authorization: Bearer 'token'
    
    Response 200:
    {
        "name": "string",
        "transaction": [
            {"type": "string", "category": "string", "count": 123.45}
        ],
        "limit_data": 1
    }
    
    Response 403: JWT NOT FOUND
    Response 401: Incorrect type of request
    Response 404: СЧЁТ НЕ НАЙДЕН
    """
    try:
        return await amount_service.get_transaction_history(
            account_name=name,
            from_date=from_date,
            to_date=to_date,
            transaction_type=type,
        )
    except AmountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="СЧЁТ НЕ НАЙДЕН",
        )
    except InvalidTransactionDataError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect type of request",
        )


@router.post(
    "/transaction",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_token)],
)
async def create_transaction(
    data: TransactionCreateRequest,
    amount_service: AmountService = Depends(get_amount_service),
):
    """
    POST /api/amount/transaction - добавить новую транзакцию
    
    Authorization: Bearer 'token'
    
    Body:
    {
        "name": "имя счёта",
        "type": "тип транзакции (income/outcome)",
        "category": "категория транзакции",
        "count": 123.45
    }
    
    Response 200: {}
    Response 403: JWT NOT FOUND
    Response 404: СЧЁТ НЕ НАЙДЕН
    Response 401: Некорректные данные
    """
    try:
        await amount_service.create_transaction(
            account_name=data.name,
            transaction_type=data.type,
            category=data.category,
            count=data.count,
        )
        return {}
    except AmountNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="СЧЁТ НЕ НАЙДЕН",
        )
    except InvalidTransactionDataError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные",
        )

