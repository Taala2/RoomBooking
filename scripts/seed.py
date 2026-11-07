"""Create the first administrator and demo rooms.

Usage:
    python -m scripts.seed --login admin --email admin@example.com
    docker compose exec api python -m scripts.seed --login admin --email admin@example.com

The password is asked interactively or taken from SEED_ADMIN_PASSWORD.
Safe to run again: an existing user is promoted, rooms are added only to an empty database.
"""
import argparse
import getpass
import logging
import os

from pydantic import ValidationError
from sqlalchemy.orm import Session

from core.database import SessionLocal
from main import app  # noqa: F401  (imports all models so relationships resolve)
from rooms.rooms_models import Room
from rooms.rooms_repositories import count_rooms, create_room
from users.users_models import User
from users.users_repositories import get_user_by_login_or_email, update_user
from users.users_schemas import UserCreateRequest, UserRole
from users.users_services import create_user_service

logger = logging.getLogger("seed")

DEMO_ROOMS = (
    ("Переговорная «Альфа»", 6, "Телевизор для презентаций"),
    ("Переговорная «Бета»", 10, "Проектор и маркерная доска"),
    ("Конференц-зал", 40, "Проектор, микрофоны, видеосвязь"),
    ("Тихая комната", 2, "Для звонков и сосредоточенной работы"),
)


def ensure_admin(db: Session, login: str, email: str, password: str) -> User:
    """Create the admin, or give the admin role to an existing user with this login/email."""
    data = UserCreateRequest(login=login, email=email, password=password)
    user = get_user_by_login_or_email(db, data.login, data.email)

    if not user:
        user = create_user_service(db, data.login, data.email, data.password)
        logger.info("Created user %s", user.login)

    if user.role != UserRole.ADMIN:
        user.role = UserRole.ADMIN
        user = update_user(db, user)
        logger.info("User %s is now admin", user.login)

    return user


def ensure_demo_rooms(db: Session) -> int:
    """Add demo rooms only when there are no rooms yet; returns how many were created."""
    if count_rooms(db) > 0:
        logger.info("Rooms already exist, demo rooms skipped")
        return 0

    for name, capacity, description in DEMO_ROOMS:
        create_room(db, Room(name=name, capacity=capacity, description=description))

    logger.info("Created %s demo rooms", len(DEMO_ROOMS))
    return len(DEMO_ROOMS)


def read_password() -> str:
    return os.environ.get("SEED_ADMIN_PASSWORD") or getpass.getpass("Пароль администратора: ")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create the first admin and demo rooms")
    parser.add_argument("--login", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--no-rooms", action="store_true", help="do not add demo rooms")
    args = parser.parse_args(argv)

    try:
        with SessionLocal() as db:
            ensure_admin(db, args.login, args.email, read_password())

            if not args.no_rooms:
                ensure_demo_rooms(db)
    except ValidationError as exc:
        logger.error("Invalid admin data: %s", "; ".join(error["msg"] for error in exc.errors()))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
