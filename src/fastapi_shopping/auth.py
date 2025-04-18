from app.config import app_config
from db import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models import User
from sqlalchemy.orm import Session

# These should be in your environment variables

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = app_config.SECRET_KEY
ALGORITHM = app_config.ALGORITHM


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    UserQ = User.__sqlmodel__
    user = db.query(UserQ).filter(UserQ.email == email).first()
    if user is None:
        raise credentials_exception

    return user


# Optional: Get current admin user
async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
