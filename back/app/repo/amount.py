from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import AmountORM, TransactionORM
from typing import List, Optional
from datetime import datetime

class AmountRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_amount_by_name(self, name: str) -> Optional[AmountORM]:
        result = await self.session.execute(
            select(AmountORM).where(AmountORM.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all_amounts(self) -> List[AmountORM]:
        result = await self.session.execute(select(AmountORM))
        return list(result.scalars().all())

    async def create_amount(self, name: str, count: float = 0.0) -> AmountORM:
        amount = AmountORM(name=name, count=count)
        self.session.add(amount)
        await self.session.commit()
        await self.session.refresh(amount)
        return amount

    async def get_transactions(
        self,
        amount_id: int,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        transaction_type: Optional[str] = None
    ) -> List[TransactionORM]:
        query = select(TransactionORM).where(TransactionORM.amount_id == amount_id)
        
        if from_date:
            query = query.where(TransactionORM.created_at >= from_date)
        if to_date:
            query = query.where(TransactionORM.created_at <= to_date)
        if transaction_type:
            query = query.where(TransactionORM.type == transaction_type)
        
        query = query.order_by(TransactionORM.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_latest_transaction(self, amount_id: int) -> Optional[TransactionORM]:
        result = await self.session.execute(
            select(TransactionORM)
            .where(TransactionORM.amount_id == amount_id)
            .order_by(TransactionORM.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_transaction(
        self,
        amount_id: int,
        transaction_type: str,
        category: str,
        count: float
    ) -> TransactionORM:
        transaction = TransactionORM(
            amount_id=amount_id,
            type=transaction_type,
            category=category,
            count=count
        )
        self.session.add(transaction)
        
        # Обновляем баланс счёта
        amount = await self.session.get(AmountORM, amount_id)
        if amount:
            if transaction_type == 'income':
                amount.count += count
            elif transaction_type == 'outcome':
                amount.count -= count
        
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

