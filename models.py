from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    is_admin: bool = False
    orders: List["Order"] = Relationship(back_populates="user")


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    products: List["Product"] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    price: float
    stock: int
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    category: Optional["Category"] = Relationship(back_populates="products")
    order_items: List["OrderItem"] = Relationship(back_populates="product")


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="orders")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str
    total_amount: float
    items: List["OrderItem"] = Relationship(back_populates="order")
    payment_intent_id: str
    payment_intent_status: str


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    order: Optional["Order"] = Relationship(back_populates="items")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    product: Optional["Product"] = Relationship(back_populates="order_items")
    quantity: int
    price: float


class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    items: List["CartItem"] = Relationship(back_populates="cart")


class CartItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: Optional[int] = Field(default=None, foreign_key="cart.id")
    cart: Optional["Cart"] = Relationship(back_populates="items")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    product: Optional["Product"] = Relationship()
    quantity: int
