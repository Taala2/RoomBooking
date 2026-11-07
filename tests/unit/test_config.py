import pytest
from pydantic import ValidationError

from core.config import Settings

pytestmark = pytest.mark.unit

DATABASE_URL = "postgresql+psycopg2://user:pass@localhost:5432/room_booking"


def test_secret_key_from_env_example_is_rejected():
    with pytest.raises(ValidationError, match="SECRET_KEY"):
        Settings(database_url=DATABASE_URL, secret_key="change-me-to-a-long-random-string")


def test_short_secret_key_is_rejected():
    with pytest.raises(ValidationError):
        Settings(database_url=DATABASE_URL, secret_key="short")


def test_random_secret_key_is_accepted():
    settings = Settings(database_url=DATABASE_URL, secret_key="k3v9" * 10)

    assert settings.secret_key == "k3v9" * 10
