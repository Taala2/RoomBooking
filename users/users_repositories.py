from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from users.users_models import User


def get_user_by_id(db: Session, user_id: int):
    user = db.get(User, user_id)
    return user

def get_user_by_login_or_email(db: Session, login: str, email: str):
    stmt = select(User).where(or_(
        User.login == login,
        func.lower(User.email) == email.lower()
    ))

    return db.execute(stmt.limit(1)).scalars().first()

def get_users(db: Session, limit: int, offset: int):
    stmt = select(User).order_by(User.id).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())

def count_users(db: Session):
    stmt = select(func.count()).select_from(User)
    return db.scalar(stmt) or 0

def create_user(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: User):
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()