from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

Base = declarative_base()

class UsersORM(Base, SerializerMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    login: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)

# Mock service models (используют отдельную БД mock_db)
class AmountORM(Base, SerializerMixin):
    __tablename__ = 'amounts'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    count: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

class TransactionORM(Base, SerializerMixin):
    __tablename__ = 'transactions'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount_id: Mapped[int] = mapped_column(ForeignKey('amounts.id'), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'income' or 'outcome'
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    count: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

