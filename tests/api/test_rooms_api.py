from datetime import UTC, datetime, timedelta

import pytest

from bookings.bookings_models import Booking
from bookings.bookings_repositories import create_booking, get_booking_by_id
from tests.factories import auth_headers

pytestmark = pytest.mark.api

CREATE_URL = "/rooms/create"
NEW_ROOM = {"name": "Большой зал", "capacity": 30, "description": "Проектор"}


def room_url(room_id: int) -> str:
    return f"/rooms/{room_id}"


def change_url(room_id: int) -> str:
    return f"/rooms/change/{room_id}"


def delete_url(room_id: int) -> str:
    return f"/rooms/delete/{room_id}"


def add_booking(db, user, room, start):
    """Insert directly: the service would reject bookings in the past."""
    booking = Booking(user_id=user.id, room_id=room.id, start_time=start, end_time=start + timedelta(hours=1))
    return create_booking(db, booking)


def test_admin_creates_room(client, admin):
    response = client.post(CREATE_URL, json=NEW_ROOM, headers=auth_headers(admin))

    assert response.status_code == 201
    assert response.json()["name"] == NEW_ROOM["name"]


def test_regular_user_cannot_create_room(client, user):
    assert client.post(CREATE_URL, json=NEW_ROOM, headers=auth_headers(user)).status_code == 403


def test_get_existing_room(client, room):
    response = client.get(room_url(room.id))

    assert response.status_code == 200
    assert response.json()["id"] == room.id


def test_get_missing_room_returns_404(client):
    assert client.get(room_url(999_999)).status_code == 404


def test_list_rooms_returns_page(client, room):
    response = client.get("/rooms/list")

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_change_uses_room_id_from_path_and_keeps_other_fields(client, admin, room):
    response = client.patch(change_url(room.id), json={"capacity": 25}, headers=auth_headers(admin))

    assert response.status_code == 200
    assert response.json()["capacity"] == 25
    assert response.json()["name"] == room.name


def test_change_can_clear_description(client, admin, room):
    client.patch(change_url(room.id), json={"description": "temp"}, headers=auth_headers(admin))

    response = client.patch(change_url(room.id), json={"description": None}, headers=auth_headers(admin))

    assert response.json()["description"] is None


def test_change_rejects_null_name(client, admin, room):
    response = client.patch(change_url(room.id), json={"name": None}, headers=auth_headers(admin))

    assert response.status_code == 422


def test_change_missing_room_returns_404(client, admin):
    assert client.patch(change_url(999_999), json={"capacity": 5}, headers=auth_headers(admin)).status_code == 404


def test_delete_requires_token(client, room):
    assert client.delete(delete_url(room.id)).status_code == 401


def test_regular_user_cannot_delete_room(client, user, room):
    assert client.delete(delete_url(room.id), headers=auth_headers(user)).status_code == 403


def test_old_broken_delete_path_is_gone(client, admin, room):
    assert client.delete(f"/roomsdelete/{room.id}", headers=auth_headers(admin)).status_code == 404


def test_admin_deletes_room(client, admin, room):
    assert client.delete(delete_url(room.id), headers=auth_headers(admin)).status_code == 204
    assert client.get(room_url(room.id)).status_code == 404


def test_room_with_upcoming_booking_cannot_be_deleted(client, db, admin, user, room):
    add_booking(db, user, room, datetime.now(UTC) + timedelta(days=1))

    assert client.delete(delete_url(room.id), headers=auth_headers(admin)).status_code == 409


def test_room_with_only_past_bookings_is_deleted_with_them(client, db, admin, user, room):
    past = add_booking(db, user, room, datetime.now(UTC) - timedelta(days=1))
    past_id = past.id

    assert client.delete(delete_url(room.id), headers=auth_headers(admin)).status_code == 204

    db.expire_all()
    assert get_booking_by_id(db, past_id) is None
