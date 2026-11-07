import logging

import pytest
from fastapi.testclient import TestClient

from main import app
from rooms import rooms_routers

pytestmark = pytest.mark.api


def test_unhandled_error_returns_500_without_details_and_is_logged(client, monkeypatch, caplog):
    def broken_service(*_args, **_kwargs):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(rooms_routers, "get_rooms_service", broken_service)
    # The default client re-raises server errors; this one returns the 500 response.
    safe_client = TestClient(app, raise_server_exceptions=False)

    with caplog.at_level(logging.ERROR, logger="core.handlers"):
        response = safe_client.get("/rooms/list")

    assert response.status_code == 500
    assert response.json() == {"detail": "Внутренняя ошибка сервера"}
    assert "secret internal detail" not in response.text
    assert "Unhandled RuntimeError on GET /rooms/list" in caplog.text
