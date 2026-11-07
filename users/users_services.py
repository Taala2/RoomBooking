from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.exceptions import AdminCannotDemoteSelfError, EmailAlreadyExistsError, IncorrectPasswordError, UserNotFoundError, UsernameAlreadyExistsError
from core.security import hash_password, verify_password
from users.users_models import User
from users.users_repositories import create_user, get_user_by_id, get_user_by_login_or_email, update_user
from users.users_schemas import UserRole

LOGIN_TAKEN_MESSAGE = "Такой логин уже занят"
EMAIL_TAKEN_MESSAGE = "Такая почта уже занята"


def create_user_service(db: Session, login: str, email: str, password: str):
    user = get_user_by_login_or_email(db, login, email)

    if user:
        if user.email == email:
            raise EmailAlreadyExistsError(EMAIL_TAKEN_MESSAGE)

        if user.login == login:
            raise UsernameAlreadyExistsError(LOGIN_TAKEN_MESSAGE)

    new_user = User(login = login,
                   email = email,
                   hashed_password = hash_password(password))

    try:
        return create_user(db, new_user)
    except IntegrityError as exc:
        db.rollback()
        raise_if_duplicate(exc)
        raise

def raise_if_duplicate(exc: IntegrityError):
    """Concurrent registration with the same login/email is caught by unique constraints."""
    constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)

    if constraint == "users_email_key":
        raise EmailAlreadyExistsError(EMAIL_TAKEN_MESSAGE) from exc

    if constraint == "users_login_key":
        raise UsernameAlreadyExistsError(LOGIN_TAKEN_MESSAGE) from exc

def authenticate_user_service(db: Session, login_or_email: str, password: str):
    user = get_user_by_login_or_email(db, login_or_email, login_or_email)

    # Same error for unknown login and wrong password: do not reveal which logins exist.
    if not user or not verify_password(password, user.hashed_password):
        raise IncorrectPasswordError("Неверный логин или пароль")

    return user

def change_user_role_service(db: Session, current_user: User, user_id: int, role: UserRole):
    user = get_user_by_id(db, user_id)

    if not user:
        raise UserNotFoundError("Пользователь не найден")

    if current_user.id == user.id:
        raise AdminCannotDemoteSelfError("Админ не может изменить свою роль")

    user.role = role

    return update_user(db, user)