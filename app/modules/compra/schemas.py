from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.modules.compra.models import EstadoCompra


class CompraProductoInput(BaseModel):
    nombre_producto: str
    cantidad: int
    precio_unitario: float


class CompraCreateInput(BaseModel):
    productos: List[CompraProductoInput]


class DetalleCompraResponse(BaseModel):
    id: int
    producto_id: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float

    class Config:
        from_attributes = True


class CompraResponse(BaseModel):
    id: int
    proveedor: str
    fecha: datetime
    total: float
    estado: EstadoCompra
    created_at: Optional[datetime] = None
    detalles: List[DetalleCompraResponse] = []

    class Config:
        from_attributes = True


class CompraUpdate(BaseModel):
    estado: Optional[EstadoCompra] = None