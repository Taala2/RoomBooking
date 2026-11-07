import pytest
from pydantic import ValidationError

from rooms.rooms_repositories import count_rooms
from scripts import seed
from users.users_repositories import get_user_by_login_or_email
from users.users_schemas import UserRole

pytestmark = pytest.mark.services

ADMIN_PASSWORD = "admin-password-123"


def test_ensure_admin_creates_admin(db):
    admin = seed.ensure_admin(db, "boss", "Boss@Example.com", ADMIN_PASSWORD)

    assert admin.role == UserRole.ADMIN
    assert admin.email == "boss@example.com"


def test_ensure_admin_promotes_existing_user(db, user):
    admin = seed.ensure_admin(db, user.login, user.email, ADMIN_PASSWORD)

    assert admin.id == user.id
    assert admin.role == UserRole.ADMIN


def test_ensure_admin_is_idempotent(db):
    first = seed.ensure_admin(db, "boss", "boss@example.com", ADMIN_PASSWORD)
    second = seed.ensure_admin(db, "boss", "boss@example.com", ADMIN_PASSWORD)

    assert first.id == second.id


def test_ensure_admin_rejects_short_password(db):
    with pytest.raises(ValidationError):
        seed.ensure_admin(db, "boss", "boss@example.com", "short")


def test_demo_rooms_are_added_only_to_empty_database(db):
    created_first = seed.ensure_demo_rooms(db)
    created_again = seed.ensure_demo_rooms(db)

    assert created_first == len(seed.DEMO_ROOMS)
    assert created_again == 0
    assert count_rooms(db) == len(seed.DEMO_ROOMS)


def test_main_uses_password_from_environment(db, monkeypatch):
    monkeypatch.setattr(seed, "SessionLocal", lambda: db)
    monkeypatch.setenv("SEED_ADMIN_PASSWORD", ADMIN_PASSWORD)

    exit_code = seed.main(["--login", "boss", "--email", "boss@example.com"])

    admin = get_user_by_login_or_email(db, "boss", "boss@example.com")
    assert exit_code == 0
    assert admin.role == UserRole.ADMIN
    assert count_rooms(db) == len(seed.DEMO_ROOMS)


def test_main_returns_error_code_for_invalid_email(db, monkeypatch):
    monkeypatch.setattr(seed, "SessionLocal", lambda: db)
    monkeypatch.setenv("SEED_ADMIN_PASSWORD", ADMIN_PASSWORD)

    assert seed.main(["--login", "boss", "--email", "not-an-email", "--no-rooms"]) == 1
