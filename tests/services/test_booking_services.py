from datetime import timedelta

import pytest

from bookings.bookings_schemas import BookingStatus
from bookings.bookings_services import (
    cancel_booking_service,
    change_booking_time_service,
    create_booking_service,
    get_my_booking_service,
)
from core.exceptions import (
    BookingAccessDeniedError,
    BookingAlreadyCanceledError,
    BookingConflictError,
    RoomNotFoundError,
)

pytestmark = pytest.mark.services

HOUR = timedelta(hours=1)


def book(db, user, room_id, start, end):
    return create_booking_service(
        db=db,
        user_id=user.id,
        room_id=room_id,
        start_time=start,
        end_time=end
    )


def test_create_booking_saves_active_booking(db, user, room, tomorrow):
    booking = book(db, user, room.id, tomorrow, tomorrow + HOUR)

    assert booking.id is not None
    assert booking.status == BookingStatus.ACTIVE
    assert booking.start_time == tomorrow
    assert booking.end_time == tomorrow + HOUR


def test_create_booking_for_missing_room_raises(db, user, tomorrow):
    with pytest.raises(RoomNotFoundError):
        book(db, user, 999_999, tomorrow, tomorrow + HOUR)


def test_overlapping_booking_raises_conflict(db, user, other_user, room, tomorrow):
    book(db, user, room.id, tomorrow, tomorrow + 2 * HOUR)

    with pytest.raises(BookingConflictError):
        book(db, other_user, room.id, tomorrow + HOUR, tomorrow + 3 * HOUR)


def test_adjacent_bookings_do_not_conflict(db, user, other_user, room, tomorrow):
    book(db, user, room.id, tomorrow, tomorrow + HOUR)

    booking = book(db, other_user, room.id, tomorrow + HOUR, tomorrow + 2 * HOUR)

    assert booking.id is not None


def test_canceled_booking_does_not_block_slot(db, user, other_user, room, tomorrow):
    first = book(db, user, room.id, tomorrow, tomorrow + HOUR)
    cancel_booking_service(db, user.id, first.id)

    booking = book(db, other_user, room.id, tomorrow, tomorrow + HOUR)

    assert booking.status == BookingStatus.ACTIVE


@pytest.mark.xfail(strict=True, reason="get_conflict_booking uses scalar_one_or_none: fixed in stage 5")
def test_overlap_with_several_bookings_raises_conflict(db, user, other_user, room, tomorrow):
    book(db, user, room.id, tomorrow, tomorrow + HOUR)
    book(db, user, room.id, tomorrow + 2 * HOUR, tomorrow + 3 * HOUR)

    with pytest.raises(BookingConflictError):
        book(db, other_user, room.id, tomorrow, tomorrow + 4 * HOUR)


def test_change_booking_time_within_own_slot(db, user, room, tomorrow):
    booking = book(db, user, room.id, tomorrow, tomorrow + 2 * HOUR)

    changed = change_booking_time_service(
        db=db,
        user_id=user.id,
        booking_id=booking.id,
        start_time=tomorrow + HOUR,
        end_time=tomorrow + 3 * HOUR
    )

    assert changed.start_time == tomorrow + HOUR


def test_change_booking_time_into_busy_slot_raises(db, user, other_user, room, tomorrow):
    book(db, other_user, room.id, tomorrow, tomorrow + HOUR)
    booking = book(db, user, room.id, tomorrow + 2 * HOUR, tomorrow + 3 * HOUR)

    with pytest.raises(BookingConflictError):
        change_booking_time_service(
            db=db,
            user_id=user.id,
            booking_id=booking.id,
            start_time=tomorrow,
            end_time=tomorrow + HOUR
        )


def test_change_foreign_booking_is_denied(db, user, other_user, room, tomorrow):
    booking = book(db, user, room.id, tomorrow, tomorrow + HOUR)

    with pytest.raises(BookingAccessDeniedError):
        change_booking_time_service(
            db=db,
            user_id=other_user.id,
            booking_id=booking.id,
            start_time=tomorrow + HOUR,
            end_time=tomorrow + 2 * HOUR
        )


def test_cancel_booking_sets_canceled_status(db, user, room, tomorrow):
    booking = book(db, user, room.id, tomorrow, tomorrow + HOUR)

    canceled = cancel_booking_service(db, user.id, booking.id)

    assert canceled.status == BookingStatus.CANCELED


def test_cancel_twice_raises(db, user, room, tomorrow):
    booking = book(db, user, room.id, tomorrow, tomorrow + HOUR)
    cancel_booking_service(db, user.id, booking.id)

    with pytest.raises(BookingAlreadyCanceledError):
        cancel_booking_service(db, user.id, booking.id)


def test_get_my_bookings_returns_only_own(db, user, other_user, room, tomorrow):
    own = book(db, user, room.id, tomorrow, tomorrow + HOUR)
    book(db, other_user, room.id, tomorrow + HOUR, tomorrow + 2 * HOUR)

    bookings = get_my_booking_service(db, user.id)

    assert [booking.id for booking in bookings] == [own.id]
