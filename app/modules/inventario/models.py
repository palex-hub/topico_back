from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)

    productos = relationship("Producto", back_populates="categoria")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False, unique=True, index=True)
    codigo = Column(String(100), nullable=True)
    descripcion = Column(String(500), nullable=True)
    cantidad = Column(Integer, default=0)
    precio_compra = Column(Float, default=0.0)
    precio_venta = Column(Float, default=0.0)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    categoria = relationship("Categoria", back_populates="productos")