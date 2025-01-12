from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models import Order, OrderItem, Product
from pydantic_models import OrderCreate, OrderOut

router = APIRouter(prefix="/catalog")


# Order endpoints
@router.post("/orders/", response_model=OrderOut)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Calculate total amount and create order
    total_amount = 0
    order_items = []

    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product {item.product_id} not found"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {item.product_id}",
            )

        total_amount += product.price * item.quantity
        order_items.append(
            OrderItem(
                product_id=item.product_id, quantity=item.quantity, price=product.price
            )
        )

        # Update stock
        product.stock -= item.quantity

    db_order = Order(status="pending", total_amount=total_amount, items=order_items)

    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
