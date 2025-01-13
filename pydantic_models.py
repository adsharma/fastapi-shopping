import datetime
from typing import List, Optional

from pydantic import BaseModel


# Pydantic Models
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemBase]


class OrderOut(BaseModel):
    id: int
    status: str
    total_amount: float
    created_at: datetime.datetime
    items: List[OrderItemBase]

    class Config:
        orm_mode = True


# payments related
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int


class CartItemOut(BaseModel):
    product_id: int
    quantity: int
    product: ProductOut

    class Config:
        orm_mode = True


class CartOut(BaseModel):
    id: int
    items: List[CartItemOut]
    total: float

    class Config:
        orm_mode = True
