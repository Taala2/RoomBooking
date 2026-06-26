from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from bookings.models import Booking
from bookings.repository import create_booking, get_booking_by_id, get_booking_by_user_id, get_conflict_booking, update_booking
from bookings.schemas import BookingStatus
from rooms.repository import get_room_by_id


def create_booking_service(
        db: Session,
        user_id: int,
        room_id: int,
        start_time: datetime,
        end_time: datetime
):
    if not validate_time(start_time, end_time):
        return None

    room = get_room_by_id(db, room_id)

    if not room:
        return None

    conflict_booking = get_conflict_booking(
        db=db,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time
    )

    if conflict_booking:
        return None


    new_booking = Booking(
        user_id=user_id,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time
    )

    return create_booking(db, new_booking)

def get_my_booking_service(db: Session, user_id: int):
    return get_booking_by_user_id(db, user_id)

def cancel_booking_service(db: Session, user_id: int, booking_id: int):
    booking = get_user_booking(db, user_id, booking_id)

    if not booking:
        return None

    if booking.status == BookingStatus.CANCELED:
        return None

    booking.status = BookingStatus.CANCELED

    return update_booking(db, booking)

def change_booking_time_service(
        db: Session,
        user_id: int,
        booking_id: int,
        start_time: datetime,
        end_time: datetime
):
    booking = get_user_booking(db, user_id, booking_id)

    if not booking:
        return None

    if not validate_time(start_time, end_time):
        return None

    if booking.status == BookingStatus.CANCELED:
        return None

    conflict = get_conflict_booking(
        db=db,
        room_id=booking.room_id,
        start_time=start_time,
        end_time=end_time,
        exclude_booking_id=booking.id
    )

    if conflict:
        return None

    booking.start_time = start_time
    booking.end_time = end_time

    return update_booking(db, booking)

def validate_time(start_time: datetime, end_time: datetime):
    if start_time >= end_time:
        return False

    if start_time < datetime.now(UTC):
        return False

    duration = end_time - start_time

    if duration > timedelta(hours=5):
        return False

    return True

def get_user_booking(db: Session, user_id: int, booking_id: int):
    booking = get_booking_by_id(db, booking_id)

    if not booking:
        return None

    if booking.user_id != user_id:
        return None

    return booking