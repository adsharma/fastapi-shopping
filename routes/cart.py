import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from db import get_db
from models import Cart, CartItem, Order, OrderItem, Product, User
from pydantic_models import CartItemCreate, CartItemOut, CartOut, ProductOut

router = APIRouter(prefix="/cart")


# Add these new endpoints
@router.post("/cart/items/", response_model=CartOut)
async def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get or create cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()

    # Check if product exists and has enough stock
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    # Add or update cart item
    cart_item = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id, CartItem.product_id == item.product_id)
        .first()
    )

    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id, product_id=item.product_id, quantity=item.quantity
        )
        db.add(cart_item)

    db.commit()
    return await get_cart(db, current_user)


@router.get("/cart/", response_model=CartOut)
async def get_cart(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Calculate total
    total = 0
    for item in cart.items:
        total += item.product.price * item.quantity

    return CartOut(
        id=cart.id,
        items=[
            CartItemOut(
                product_id=item.product_id,
                quantity=item.quantity,
                product=ProductOut.from_orm(item.product),
            )
            for item in cart.items
        ],
        total=total,
    )


@router.post("/cart/checkout/")
async def checkout(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    CartQ = Cart.__sqlmodel__
    cart = db.query(CartQ).filter(CartQ.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=404, detail="Cart is empty")

    # Calculate total
    total = 0
    order_items = []
    for cart_item in cart.items:
        product = cart_item.product
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400, detail=f"Insufficient stock for product {product.id}"
            )
        total += product.price * cart_item.quantity
        order_items.append(
            OrderItem(
                product_id=product.id, quantity=cart_item.quantity, price=product.price
            )
        )

    # Create Stripe payment intent
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),  # Convert to cents
            currency="usd",
            metadata={"user_id": current_user.id},
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create order
    order_items = [o.__sqlmodel__ for o in order_items]
    order = Order(
        user_id=current_user.id,
        status="pending",
        total_amount=total,
        items=order_items,
        payment_intent_id=intent.id,
        payment_intent_status="pending",
    )

    db.add(order.sqlmodel())

    # Clear cart
    for item in cart.items:
        db.delete(item)
    db.delete(cart)

    db.commit()

    return {"client_secret": intent.client_secret, "order_id": order.id}
