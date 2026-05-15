from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.modules.ventas.models import EstadoVenta


class VentaProductoInput(BaseModel):
    nombre_producto: str
    cantidad: int


class VentaCreateInput(BaseModel):
    nombre_cliente: str
    productos: List[VentaProductoInput]


class DetalleVentaResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float

    class Config:
        from_attributes = True


class VentaResponse(BaseModel):
    id: int
    cliente_id: int
    nombre_cliente: str
    fecha: datetime
    total: float
    estado: EstadoVenta
    created_at: Optional[datetime] = None
    detalles: List[DetalleVentaResponse] = []

    class Config:
        from_attributes = True


class VentaUpdate(BaseModel):
    estado: Optional[EstadoVenta] = None