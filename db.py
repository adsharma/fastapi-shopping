from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./shopify_clone.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
