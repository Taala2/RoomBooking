from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from core.security import hash_password, verify_password
from users.models import User
from users.schemas import UserRole

def get_user_by_register(db: Session, login: str, email: str | None):
    if email is None:
        statement = select(User).where(User.login == login)
    else:
        statement = select(User).where(
            or_(
                User.login == login,
                User.email == email
            )
        )
    return db.execute(statement).scalar_one_or_none()

def create_user(db: Session, login: str, email: str | None, password: str):
    db_user = User(login = login,
                   email = email,
                   hashed_password = hash_password(password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, login_or_email: str, password: str):
    user = db.query(User).filter(
        or_(
            User.email == login_or_email,
            User.login == login_or_email
    )).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def change_user_by_id(db: Session, user_id: int, role: UserRole):
    user = db.get(User, user_id)

    if user is None:
        return None

    user.role = role

    db.commit()
    db.refresh(user)

    return user