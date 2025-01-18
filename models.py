from dataclasses import field
from datetime import datetime
from typing import List, Optional

from fquery.sqlmodel import SQL_PK, foreign_key, many_to_one, one_to_many, sqlmodel


@sqlmodel
class User:
    id: Optional[int] = field(default=None, **SQL_PK)
    email: str
    hashed_password: str
    is_admin: bool = False
    orders: List["Order"] = one_to_many()


@sqlmodel
class Category:
    id: Optional[int] = field(default=None, **SQL_PK)
    name: str
    description: str
    products: List["Product"] = one_to_many()


@sqlmodel
class Product:
    id: Optional[int] = field(default=None, **SQL_PK)
    name: str
    description: str
    price: float
    stock: int
    category: Optional[Category] = many_to_one("category.id")
    order_items: List["OrderItem"] = one_to_many()


@sqlmodel
class Order:
    id: Optional[int] = field(default=None, **SQL_PK)
    status: str
    total_amount: float
    payment_intent_id: str
    payment_intent_status: str
    items: List["OrderItem"] = one_to_many()
    user: Optional[User] = many_to_one("user.id")
    created_at: datetime = field(default_factory=datetime.utcnow)


@sqlmodel
class OrderItem:
    id: Optional[int] = field(default=None, **SQL_PK)
    quantity: int
    price: float
    order: Optional[Order] = many_to_one("order.id", back_populates="items")
    product: Optional[Product] = many_to_one("product.id", back_populates="order_items")


@sqlmodel
class Cart:
    id: Optional[int] = field(default=None, **SQL_PK)
    user: Optional[User] = foreign_key("users.id")
    created_at: datetime = field(default_factory=datetime.utcnow)
    items: List["CartItem"] = one_to_many()


@sqlmodel
class CartItem:
    id: Optional[int] = field(default=None, **SQL_PK)
    quantity: int
    cart_id: Optional[int] = field(default=None, metadata={"foreign_key": "cart.id"})
    cart: Optional[Cart] = many_to_one("cart.id", back_populates="items")
    product: Optional[Product] = foreign_key("products.id")
