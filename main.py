from fastapi import FastAPI
from sqlmodel import SQLModel

from db import engine
from routes.cart import router as cart_router
from routes.catalog import router as catalog_router
from routes.order import router as order_router
from routes.payments import router as payments_router
from routes.user import router as user_router

# FastAPI app
app = FastAPI(title="Shopify Clone API")
app.include_router(user_router)
app.include_router(catalog_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(payments_router)


# Create tables
SQLModel.metadata.create_all(bind=engine)
