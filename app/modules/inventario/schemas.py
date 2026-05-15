from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        from_attributes = True


class ProductoBase(BaseModel):
    nombre: str
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad: int = 0
    precio_compra: float = 0.0
    precio_venta: float = 0.0
    categoria_id: Optional[int] = None
    activo: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad: Optional[int] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    categoria_id: Optional[int] = None
    activo: Optional[bool] = None


class ProductoResponse(ProductoBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True