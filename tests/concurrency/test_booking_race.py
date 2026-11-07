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


def pause_after_conflict_check(monkeypatch, barrier):
    """Make every request finish the conflict check before anyone inserts."""
    original = bookings_services.get_conflict_booking

    def check_then_wait(*args, **kwargs):
        result = original(*args, **kwargs)
        barrier.wait()
        return result

    monkeypatch.setattr(bookings_services, "get_conflict_booking", check_then_wait)


@pytest.mark.xfail(strict=True, reason="race condition in create_booking_service: fixed in stage 5")
def test_parallel_bookings_of_same_slot_create_only_one(session_factory, monkeypatch, tomorrow):
    with session_factory() as setup:
        user_id = make_user(setup, "racer").id
        room_id = make_room(setup).id

    pause_after_conflict_check(
        monkeypatch,
        threading.Barrier(PARALLEL_REQUESTS, timeout=BARRIER_TIMEOUT_SECONDS)
    )
    results = []

    def try_to_book():
        with session_factory() as session:
            try:
                bookings_services.create_booking_service(
                    db=session,
                    user_id=user_id,
                    room_id=room_id,
                    start_time=tomorrow,
                    end_time=tomorrow + timedelta(hours=1)
                )
                results.append("created")
            except BookingConflictError:
                results.append("conflict")
            except Exception as exc:
                results.append(type(exc).__name__)

    threads = [threading.Thread(target=try_to_book) for _ in range(PARALLEL_REQUESTS)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=BARRIER_TIMEOUT_SECONDS * 2)

    with session_factory() as check:
        active_count = check.scalar(
            select(func.count()).select_from(Booking).where(
                Booking.room_id == room_id,
                Booking.status == BookingStatus.ACTIVE
            )
        )

    assert sorted(results) == ["conflict", "created"]
    assert active_count == 1
