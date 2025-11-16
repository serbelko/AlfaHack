"""
Сервис для работы со счетами и транзакциями.
Содержит бизнес-логику работы с amount.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.repo.amount import AmountRepository
from app.core.db import AmountORM, TransactionORM
from app.core.logger import get_logger
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
    TransactionItem,
)

logger = get_logger(__name__)


class AmountService:
    """
    Сервис для работы со счетами и транзакциями.
    Здесь бизнес-логика, проверки, валидация.
    К базе ходит только через AmountRepository.
    """

    def __init__(self, amount_repo: AmountRepository) -> None:
        self.amount_repo = amount_repo

    # ---------- Работа со счетами ----------

    async def get_amount_by_name(self, name: str) -> AmountORM:
        """
        Получить счёт по имени.
        
        Args:
            name: Имя счёта
            
        Returns:
            Объект счёта
            
        Raises:
            AmountNotFoundError: Если счёт не найден
        """
        logger.debug(f"Getting amount by name: {name}")
        amount = await self.amount_repo.get_amount_by_name(name)
        if not amount:
            logger.warning(f"Amount not found: {name}")
            raise AmountNotFoundError(f"Amount with name={name} not found")
        logger.debug(f"Amount found: name={name}, count={amount.count}")
        return amount

    async def get_all_amounts(self) -> AmountListResponse:
        """
        Получить все счета.
        
        Returns:
            Список всех счетов
        """
        logger.debug("Getting all amounts")
        amounts = await self.amount_repo.get_all_amounts()
        
        amount_responses = [
            AmountResponse(count=amount.count, name=amount.name)
            for amount in amounts
        ]
        
        logger.debug(f"Retrieved {len(amount_responses)} amounts")
        return AmountListResponse(
            amounts=amount_responses,
            limit_data=len(amount_responses)
        )

    async def create_amount(self, name: str, count: float = 0.0) -> AmountORM:
        """
        Создать новый счёт.
        
        Args:
            name: Имя счёта
            count: Начальный баланс (по умолчанию 0.0)
            
        Returns:
            Созданный счёт
            
        Raises:
            AmountAlreadyExistsError: Если счёт с таким именем уже существует
            InvalidAmountDataError: Если данные некорректны (отрицательный баланс)
        """
        logger.info(f"Creating amount: name={name}, count={count}")
        
        # Проверяем, не существует ли уже счёт с таким именем
        existing_amount = await self.amount_repo.get_amount_by_name(name)
        if existing_amount:
            logger.warning(f"Amount creation failed: Account already exists - name={name}")
            raise AmountAlreadyExistsError(f"Amount with name={name} already exists")
        
        # Валидация суммы (не может быть отрицательной)
        if count < 0:
            logger.warning(f"Amount creation failed: Negative count - name={name}, count={count}")
            raise InvalidAmountDataError("Amount count cannot be negative")
        
        try:
            amount = await self.amount_repo.create_amount(name, count)
            logger.info(f"Amount created successfully: name={amount.name}, count={amount.count}")
            return amount
        except Exception as e:
            logger.error(f"Amount creation failed: Unexpected error - name={name}, error={e}", exc_info=True)
            raise InvalidAmountDataError(f"Failed to create amount: {str(e)}")

    # ---------- Работа с транзакциями ----------

    async def get_latest_transaction(self, account_name: str) -> Optional[Dict[str, Any]]:
        """
        Получить последнюю транзакцию по счёту.
        
        Args:
            account_name: Имя счёта
            
        Returns:
            Словарь с данными транзакции или None, если транзакций нет
            
        Raises:
            AmountNotFoundError: Если счёт не найден
        """
        logger.debug(f"Getting latest transaction for account: {account_name}")
        amount = await self.get_amount_by_name(account_name)
        
        transaction = await self.amount_repo.get_latest_transaction(amount.id)
        
        if not transaction:
            logger.debug(f"No transactions found for account: {account_name}")
            return None
        
        return {
            "type": transaction.type,
            "category": transaction.category,
            "count": transaction.count,
        }

    async def get_transaction_history(
        self,
        account_name: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        transaction_type: Optional[str] = None,
    ) -> HistoryResponse:
        """
        Получить историю транзакций по счёту.
        
        Args:
            account_name: Имя счёта
            from_date: Начало периода (YYYY-MM-DD)
            to_date: Конец периода (YYYY-MM-DD)
            transaction_type: Тип транзакции (input/output/income/outcome)
            
        Returns:
            История транзакций
            
        Raises:
            AmountNotFoundError: Если счёт не найден
            InvalidTransactionDataError: Если данные некорректны (неверный тип или формат даты)
        """
        logger.info(
            f"Getting transaction history: account={account_name}, "
            f"from={from_date}, to={to_date}, type={transaction_type}"
        )
        
        # Проверка типа транзакции
        if transaction_type and transaction_type not in ['input', 'output', 'income', 'outcome']:
            logger.warning(f"Invalid transaction type: {transaction_type}")
            raise InvalidTransactionDataError("Incorrect type of request")
        
        # Преобразуем input/output в income/outcome для внутреннего использования
        internal_type = None
        if transaction_type == 'input':
            internal_type = 'income'
        elif transaction_type == 'output':
            internal_type = 'outcome'
        elif transaction_type in ['income', 'outcome']:
            internal_type = transaction_type
        
        # Получаем счёт
        amount = await self.get_amount_by_name(account_name)
        
        # Парсим даты
        from_dt = None
        to_dt = None
        if from_date:
            try:
                from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            except ValueError as e:
                logger.warning(f"Invalid from_date format: {from_date}")
                raise InvalidTransactionDataError("Incorrect type of request") from e
        if to_date:
            try:
                to_dt = datetime.strptime(to_date, "%Y-%m-%d")
                # Добавляем время конца дня
                to_dt = to_dt.replace(hour=23, minute=59, second=59)
            except ValueError as e:
                logger.warning(f"Invalid to_date format: {to_date}")
                raise InvalidTransactionDataError("Incorrect type of request") from e
        
        # Получаем транзакции
        transactions = await self.amount_repo.get_transactions(
            amount.id,
            from_date=from_dt,
            to_date=to_dt,
            transaction_type=internal_type
        )
        
        transaction_items = [
            TransactionItem(
                type=trans.type,
                category=trans.category,
                count=trans.count
            )
            for trans in transactions
        ]
        
        logger.debug(f"Retrieved {len(transaction_items)} transactions for account: {account_name}")
        
        return HistoryResponse(
            name=amount.name,
            transaction=transaction_items,
            limit_data=len(transaction_items)
        )

    async def create_transaction(
        self,
        account_name: str,
        transaction_type: str,
        category: str,
        count: float,
    ) -> TransactionORM:
        """
        Создать новую транзакцию.
        
        Args:
            account_name: Имя счёта
            transaction_type: Тип транзакции (income/outcome)
            category: Категория транзакции
            count: Сумма транзакции
            
        Returns:
            Созданная транзакция
            
        Raises:
            AmountNotFoundError: Если счёт не найден
            InvalidTransactionDataError: Если данные некорректны
        """
        logger.info(
            f"Creating transaction: account={account_name}, type={transaction_type}, "
            f"category={category}, count={count}"
        )
        
        # Валидация типа транзакции
        if transaction_type not in ['income', 'outcome']:
            logger.warning(f"Transaction creation failed: Invalid type - type={transaction_type}")
            raise InvalidTransactionDataError("Transaction type must be 'income' or 'outcome'")
        
        # Валидация суммы
        if count <= 0:
            logger.warning(f"Transaction creation failed: Invalid count - count={count}")
            raise InvalidTransactionDataError("Transaction count must be greater than 0")
        
        # Получаем счёт
        amount = await self.get_amount_by_name(account_name)
        
        try:
            transaction = await self.amount_repo.create_transaction(
                amount.id,
                transaction_type,
                category,
                count
            )
            # Получаем обновлённый amount после транзакции
            updated_amount = await self.amount_repo.get_amount_by_name(account_name)
            logger.info(
                f"Transaction created successfully: account_id={updated_amount.id}, "
                f"type={transaction_type}, count={count}, new_balance={updated_amount.count}"
            )
            return transaction
        except Exception as e:
            logger.error(
                f"Transaction creation failed: Unexpected error - account={account_name}, error={e}",
                exc_info=True
            )
            raise InvalidTransactionDataError(f"Failed to create transaction: {str(e)}") from e

