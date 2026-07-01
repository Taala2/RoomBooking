from sqlalchemy.orm import Session

from core.exceptions import AdminCannotDemoteSelfError, EmailAlreadyExistsError, IncorrectPasswordError, UserNotFoundError, UsernameAlreadyExistsError
from core.security import hash_password, verify_password
from users.users_models import User
from users.users_repositories import create_user, get_user_by_id, get_user_by_login_or_email, update_user
from users.users_schemas import UserRole


def create_user_service(db: Session, login: str, email: str, password: str):
    user = get_user_by_login_or_email(db, login, email)

    if user:
        if user.email == email:
            raise EmailAlreadyExistsError("Такая почта уже занята")

        if user.login == login:
            raise UsernameAlreadyExistsError("Такой логин уже занят")

    new_user = User(login = login,
                   email = email,
                   hashed_password = hash_password(password))

    return create_user(db, new_user)

def authenticate_user_service(db: Session, login_or_email: str, password: str):
    user = get_user_by_login_or_email(db, login_or_email, login_or_email)

    if not user:
        raise UserNotFoundError("Такого пользователя не существует")

    if not verify_password(password, user.hashed_password):
        raise IncorrectPasswordError("Не верный пароль")

    return user

def change_user_role_service(db: Session, current_user: User, user_id: int, role: UserRole):
    user = get_user_by_id(db, user_id)

    if not user:
        raise UserNotFoundError("Такого пользователя не существует")

    if current_user.role == user.role:
        raise AdminCannotDemoteSelfError("Админ не может изменить свою роль")

    user.role = role

    return update_user(db, user)