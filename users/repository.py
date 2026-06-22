from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from users.models import User


def get_by_id(db: Session, user_id: int):
    user = db.get(User, user_id)
    return user

def get_user_by_login_or_email(db: Session, login: str, email: str):
    stmt = select(User).where(or_(
        User.login == login,
        User.email == email
    ))

    user = db.execute(stmt).scalar_one_or_none()

    return user

def create(db: Session, user: User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update(db: Session, user: User):
    db.commit()
    db.refresh(user)
    return user

def delete(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()