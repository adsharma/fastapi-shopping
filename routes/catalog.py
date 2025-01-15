from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models import Category, Product
from pydantic_models import CategoryCreate, CategoryOut, ProductCreate, ProductOut

router = APIRouter(prefix="/catalog")


# Category endpoints
@router.post("/categories/", response_model=CategoryOut)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(**category.dict()).sqlmodel()
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/categories/", response_model=List[CategoryOut])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    CategoryQ = Category.__sqlmodel__
    categories = db.query(CategoryQ).offset(skip).limit(limit).all()
    return categories


# Product endpoints
@router.post("/products/", response_model=ProductOut)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict()).sqlmodel()
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/products/", response_model=List[ProductOut])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ProductQ = Product.__sqlmodel__
    products = db.query(ProductQ).offset(skip).limit(limit).all()
    return products


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    ProductQ = Product.__sqlmodel__
    product = db.query(ProductQ).filter(ProductQ.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
