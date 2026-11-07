from datetime import UTC, datetime, timedelta, timezone

import pytest

from bookings.bookings_services import validate_time
from core.exceptions import InvalidBookingTimeError

pytestmark = pytest.mark.unit

MAX_DURATION = timedelta(hours=5)


def test_valid_interval_passes(tomorrow):
    validate_time(tomorrow, tomorrow + timedelta(hours=1))


def test_end_before_start_raises(tomorrow):
    with pytest.raises(InvalidBookingTimeError):
        validate_time(tomorrow, tomorrow - timedelta(hours=1))


def test_end_equal_to_start_raises(tomorrow):
    with pytest.raises(InvalidBookingTimeError):
        validate_time(tomorrow, tomorrow)


def test_start_in_past_raises():
    start = datetime.now(UTC) - timedelta(minutes=1)

    with pytest.raises(InvalidBookingTimeError):
        validate_time(start, start + timedelta(hours=1))


def test_exactly_max_duration_is_allowed(tomorrow):
    validate_time(tomorrow, tomorrow + MAX_DURATION)


def test_longer_than_max_duration_raises(tomorrow):
    with pytest.raises(InvalidBookingTimeError):
        validate_time(tomorrow, tomorrow + MAX_DURATION + timedelta(minutes=1))


def test_other_timezone_is_compared_as_same_moment():
    almaty = timezone(timedelta(hours=5))
    one_hour_ago = (datetime.now(UTC) - timedelta(hours=1)).astimezone(almaty)

    with pytest.raises(InvalidBookingTimeError):
        validate_time(one_hour_ago, one_hour_ago + timedelta(minutes=30))
