import pytest

from core.exceptions import EmailAlreadyExistsError, UsernameAlreadyExistsError
from users import users_services

pytestmark = pytest.mark.services


@pytest.fixture
def skip_duplicate_check(monkeypatch):
    """Simulate a concurrent registration: the pre-check sees no existing user."""
    monkeypatch.setattr(users_services, "get_user_by_login_or_email", lambda *_: None)


def test_concurrent_duplicate_login_is_caught_by_database(db, user, skip_duplicate_check):
    with pytest.raises(UsernameAlreadyExistsError):
        users_services.create_user_service(db, user.login, "fresh@example.com", "password123")


def test_concurrent_duplicate_email_is_caught_by_database(db, user, skip_duplicate_check):
    with pytest.raises(EmailAlreadyExistsError):
        users_services.create_user_service(db, "fresh_login", user.email, "password123")
