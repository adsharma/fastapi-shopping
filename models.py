from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from fquery.sqlmodel import (
    SQL_PK,
    foreignkey,
    many_to_one,
    one_to_many,
    sqlmodel,
    unique,
)
from sqlmodel import Field, Relationship, SQLModel


@sqlmodel
class User:
    email: str
    hashed_password: str
    is_admin: bool = False
    orders: List["Order"] = (
        field(default_factory=[], metadata={"relationship": True}),
    )
    id: Optional[int] = field(default=None, **SQL_PK)


@sqlmodel
class Category:
    name: str
    description: str
    products: List["Product"] = (
        field(default_factory=[], metadata={"relationship": True}),
    )
    id: Optional[int] = field(default=None, **SQL_PK)


@sqlmodel
class Product:
    name: str
    description: str
    price: float
    stock: int
    category_id: Optional[int] = field(
        default=None, metadata={"foreign_key": "category.id"}
    )
    category: Optional["Category"] = (
        field(default=None, metadata={"relationship": True, "many_to_one": True}),
    )
    order_items: List["OrderItem"] = (
        field(default_factory=[], metadata={"relationship": True}),
    )
    id: Optional[int] = field(default=None, **SQL_PK)


@sqlmodel
class Order:
    status: str
    total_amount: float
    payment_intent_id: str
    payment_intent_status: str
    items: List["OrderItem"] = (
        field(default_factory=[], metadata={"relationship": True}),
    )
    user_id: Optional[int] = field(default=None, metadata={"foreign_key": "user.id"})
    user: Optional["User"] = (
        field(default=None, metadata={"relationship": True, "many_to_one": True}),
    )
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = field(default=None, **SQL_PK)


@sqlmodel
class OrderItem:
    quantity: int
    price: float
    order_id: Optional[int] = field(default=None, metadata={"foreign_key": "order.id"})
    order: Optional["Order"] = (
        field(
            default_factory=[],
            metadata={
                "relationship": True,
                "many_to_one": True,
                "back_populates": "items",
            },
        ),
    )
    product_id: Optional[int] = field(
        default=None, metadata={"foreign_key": "product.id"}
    )
    product: Optional["Product"] = (
        field(
            default=None,
            metadata={
                "relationship": True,
                "many_to_one": True,
                "back_populates": "order_items",
            },
        ),
    )
    id: Optional[int] = field(default=None, **SQL_PK)


@sqlmodel
class Cart:
    user_id: Optional[int] = field(default=None, metadata={"foreign_key": "user.id"})
    created_at: datetime = field(default_factory=datetime.utcnow)
    items: List["CartItem"] = (
        field(default_factory=[], metadata={"relationship": True}),
    )
    id: Optional[int] = field(default=None, **SQL_PK)


@sqlmodel
class CartItem:
    quantity: int
    cart_id: Optional[int] = field(default=None, metadata={"foreign_key": "cart.id"})
    cart: Optional["Cart"] = (
        field(
            default=None,
            metadata={
                "relationship": True,
                "many_to_one": True,
                "back_populates": "items",
            },
        ),
    )
    product_id: Optional[int] = field(
        default=None, metadata={"foreign_key": "product.id"}
    )
    product: Optional["Product"] = (
        field(default=None, metadata={"relationship": True}),
    )
    id: Optional[int] = field(default=None, **SQL_PK)
