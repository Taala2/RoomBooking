from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from bookings.models import Booking
from bookings.repository import create_booking, get_booking_by_id, get_booking_by_user_id, get_conflict_booking, update_booking
from bookings.schemas import BookingStatus
from core.exceptions import BookingAccessDeniedError, BookingAlreadyCanceledError, BookingConflictError, BookingNotFoundError, InvalidBookingTimeError, RoomNotFoundError
from rooms.repository import get_room_by_id


def create_booking_service(
        db: Session,
        user_id: int,
        room_id: int,
        start_time: datetime,
        end_time: datetime
):
    validate_time(start_time, end_time)

    room = get_room_by_id(db, room_id)

    if not room:
        raise RoomNotFoundError("Комната не найдено")

    conflict_booking = get_conflict_booking(
        db=db,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time
    )

    if conflict_booking:
        raise BookingConflictError("На введенное время текущая комната занята")

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

    validate_time(start_time, end_time)

    conflict = get_conflict_booking(
        db=db,
        room_id=booking.room_id,
        start_time=start_time,
        end_time=end_time,
        exclude_booking_id=booking.id
    )

    if conflict:
        raise BookingConflictError("На введенное время текущая комната занята")

    booking.start_time = start_time
    booking.end_time = end_time

    return update_booking(db, booking)

def validate_time(start_time: datetime, end_time: datetime):
    if start_time >= end_time:
        raise InvalidBookingTimeError("Время окончания должно быть позже времени начала")

    if start_time < datetime.now(UTC):
        raise InvalidBookingTimeError("Нельзя бронировать время в прошлом")

    duration = end_time - start_time

    if duration > timedelta(hours=5):
        raise InvalidBookingTimeError("Максимальная длительность бронирования — 5 часов")

def get_user_booking(db: Session, user_id: int, booking_id: int):
    booking = get_booking_by_id(db, booking_id)

    if not booking:
        raise BookingNotFoundError("Бронь не найдено")

    if booking.user_id != user_id:
        raise BookingAccessDeniedError("У вас нет доступа к этой брони")

    if booking.status == BookingStatus.CANCELED:
        raise BookingAlreadyCanceledError("Бронь уже отменен")

    return booking