from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.database import get_db
from app.modules.ventas.models import Venta, DetalleVenta, EstadoVenta
from app.modules.ventas.schemas import VentaCreateInput, VentaResponse, VentaUpdate
from app.modules.clientes.router import get_or_create_cliente
from app.modules.inventario.models import Producto

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.get("", response_model=List[VentaResponse])
def listar_ventas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ventas = db.query(Venta).offset(skip).limit(limit).all()
    result = []
    for venta in ventas:
        cliente = db.query(Cliente).filter(Cliente.id == venta.cliente_id).first()
        result.append(VentaResponse(
            id=venta.id,
            cliente_id=venta.cliente_id,
            nombre_cliente=cliente.nombre if cliente else "Desconocido",
            fecha=venta.fecha,
            total=venta.total,
            estado=venta.estado,
            created_at=venta.created_at,
            detalles=venta.detalles
        ))
    return result


@router.get("/{venta_id}", response_model=VentaResponse)
def obtener_venta(venta_id: int, db: Session = Depends(get_db)):
    from app.modules.clientes.models import Cliente
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    cliente = db.query(Cliente).filter(Cliente.id == venta.cliente_id).first()
    return VentaResponse(
        id=venta.id,
        cliente_id=venta.cliente_id,
        nombre_cliente=cliente.nombre if cliente else "Desconocido",
        fecha=venta.fecha,
        total=venta.total,
        estado=venta.estado,
        created_at=venta.created_at,
        detalles=venta.detalles
    )


@router.post("", response_model=VentaResponse, status_code=201)
def crear_venta(venta_input: VentaCreateInput, db: Session = Depends(get_db)):
    from app.modules.clientes.models import Cliente
    try:
        with db.begin():
            cliente = get_or_create_cliente(db, venta_input.nombre_cliente)
            
            total = 0.0
            detalles_data = []
            
            for prod_input in venta_input.productos:
                producto = db.query(Producto).filter(
                    Producto.nombre == prod_input.nombre_producto
                ).first()
                
                if not producto:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Producto '{prod_input.nombre_producto}' no encontrado"
                    )
                
                if producto.cantidad < prod_input.cantidad:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Stock insuficiente para el producto '{producto.nombre}'. Stock actual: {producto.cantidad}, solicitado: {prod_input.cantidad}"
                    )
                
                subtotal = prod_input.cantidad * producto.precio_venta
                total += subtotal
                
                producto.cantidad -= prod_input.cantidad
                
                detalles_data.append({
                    "producto_id": producto.id,
                    "cantidad": prod_input.cantidad,
                    "precio_unitario": producto.precio_venta,
                    "subtotal": subtotal
                })
            
            db_venta = Venta(
                cliente_id=cliente.id,
                total=total,
                estado=EstadoVenta.pendiente
            )
            db.add(db_venta)
            db.flush()
            
            for detalle in detalles_data:
                db_detalle = DetalleVenta(
                    venta_id=db_venta.id,
                    **detalle
                )
                db.add(db_detalle)
        
        db.refresh(db_venta)
        
        return VentaResponse(
            id=db_venta.id,
            cliente_id=db_venta.cliente_id,
            nombre_cliente=cliente.nombre,
            fecha=db_venta.fecha,
            total=db_venta.total,
            estado=db_venta.estado,
            created_at=db_venta.created_at,
            detalles=db_venta.detalles
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en transacción: {str(e)}")


@router.put("/{venta_id}", response_model=VentaResponse)
def actualizar_venta(venta_id: int, venta_update: VentaUpdate, db: Session = Depends(get_db)):
    from app.modules.clientes.models import Cliente
    db_venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not db_venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    if venta_update.estado:
        db_venta.estado = venta_update.estado
    
    db.commit()
    db.refresh(db_venta)
    
    cliente = db.query(Cliente).filter(Cliente.id == db_venta.cliente_id).first()
    return VentaResponse(
        id=db_venta.id,
        cliente_id=db_venta.cliente_id,
        nombre_cliente=cliente.nombre if cliente else "Desconocido",
        fecha=db_venta.fecha,
        total=db_venta.total,
        estado=db_venta.estado,
        created_at=db_venta.created_at,
        detalles=db_venta.detalles
    )


@router.delete("/{venta_id}", status_code=204)
def eliminar_venta(venta_id: int, db: Session = Depends(get_db)):
    db_venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not db_venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    db.query(DetalleVenta).filter(DetalleVenta.venta_id == venta_id).delete()
    db.delete(db_venta)
    db.commit()
    return None