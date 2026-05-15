from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.database import get_db
from app.modules.sales.models import Sale, SaleDetail, SaleStatus
from app.modules.sales.schemas import SaleCreateInput, SaleResponse, SaleUpdate
from app.modules.customers.router import get_or_create_customer
from app.modules.inventory.models import Product

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("", response_model=List[SaleResponse])
def list_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    from app.modules.customers.models import Customer
    sales = db.query(Sale).offset(skip).limit(limit).all()
    result = []
    for sale in sales:
        customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
        result.append(SaleResponse(
            id=sale.id,
            customer_id=sale.customer_id,
            customer_name=customer.name if customer else "Unknown",
            date=sale.date,
            total=sale.total,
            status=sale.status,
            created_at=sale.created_at,
            details=sale.details
        ))
    return result


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    from app.modules.customers.models import Customer
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
    return SaleResponse(
        id=sale.id,
        customer_id=sale.customer_id,
        customer_name=customer.name if customer else "Unknown",
        date=sale.date,
        total=sale.total,
        status=sale.status,
        created_at=sale.created_at,
        details=sale.details
    )


@router.post("", response_model=SaleResponse, status_code=201)
def create_sale(sale_input: SaleCreateInput, db: Session = Depends(get_db)):
    from app.modules.customers.models import Customer
    try:
        with db.begin():
            customer = get_or_create_customer(db, sale_input.customer_name)

            total = 0.0
            details_data = []

            for prod_input in sale_input.products:
                product = db.query(Product).filter(
                    Product.name == prod_input.product_name
                ).first()

                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Product '{prod_input.product_name}' not found"
                    )

                if product.quantity < prod_input.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for product '{product.name}'. Current stock: {product.quantity}, requested: {prod_input.quantity}"
                    )

                subtotal = prod_input.quantity * product.sale_price
                total += subtotal

                product.quantity -= prod_input.quantity

                details_data.append({
                    "product_id": product.id,
                    "quantity": prod_input.quantity,
                    "unit_price": product.sale_price,
                    "subtotal": subtotal
                })

            db_sale = Sale(
                customer_id=customer.id,
                total=total,
                status=SaleStatus.pending
            )
            db.add(db_sale)
            db.flush()

            for detalle in details_data:
                db_detalle = SaleDetail(
                    sale_id=db_sale.id,
                    **detalle
                )
                db.add(db_detalle)

        db.refresh(db_sale)

        return SaleResponse(
            id=db_sale.id,
            customer_id=db_sale.customer_id,
            customer_name=customer.name,
            date=db_sale.date,
            total=db_sale.total,
            status=db_sale.status,
            created_at=db_sale.created_at,
            details=db_sale.details
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction error: {str(e)}")


@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(sale_id: int, sale_update: SaleUpdate, db: Session = Depends(get_db)):
    from app.modules.customers.models import Customer
    db_sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    if sale_update.status:
        db_sale.status = sale_update.status

    db.commit()
    db.refresh(db_sale)

    customer = db.query(Customer).filter(Customer.id == db_sale.customer_id).first()
    return SaleResponse(
        id=db_sale.id,
        customer_id=db_sale.customer_id,
        customer_name=customer.name if customer else "Unknown",
        date=db_sale.date,
        total=db_sale.total,
        status=db_sale.status,
        created_at=db_sale.created_at,
        details=db_sale.details
    )


@router.delete("/{sale_id}", status_code=204)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    db.query(SaleDetail).filter(SaleDetail.sale_id == sale_id).delete()
    db.delete(db_sale)
    db.commit()
    return None
