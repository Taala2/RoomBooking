from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt

from core.database import get_db
from core.security import ALGORITHM, SECRET_KEY
from users.models import User
from users.repository import get_user_by_id
from users.schemas import UserRole


security = HTTPBearer()

def get_current_user(
        credential: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_db)
    ) -> User:
    token = credential.credentials

    payload = jwt.decode(
        token,
        SECRET_KEY,
        ALGORITHM
    )

    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Токен не действителен"
        )

    user = get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    return user

def get_current_admin(current_user: Current_user) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    return current_user

Current_user = Annotated[
    User,
    Depends(get_current_user)
]

Current_admin = Annotated[
    User,
    Depends(get_current_admin)
]