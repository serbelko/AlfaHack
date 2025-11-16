from pydantic import BaseModel
from typing import List
from datetime import datetime

class AmountResponse(BaseModel):
    count: float
    name: str

class AmountListResponse(BaseModel):
    amounts: List[AmountResponse]
    limit_data: int

class TransactionItem(BaseModel):
    type: str
    category: str
    count: float
    created_at: datetime

class HistoryResponse(BaseModel):
    name: str
    transaction: List[TransactionItem]
    limit_data: int

class AmountCreateRequest(BaseModel):
    name: str
    count: float = 0.0

class TransactionCreateRequest(BaseModel):
    name: str
    type: str  # 'income' or 'outcome'
    category: str
    count: float

