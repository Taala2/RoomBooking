from typing import Annotated
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt

from core.database import get_db
from core.security import ALGORITHM, SECRET_KEY
from users.users_models import User
from users.users_repositories import get_user_by_id
from users.users_schemas import UserRole


security = HTTPBearer()

def unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )

def get_current_user(
        credential: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(get_db)
    ) -> User:
    token = credential.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]}
        )
    except jwt.InvalidTokenError:
        raise unauthorized("Токен недействителен или истёк")

    user_id = payload.get("sub")

    if not isinstance(user_id, str) or not user_id.isdigit():
        raise unauthorized("Токен недействителен или истёк")

    user = get_user_by_id(session, int(user_id))

    if not user:
        raise unauthorized("Пользователь не найден")

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

# Larger offsets overflow PostgreSQL bigint (500) and are never needed in practice.
MAX_OFFSET = 1_000_000

Page_offset = Annotated[
    int,
    Query(ge=0, le=MAX_OFFSET)
]

Current_session = Annotated[
    Session,
    Depends(get_db)
]