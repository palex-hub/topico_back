from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.modules.sales.models import SaleStatus


class SaleProductInput(BaseModel):
    product_name: str
    quantity: int


class SaleCreateInput(BaseModel):
    customer_name: str
    products: List[SaleProductInput]


class SaleDetailResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    customer_id: int
    customer_name: str
    date: datetime
    total: float
    status: SaleStatus
    created_at: Optional[datetime] = None
    details: List[SaleDetailResponse] = []

    class Config:
        from_attributes = True


class SaleUpdate(BaseModel):
    status: Optional[SaleStatus] = None
