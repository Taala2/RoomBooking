import threading
from datetime import timedelta

import pytest
from sqlalchemy import func, select

from bookings import bookings_services
from bookings.bookings_models import Booking
from bookings.bookings_schemas import BookingStatus
from core.exceptions import BookingConflictError
from tests.factories import make_room, make_user

pytestmark = pytest.mark.concurrency

PARALLEL_REQUESTS = 2
BARRIER_TIMEOUT_SECONDS = 10
HOUR = timedelta(hours=1)


def pause_after_conflict_check(monkeypatch):
    """Make every request finish the conflict check before anyone saves."""
    barrier = threading.Barrier(PARALLEL_REQUESTS, timeout=BARRIER_TIMEOUT_SECONDS)
    original = bookings_services.get_conflict_booking

    def check_then_wait(*args, **kwargs):
        result = original(*args, **kwargs)
        barrier.wait()
        return result

    monkeypatch.setattr(bookings_services, "get_conflict_booking", check_then_wait)


def run_in_parallel(session_factory, action):
    """Call action(session, index) in separate threads and sessions, collect outcomes."""
    results = []

    def worker(index):
        with session_factory() as session:
            try:
                action(session, index)
                results.append("saved")
            except BookingConflictError:
                results.append("conflict")
            except Exception as exc:
                pgcode = getattr(getattr(exc, "orig", None), "pgcode", None)
                results.append(f"{type(exc).__name__}:{pgcode}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(PARALLEL_REQUESTS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=BARRIER_TIMEOUT_SECONDS * 2)

    return sorted(results)


def count_active_bookings(session_factory, room_id, start, end):
    with session_factory() as session:
        return session.scalar(
            select(func.count()).select_from(Booking).where(
                Booking.room_id == room_id,
                Booking.status == BookingStatus.ACTIVE,
                Booking.start_time < end,
                Booking.end_time > start
            )
        )


def test_parallel_bookings_of_same_slot_create_only_one(session_factory, monkeypatch, tomorrow):
    with session_factory() as setup:
        user_id = make_user(setup, "racer").id
        room_id = make_room(setup).id

    pause_after_conflict_check(monkeypatch)

    def create(session, _):
        bookings_services.create_booking_service(
            db=session,
            user_id=user_id,
            room_id=room_id,
            start_time=tomorrow,
            end_time=tomorrow + HOUR
        )

    results = run_in_parallel(session_factory, create)

    assert results == ["conflict", "saved"]
    assert count_active_bookings(session_factory, room_id, tomorrow, tomorrow + HOUR) == 1


def test_parallel_changes_into_same_slot_save_only_one(session_factory, monkeypatch, tomorrow):
    with session_factory() as setup:
        room_id = make_room(setup).id
        owners = []

        for index in range(PARALLEL_REQUESTS):
            user = make_user(setup, f"mover{index}")
            booking = bookings_services.create_booking_service(
                db=setup,
                user_id=user.id,
                room_id=room_id,
                start_time=tomorrow + (2 * index + 2) * HOUR,
                end_time=tomorrow + (2 * index + 3) * HOUR
            )
            owners.append((user.id, booking.id))

    pause_after_conflict_check(monkeypatch)

    def move_to_first_hour(session, index):
        user_id, booking_id = owners[index]
        bookings_services.change_booking_time_service(
            db=session,
            user_id=user_id,
            booking_id=booking_id,
            start_time=tomorrow,
            end_time=tomorrow + HOUR
        )

    results = run_in_parallel(session_factory, move_to_first_hour)

    assert results == ["conflict", "saved"]
    assert count_active_bookings(session_factory, room_id, tomorrow, tomorrow + HOUR) == 1
