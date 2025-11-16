# app/scripts/seed_amounts_admin_test.py

import asyncio
from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.session import engine, mock_engine
from app.core.db import Base, UsersORM, AmountORM, TransactionORM


TARGET_LOGINS: tuple[str, ...] = ("admin", "test")

# Чтобы обойти UNIQUE(name) и не править модели:
# admin -> "test"
# test  -> "test\u200B"  (Zero Width Space). В БД это разные значения, визуально оба "test".
VISIBLE_NAME = "test"
HIDDEN_SUFFIX = "\u200B"   # Zero-Width Space


async def init_mock_db() -> None:
    """Создаёт таблицы в mock БД (идемпотентно)."""
    async with mock_engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all,
            tables=[AmountORM.__table__, TransactionORM.__table__],
        )


async def fetch_users_by_login(logins: Iterable[str]) -> list[UsersORM]:
    """Читаем пользователей из ОСНОВНОЙ БД по логинам."""
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as session:
        res = await session.execute(select(UsersORM).where(UsersORM.login.in_(list(logins))))
        return list(res.scalars().all())


def amount_name_for(owner_login: str) -> str:
    """Возвращает имя счёта для каждого владельца без изменения core-моделей."""
    if owner_login == "admin":
        return VISIBLE_NAME
    if owner_login == "test":
        return VISIBLE_NAME + HIDDEN_SUFFIX
    # на всякий случай для прочих логинов
    return f"{VISIBLE_NAME}{HIDDEN_SUFFIX}"


def build_transactions_for(owner_login: str) -> list[dict]:
    """Разные наборы транзакций для admin и test."""
    now = datetime.utcnow()
    if owner_login == "admin":
        return [
            {"type": "income",  "category": "зарплата",      "count": 120_000.0, "created_at": now - timedelta(days=28)},
            {"type": "outcome", "category": "аренда",        "count": 35_000.0,  "created_at": now - timedelta(days=25)},
            {"type": "outcome", "category": "еда",           "count": 12_500.0,  "created_at": now - timedelta(days=22)},
            {"type": "income",  "category": "бонус",         "count": 20_000.0,  "created_at": now - timedelta(days=18)},
            {"type": "outcome", "category": "транспорт",     "count": 4_200.0,   "created_at": now - timedelta(days=14)},
            {"type": "outcome", "category": "коммунальные",  "count": 7_800.0,   "created_at": now - timedelta(days=10)},
            {"type": "outcome", "category": "подписки",      "count": 1_200.0,   "created_at": now - timedelta(days=7)},
        ]
    # для "test"
    return [
        {"type": "income",  "category": "подработка",     "count": 25_000.0, "created_at": now - timedelta(days=27)},
        {"type": "outcome", "category": "еда",            "count": 6_100.0,  "created_at": now - timedelta(days=24)},
        {"type": "outcome", "category": "развлечения",    "count": 3_900.0,  "created_at": now - timedelta(days=21)},
        {"type": "income",  "category": "фриланс",        "count": 18_000.0, "created_at": now - timedelta(days=16)},
        {"type": "outcome", "category": "спорт",          "count": 2_400.0,  "created_at": now - timedelta(days=12)},
        {"type": "outcome", "category": "покупки",        "count": 9_300.0,  "created_at": now - timedelta(days=9)},
        {"type": "outcome", "category": "подписки",       "count": 990.0,    "created_at": now - timedelta(days=6)},
    ]


async def ensure_amount(mock_session, owner_login: str) -> AmountORM:
    """Создаёт/возвращает счёт для владельца. Имя визуально 'test' для обоих, но в БД разные."""
    name = amount_name_for(owner_login)
    res = await mock_session.execute(select(AmountORM).where(AmountORM.name == name))
    amount = res.scalar_one_or_none()
    if amount is None:
        amount = AmountORM(name=name, count=0.0)
        mock_session.add(amount)
        await mock_session.flush()
        shown = VISIBLE_NAME
        suffix_info = " (zero-width suffix)" if name != VISIBLE_NAME else ""
        print(f"✅ Created amount '{shown}'{suffix_info} for '{owner_login}' (id={amount.id})")
    else:
        print(f"ℹ Amount for '{owner_login}' already exists (id={amount.id}, name stored='{amount.name}')")
    return amount


async def seed_amounts_and_transactions() -> None:
    """Создаёт у admin и test по отдельному счёту 'test' (визуально) и транзакции к ним."""
    # Проверяем наличие пользователей в основной БД
    users = await fetch_users_by_login(TARGET_LOGINS)
    existing = {u.login for u in users}
    missing = [l for l in TARGET_LOGINS if l not in existing]
    if missing:
        print(f"⚠ Users not found in main DB: {missing}. Сначала запустите seed_users.py")
        # продолжаем для тех, кто есть
    if not users:
        print("⚠ No target users found. Exit.")
        return

    mock_session_maker = async_sessionmaker(mock_engine, expire_on_commit=False)
    async with mock_session_maker() as mock_session:
        for owner_login in TARGET_LOGINS:
            if owner_login not in existing:
                continue

            amount = await ensure_amount(mock_session, owner_login)

            # Проверяем, есть ли уже транзакции
            res = await mock_session.execute(
                select(TransactionORM).where(TransactionORM.amount_id == amount.id)
            )
            existing_tx = list(res.scalars().all())
            if existing_tx:
                print(f"ℹ Amount for '{owner_login}' already has {len(existing_tx)} transactions. Skip.")
                continue

            tx_data = build_transactions_for(owner_login)
            for t in tx_data:
                tx = TransactionORM(
                    amount_id=amount.id,
                    type=t["type"],
                    category=t["category"],
                    count=t["count"],
                    created_at=t["created_at"],
                )
                mock_session.add(tx)
                if t["type"] == "income":
                    amount.count += t["count"]
                elif t["type"] == "outcome":
                    amount.count -= t["count"]

            await mock_session.commit()
            # Печатаем видимое имя (оба выглядят как 'test')
            print(f"✅ Created {len(tx_data)} transactions for '{owner_login}', amount '{VISIBLE_NAME}'. Final balance: {amount.count:.2f}")


async def main() -> None:
    await init_mock_db()
    await seed_amounts_and_transactions()


if __name__ == "__main__":
    asyncio.run(main())
