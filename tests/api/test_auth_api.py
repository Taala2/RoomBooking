from datetime import UTC, datetime, timedelta

import jwt
import pytest

from core.security import ALGORITHM, SECRET_KEY
from tests.factories import auth_headers

pytestmark = pytest.mark.api

ME_URL = "/users/me"


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def make_token(payload: dict) -> str:
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)


def test_valid_token_returns_profile(client, user):
    response = client.get(ME_URL, headers=auth_headers(user))

    assert response.status_code == 200
    assert response.json()["login"] == user.login


def test_missing_token_returns_401(client):
    assert client.get(ME_URL).status_code == 401


def test_garbage_token_returns_401(client):
    response = client.get(ME_URL, headers=bearer("not-a-jwt"))

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_token_signed_with_other_key_returns_401(client, user):
    token = jwt.encode({"sub": str(user.id)}, "x" * 32, ALGORITHM)

    assert client.get(ME_URL, headers=bearer(token)).status_code == 401


def test_expired_token_returns_401(client, user):
    expired = datetime.now(UTC) - timedelta(minutes=1)
    token = make_token({"sub": str(user.id), "exp": expired})

    assert client.get(ME_URL, headers=bearer(token)).status_code == 401


@pytest.mark.parametrize("payload", [{}, {"sub": "abc"}, {"sub": 5}])
def test_token_without_valid_sub_returns_401(client, payload):
    assert client.get(ME_URL, headers=bearer(make_token(payload))).status_code == 401


def test_token_of_missing_user_returns_401(client):
    token = make_token({"sub": "999999"})

    assert client.get(ME_URL, headers=bearer(token)).status_code == 401
