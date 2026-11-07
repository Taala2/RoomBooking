import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine, make_url, text
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings
from core.database import get_db
from main import app
from tests.factories import make_room, make_user
from users.users_schemas import UserRole

ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"


def get_test_database_url() -> URL:
    url = os.getenv("TEST_DATABASE_URL")

    if url:
        return make_url(url)

    real_url = make_url(settings.database_url)
    return real_url.set(database=f"{real_url.database}_test")


TEST_DATABASE_URL = get_test_database_url()

if not TEST_DATABASE_URL.database.endswith("_test"):
    raise RuntimeError(
        f"Тесты запускаются только на БД с суффиксом _test, получено: {TEST_DATABASE_URL.database}"
    )


def recreate_test_database() -> None:
    name = TEST_DATABASE_URL.database
    admin_engine = create_engine(
        TEST_DATABASE_URL.set(database="postgres"),
        isolation_level="AUTOCOMMIT"
    )

    with admin_engine.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        connection.execute(text(f'CREATE DATABASE "{name}"'))

    admin_engine.dispose()


def run_migrations() -> None:
    config = Config(str(ALEMBIC_INI))
    url = TEST_DATABASE_URL.render_as_string(hide_password=False)
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    command.upgrade(config, "head")


@pytest.fixture(scope="session")
def test_engine():
    recreate_test_database()
    run_migrations()

    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture
def db(test_engine):
    """Session whose commits are rolled back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """API client whose requests use the rolled-back test session."""
    app.dependency_overrides[get_db] = lambda: db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def session_factory(test_engine):
    """Independent sessions with real commits; tables are truncated afterwards."""
    yield sessionmaker(bind=test_engine, autoflush=False)

    with test_engine.begin() as connection:
        connection.execute(text("TRUNCATE bookings, rooms, users RESTART IDENTITY CASCADE"))


@pytest.fixture
def tomorrow() -> datetime:
    """Start of the next full hour one day ahead (UTC), fixed for the whole test."""
    moment = datetime.now(UTC) + timedelta(days=1)
    return moment.replace(minute=0, second=0, microsecond=0)


@pytest.fixture
def user(db):
    return make_user(db, "user")


@pytest.fixture
def other_user(db):
    return make_user(db, "other_user")


@pytest.fixture
def admin(db):
    return make_user(db, "admin", UserRole.ADMIN)


@pytest.fixture
def room(db):
    return make_room(db)
