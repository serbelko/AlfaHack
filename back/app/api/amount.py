from typing import Optional
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    status,
    Query,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.session import get_mock_session
from app.repo.amount import AmountRepository
from app.schemas.amount import (
    AmountResponse,
    AmountListResponse,
    HistoryResponse,
    AmountCreateRequest,
    TransactionCreateRequest,
    TransactionItem,
)
from app.services.security import SecurityManager

router = APIRouter(prefix="/api/amount", tags=["amount"])


async def verify_token(
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """
    Проверяет JWT токен из заголовка Authorization.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT NOT FOUND",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT NOT FOUND",
        )

    token = parts[1]

    try:
        SecurityManager.decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="JWT NOT FOUND",
        )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=AmountResponse,
    dependencies=[Depends(verify_token)],
)
async def get_amount(
    name: str = Query(..., description="Имя счёта"),
    session: AsyncSession = Depends(get_mock_session),
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
    """
    repo = AmountRepository(session)
    amount = await repo.get_amount_by_name(name)
    
    if not amount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="СЧЁТ НЕ НАЙДЕН",
        )
    
    return AmountResponse(count=amount.count, name=amount.name)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=AmountListResponse,
    dependencies=[Depends(verify_token)],
)
async def get_all_amounts(
    session: AsyncSession = Depends(get_mock_session),
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
    repo = AmountRepository(session)
    amounts = await repo.get_all_amounts()
    
    amount_responses = [
        AmountResponse(count=amount.count, name=amount.name)
        for amount in amounts
    ]
    
    return AmountListResponse(
        amounts=amount_responses,
        limit_data=len(amount_responses)
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=AmountResponse,
    dependencies=[Depends(verify_token)],
)
async def create_amount(
    data: AmountCreateRequest,
    session: AsyncSession = Depends(get_mock_session),
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
    repo = AmountRepository(session)
    
    # Проверяем, не существует ли уже счёт с таким именем
    existing_amount = await repo.get_amount_by_name(data.name)
    if existing_amount:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные",
        )
    
    # Валидация суммы (не может быть отрицательной)
    if data.count < 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные",
        )
    
    try:
        amount = await repo.create_amount(data.name, data.count)
        return AmountResponse(count=amount.count, name=amount.name)
    except Exception:
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
    session: AsyncSession = Depends(get_mock_session),
):
    """
    GET /api/amount/transaction?name=string - данные об одной транзакции
    
    Authorization: Bearer 'token'
    
    Response 200: данные последней транзакции
    Response 403: JWT NOT FOUND
    Response 404: СЧЁТ НЕ НАЙДЕН
    """
    repo = AmountRepository(session)
    amount = await repo.get_amount_by_name(name)
    
    if not amount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="СЧЁТ НЕ НАЙДЕН",
        )
    
    transaction = await repo.get_latest_transaction(amount.id)
    
    if not transaction:
        return {}
    
    return {
        "type": transaction.type,
        "category": transaction.category,
        "count": transaction.count,
    }


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
    session: AsyncSession = Depends(get_mock_session),
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
    """
    # Проверка типа транзакции
    if type and type not in ['input', 'output', 'income', 'outcome']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect type of request",
        )
    
    # Преобразуем input/output в income/outcome для внутреннего использования
    transaction_type = None
    if type == 'input':
        transaction_type = 'income'
    elif type == 'output':
        transaction_type = 'outcome'
    elif type in ['income', 'outcome']:
        transaction_type = type
    
    repo = AmountRepository(session)
    amount = await repo.get_amount_by_name(name)
    
    if not amount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="СЧЁТ НЕ НАЙДЕН",
        )
    
    # Парсим даты
    from_dt = None
    to_dt = None
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect type of request",
            )
    if to_date:
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            # Добавляем время конца дня
            to_dt = to_dt.replace(hour=23, minute=59, second=59)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect type of request",
            )
    
    transactions = await repo.get_transactions(
        amount.id,
        from_date=from_dt,
        to_date=to_dt,
        transaction_type=transaction_type
    )
    
    transaction_items = [
        TransactionItem(
            type=trans.type,
            category=trans.category,
            count=trans.count
        )
        for trans in transactions
    ]
    
    return HistoryResponse(
        name=amount.name,
        transaction=transaction_items,
        limit_data=len(transaction_items)
    )


@router.post(
    "/transaction",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_token)],
)
async def create_transaction(
    data: TransactionCreateRequest,
    session: AsyncSession = Depends(get_mock_session),
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
    # Валидация типа транзакции
    if data.type not in ['income', 'outcome']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные",
        )
    
    # Валидация суммы
    if data.count <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные",
        )
    
    repo = AmountRepository(session)
    amount = await repo.get_amount_by_name(data.name)
    
    if not amount:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="СЧЁТ НЕ НАЙДЕН",
        )
    
    try:
        await repo.create_transaction(
            amount.id,
            data.type,
            data.category,
            data.count
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные",
        )
    
    return {}

