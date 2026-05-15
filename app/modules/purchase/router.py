from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.modules.purchase.models import Purchase, PurchaseDetail, PurchaseStatus
from app.modules.purchase.schemas import PurchaseCreateInput, PurchaseResponse, PurchaseUpdate
from app.modules.inventory.router import get_or_create_product
from app.modules.inventory.models import Product

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.get("", response_model=List[PurchaseResponse])
def list_purchases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    purchases = db.query(Purchase).offset(skip).limit(limit).all()
    result = []
    for purchase in purchases:
        result.append(PurchaseResponse(
            id=purchase.id,
            supplier=purchase.supplier,
            date=purchase.date,
            total=purchase.total,
            status=purchase.status,
            created_at=purchase.created_at,
            details=purchase.details
        ))
    return result


@router.get("/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return PurchaseResponse(
        id=purchase.id,
        supplier=purchase.supplier,
        date=purchase.date,
        total=purchase.total,
        status=purchase.status,
        created_at=purchase.created_at,
        details=purchase.details
    )


@router.post("", response_model=PurchaseResponse, status_code=201)
def create_purchase(purchase_input: PurchaseCreateInput, db: Session = Depends(get_db)):
    try:
        with db.begin():
            total = 0.0
            details_data = []

            for prod_input in purchase_input.products:
                product = get_or_create_product(
                    db,
                    name=prod_input.product_name,
                    sale_price=prod_input.unit_price,
                    purchase_price=prod_input.unit_price
                )

                subtotal = prod_input.quantity * prod_input.unit_price
                total += subtotal

                product.quantity += prod_input.quantity

                details_data.append({
                    "product_id": product.id,
                    "quantity": prod_input.quantity,
                    "unit_price": prod_input.unit_price,
                    "subtotal": subtotal
                })

            db_purchase = Purchase(
                supplier="General Supplier",
                total=total,
                status=PurchaseStatus.pending
            )
            db.add(db_purchase)
            db.flush()

            for detalle in details_data:
                db_detalle = PurchaseDetail(
                    purchase_id=db_purchase.id,
                    **detalle
                )
                db.add(db_detalle)

        db.refresh(db_purchase)

        return PurchaseResponse(
            id=db_purchase.id,
            supplier=db_purchase.supplier,
            date=db_purchase.date,
            total=db_purchase.total,
            status=db_purchase.status,
            created_at=db_purchase.created_at,
            details=db_purchase.details
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction error: {str(e)}")


@router.put("/{purchase_id}", response_model=PurchaseResponse)
def update_purchase(purchase_id: int, purchase_update: PurchaseUpdate, db: Session = Depends(get_db)):
    db_purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not db_purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    if purchase_update.status:
        db_purchase.status = purchase_update.status

    db.commit()
    db.refresh(db_purchase)

    return PurchaseResponse(
        id=db_purchase.id,
        supplier=db_purchase.supplier,
        date=db_purchase.date,
        total=db_purchase.total,
        status=db_purchase.status,
        created_at=db_purchase.created_at,
        details=db_purchase.details
    )


@router.delete("/{purchase_id}", status_code=204)
def delete_purchase(purchase_id: int, db: Session = Depends(get_db)):
    db_purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not db_purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    db.query(PurchaseDetail).filter(PurchaseDetail.purchase_id == purchase_id).delete()
    db.delete(db_purchase)
    db.commit()
    return None
