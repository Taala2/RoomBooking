from typing import Annotated

import bcrypt
from fastapi import Depends
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.database import get_db
from users.models import User
from users.schemas import UserRole

security = HTTPBearer()

SECRET_KEY = "SUPER_SECRET_RANDOM_STRING_CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(user_id),
        "exp": expire
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt

def get_current_user(credential: HTTPAuthorizationCredentials = Depends(security),
                     session: Session = Depends(get_db)) -> User:
    token = credential.credentials

    payload = jwt.decode(
        token,
        SECRET_KEY,
        ALGORITHM
    )

    user_id = payload.get("sub")

    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    return user

Current_user = Annotated[
    User,
    Depends(get_current_user)
]

def get_current_admin(current_user: Current_user) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    return current_user

Current_admin = Annotated[
    User,
    Depends(get_current_admin)
]