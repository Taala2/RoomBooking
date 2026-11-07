from datetime import UTC, datetime, timedelta, timezone

import pytest

from tests.factories import auth_headers

pytestmark = pytest.mark.api

BOOKINGS_URL = "/bookings/"
CANCEL_URL = "/bookings/cancel"
CHANGE_URL = "/bookings/change"
HOUR = timedelta(hours=1)


def iso(moment: datetime) -> str:
    return moment.isoformat()


def create(client, user, room_id, start, end):
    payload = {"room_id": room_id, "start_time": iso(start), "end_time": iso(end)}
    return client.post(BOOKINGS_URL, json=payload, headers=auth_headers(user))


def parse(value: str) -> datetime:
    return datetime.fromisoformat(value)


def test_create_booking_returns_201_with_status(client, user, room, tomorrow):
    response = create(client, user, room.id, tomorrow, tomorrow + HOUR)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "active"
    assert parse(body["start_time"]) == tomorrow
    assert "created_at" in body


def test_create_booking_without_token_returns_401(client, room, tomorrow):
    payload = {"room_id": room.id, "start_time": iso(tomorrow), "end_time": iso(tomorrow + HOUR)}

    assert client.post(BOOKINGS_URL, json=payload).status_code == 401


def test_naive_datetime_returns_422(client, user, room, tomorrow):
    naive = tomorrow.replace(tzinfo=None)

    assert create(client, user, room.id, naive, naive + HOUR).status_code == 422


def test_other_offset_is_stored_as_same_moment(client, user, room, tomorrow):
    almaty = timezone(timedelta(hours=5))
    start = tomorrow.astimezone(almaty)

    response = create(client, user, room.id, start, start + HOUR)

    assert parse(response.json()["start_time"]) == tomorrow


def test_overlapping_booking_returns_409(client, user, other_user, room, tomorrow):
    create(client, user, room.id, tomorrow, tomorrow + 2 * HOUR)

    assert create(client, other_user, room.id, tomorrow + HOUR, tomorrow + 3 * HOUR).status_code == 409


def test_booking_in_past_returns_400(client, user, room):
    past = datetime.now(UTC) - HOUR

    assert create(client, user, room.id, past, past + HOUR).status_code == 400


def test_booking_missing_room_returns_404(client, user, tomorrow):
    assert create(client, user, 999_999, tomorrow, tomorrow + HOUR).status_code == 404


def test_my_bookings_are_sorted_and_only_own(client, user, other_user, room, tomorrow):
    late = create(client, user, room.id, tomorrow + 3 * HOUR, tomorrow + 4 * HOUR).json()
    early = create(client, user, room.id, tomorrow, tomorrow + HOUR).json()
    create(client, other_user, room.id, tomorrow + HOUR, tomorrow + 2 * HOUR)

    response = client.get(BOOKINGS_URL, headers=auth_headers(user))

    assert response.status_code == 200
    assert [booking["id"] for booking in response.json()] == [early["id"], late["id"]]
    assert all(booking["status"] == "active" for booking in response.json())


def test_cancel_returns_canceled_booking(client, user, room, tomorrow):
    booking = create(client, user, room.id, tomorrow, tomorrow + HOUR).json()

    response = client.post(CANCEL_URL, json={"booking_id": booking["id"]}, headers=auth_headers(user))

    assert response.status_code == 200
    assert response.json()["status"] == "canceled"


def test_cancel_twice_returns_409(client, user, room, tomorrow):
    booking = create(client, user, room.id, tomorrow, tomorrow + HOUR).json()
    client.post(CANCEL_URL, json={"booking_id": booking["id"]}, headers=auth_headers(user))

    response = client.post(CANCEL_URL, json={"booking_id": booking["id"]}, headers=auth_headers(user))

    assert response.status_code == 409


def test_cancel_foreign_booking_returns_403(client, user, other_user, room, tomorrow):
    booking = create(client, user, room.id, tomorrow, tomorrow + HOUR).json()

    response = client.post(CANCEL_URL, json={"booking_id": booking["id"]}, headers=auth_headers(other_user))

    assert response.status_code == 403


def test_cancel_missing_booking_returns_404(client, user):
    response = client.post(CANCEL_URL, json={"booking_id": 999_999}, headers=auth_headers(user))

    assert response.status_code == 404


def test_change_returns_booking_with_new_time(client, user, room, tomorrow):
    booking = create(client, user, room.id, tomorrow, tomorrow + HOUR).json()
    payload = {"booking_id": booking["id"], "start_time": iso(tomorrow + 2 * HOUR), "end_time": iso(tomorrow + 3 * HOUR)}

    response = client.post(CHANGE_URL, json=payload, headers=auth_headers(user))

    assert response.status_code == 200
    assert parse(response.json()["start_time"]) == tomorrow + 2 * HOUR


def test_change_into_busy_slot_returns_409(client, user, other_user, room, tomorrow):
    create(client, other_user, room.id, tomorrow, tomorrow + HOUR)
    booking = create(client, user, room.id, tomorrow + 2 * HOUR, tomorrow + 3 * HOUR).json()
    payload = {"booking_id": booking["id"], "start_time": iso(tomorrow), "end_time": iso(tomorrow + HOUR)}

    assert client.post(CHANGE_URL, json=payload, headers=auth_headers(user)).status_code == 409
