from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.modules.compra.models import Compra, DetalleCompra, EstadoCompra
from app.modules.compra.schemas import CompraCreateInput, CompraResponse, CompraUpdate
from app.modules.inventario.router import get_or_create_producto
from app.modules.inventario.models import Producto

router = APIRouter(prefix="/compras", tags=["Compras"])


@router.get("", response_model=List[CompraResponse])
def listar_compras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    compras = db.query(Compra).offset(skip).limit(limit).all()
    result = []
    for compra in compras:
        result.append(CompraResponse(
            id=compra.id,
            proveedor=compra.proveedor,
            fecha=compra.fecha,
            total=compra.total,
            estado=compra.estado,
            created_at=compra.created_at,
            detalles=compra.detalles
        ))
    return result


@router.get("/{compra_id}", response_model=CompraResponse)
def obtener_compra(compra_id: int, db: Session = Depends(get_db)):
    compra = db.query(Compra).filter(Compra.id == compra_id).first()
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return CompraResponse(
        id=compra.id,
        proveedor=compra.proveedor,
        fecha=compra.fecha,
        total=compra.total,
        estado=compra.estado,
        created_at=compra.created_at,
        detalles=compra.detalles
    )


@router.post("", response_model=CompraResponse, status_code=201)
def crear_compra(compra_input: CompraCreateInput, db: Session = Depends(get_db)):
    try:
        with db.begin():
            total = 0.0
            detalles_data = []
            
            for prod_input in compra_input.productos:
                producto = get_or_create_producto(
                    db,
                    nombre=prod_input.nombre_producto,
                    precio_venta=prod_input.precio_unitario,
                    precio_compra=prod_input.precio_unitario
                )
                
                subtotal = prod_input.cantidad * prod_input.precio_unitario
                total += subtotal
                
                producto.cantidad += prod_input.cantidad
                
                detalles_data.append({
                    "producto_id": producto.id,
                    "nombre_producto": producto.nombre,
                    "cantidad": prod_input.cantidad,
                    "precio_unitario": prod_input.precio_unitario,
                    "subtotal": subtotal
                })
            
            db_compra = Compra(
                proveedor="Proveedor General",
                total=total,
                estado=EstadoCompra.pendiente
            )
            db.add(db_compra)
            db.flush()
            
            for detalle in detalles_data:
                producto_id = detalle.pop("nombre_producto")
                db_detalle = DetalleCompra(
                    compra_id=db_compra.id,
                    **detalle
                )
                db.add(db_detalle)
        
        db.refresh(db_compra)
        
        return CompraResponse(
            id=db_compra.id,
            proveedor=db_compra.proveedor,
            fecha=db_compra.fecha,
            total=db_compra.total,
            estado=db_compra.estado,
            created_at=db_compra.created_at,
            detalles=db_compra.detalles
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en transacción: {str(e)}")


@router.put("/{compra_id}", response_model=CompraResponse)
def actualizar_compra(compra_id: int, compra_update: CompraUpdate, db: Session = Depends(get_db)):
    db_compra = db.query(Compra).filter(Compra.id == compra_id).first()
    if not db_compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    if compra_update.estado:
        db_compra.estado = compra_update.estado
    
    db.commit()
    db.refresh(db_compra)
    
    return CompraResponse(
        id=db_compra.id,
        proveedor=db_compra.proveedor,
        fecha=db_compra.fecha,
        total=db_compra.total,
        estado=db_compra.estado,
        created_at=db_compra.created_at,
        detalles=db_compra.detalles
    )


@router.delete("/{compra_id}", status_code=204)
def eliminar_compra(compra_id: int, db: Session = Depends(get_db)):
    db_compra = db.query(Compra).filter(Compra.id == compra_id).first()
    if not db_compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    db.query(DetalleCompra).filter(DetalleCompra.compra_id == compra_id).delete()
    db.delete(db_compra)
    db.commit()
    return None