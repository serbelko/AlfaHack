from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, UUID, Float, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy_serializer import SerializerMixin

Base = declarative_base()

class UsersORM(Base, SerializerMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    login: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hash_password: Mapped[str] = mapped_column(String(255), nullable=False)

