from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.modules.purchase.models import PurchaseStatus


class PurchaseProductInput(BaseModel):
    product_name: str
    quantity: int
    unit_price: float


class PurchaseCreateInput(BaseModel):
    products: List[PurchaseProductInput]


class PurchaseDetailResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class PurchaseResponse(BaseModel):
    id: int
    supplier: str
    date: datetime
    total: float
    status: PurchaseStatus
    created_at: Optional[datetime] = None
    details: List[PurchaseDetailResponse] = []

    class Config:
        from_attributes = True


class PurchaseUpdate(BaseModel):
    status: Optional[PurchaseStatus] = None
