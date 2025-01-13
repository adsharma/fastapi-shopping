import random
from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from db import get_db
from main import app
from models import Category, Product

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# Test data generation
def generate_test_products(db: Session) -> list:
    """Generate 30 dummy products across different categories"""
    categories = [
        {"name": "Electronics", "description": "Electronic gadgets"},
        {"name": "Clothing", "description": "Fashion items"},
        {"name": "Books", "description": "Reading materials"},
    ]

    products = []
    product_names = [
        "Smartphone",
        "Laptop",
        "Tablet",
        "T-Shirt",
        "Jeans",
        "Dress",
        "Novel",
        "Textbook",
        "Magazine",
        "Headphones",
        "Speaker",
        "Camera",
        "Sweater",
        "Jacket",
        "Shorts",
        "Biography",
        "Cookbook",
        "Comic",
        "Monitor",
        "Keyboard",
        "Mouse",
        "Hoodie",
        "Skirt",
        "Pants",
        "Dictionary",
        "Atlas",
        "Journal",
        "Charger",
        "Watch",
        "Earbuds",
    ]

    # Create categories
    db_categories = []
    for cat in categories:
        db_category = Category(**cat)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        db_categories.append(db_category)

    # Create products
    for i, name in enumerate(product_names):
        category = db_categories[i % len(db_categories)]
        product = Product(
            name=name,
            description=f"This is a test {name.lower()}",
            price=random.uniform(9.99, 999.99),
            stock=random.randint(0, 100),
            category_id=category.id,
        )
        db.add(product)
        products.append(product)

    db.commit()
    return products


# Fixtures
@pytest.fixture(scope="session")
def db() -> Generator:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def client(db: Session) -> Generator:
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def auth_headers(client: TestClient) -> Dict[str, str]:
    # Create test user
    user_data = {"email": "test@example.com", "password": "testpassword123"}
    client.post("/user/users/", json=user_data)

    # Get auth token
    response = client.post(
        "/user/token",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Tests
def test_create_user(client: TestClient):
    response = client.post(
        "/user/users/", json={"email": "newuser@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "email" in response.json()
    assert response.json()["email"] == "newuser@example.com"


def test_create_categories(client: TestClient, auth_headers: Dict[str, str]):
    response = client.post(
        "/catalog/categories/",
        json={"name": "Test Category", "description": "Test Description"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Category"


def test_get_categories(client: TestClient, auth_headers: Dict[str, str]):
    response = client.get("/catalog/categories/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_and_get_products(
    client: TestClient, db: Session, auth_headers: Dict[str, str]
):
    # Generate test products
    _ = generate_test_products(db)

    # Test getting all products
    response = client.get("/catalog/products/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 30

    # Test getting single product
    product_id = response.json()[0]["id"]
    response = client.get(f"/catalog/products/{product_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "name" in response.json()


def test_cart_operations(client: TestClient, auth_headers: Dict[str, str]):
    # Add item to cart
    response = client.post(
        "/cart/cart/items/", json={"product_id": 1, "quantity": 2}, headers=auth_headers
    )
    assert response.status_code == 200
    assert "items" in response.json()

    # Get cart
    response = client.get("/cart/cart/", headers=auth_headers)
    assert response.status_code == 200
    assert "total" in response.json()
    assert len(response.json()["items"]) > 0


def test_checkout_process(client: TestClient, auth_headers: Dict[str, str]):
    # First add item to cart
    client.post(
        "/cart/cart/items/", json={"product_id": 1, "quantity": 1}, headers=auth_headers
    )

    # Attempt checkout
    response = client.post("/cart/cart/checkout/", headers=auth_headers)
    assert response.status_code == 200
    assert "client_secret" in response.json()
    assert "order_id" in response.json()


def test_get_order(client: TestClient, auth_headers: Dict[str, str]):
    # Create an order first through checkout
    checkout_response = client.post("/cart/cart/checkout/", headers=auth_headers)
    order_id = checkout_response.json()["order_id"]

    # Get the order
    response = client.get(f"/catalog/orders/{order_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "status" in response.json()
    assert "total_amount" in response.json()


if __name__ == "__main__":
    pytest.main(["-v"])
