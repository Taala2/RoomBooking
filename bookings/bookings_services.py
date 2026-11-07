import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from bookings.bookings_models import Booking
from bookings.bookings_repositories import create_booking, get_booking_by_id, get_booking_by_user_id, get_conflict_booking, update_booking
from bookings.bookings_schemas import BookingStatus
from core.exceptions import BookingAccessDeniedError, BookingAlreadyCanceledError, BookingConflictError, BookingNotFoundError, InvalidBookingTimeError, RoomNotFoundError
from rooms.rooms_repositories import get_room_by_id

BOOKING_CONFLICT_MESSAGE = "На введенное время текущая комната занята"
# 23P01: overlap rejected by bookings_no_overlap.
# 40P01: two overlapping writes waited for each other and Postgres aborted one.
OVERLAP_ERROR_CODES = {"23P01", "40P01"}

logger = logging.getLogger(__name__)


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
        raise RoomNotFoundError("Комната не найдена")

    conflict_booking = get_conflict_booking(
        db=db,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time
    )

    if conflict_booking:
        logger.info("Booking conflict: room=%s overlaps booking %s", room_id, conflict_booking.id)
        raise BookingConflictError(BOOKING_CONFLICT_MESSAGE)

    new_booking = Booking(
        user_id=user_id,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time
    )

    booking = save_without_overlap(db, create_booking, new_booking)
    logger.info("Booking %s created: room=%s user=%s %s..%s", booking.id, room_id, user_id, start_time, end_time)

    return booking

def get_my_booking_service(db: Session, user_id: int):
    return get_booking_by_user_id(db, user_id)

def cancel_booking_service(db: Session, user_id: int, booking_id: int):
    booking = get_user_booking(db, user_id, booking_id)

    booking.status = BookingStatus.CANCELED

    canceled = update_booking(db, booking)
    logger.info("Booking %s canceled by user=%s", booking_id, user_id)

    return canceled

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
        logger.info("Booking conflict: booking %s cannot move onto booking %s", booking_id, conflict.id)
        raise BookingConflictError(BOOKING_CONFLICT_MESSAGE)

    booking.start_time = start_time
    booking.end_time = end_time

    changed = save_without_overlap(db, update_booking, booking)
    logger.info("Booking %s moved to %s..%s", booking_id, start_time, end_time)

    return changed

def save_without_overlap(db: Session, save, booking: Booking):
    """Save a booking; a concurrent overlap rejected by the DB becomes a conflict."""
    try:
        return save(db, booking)
    except DBAPIError as exc:
        db.rollback()

        pgcode = getattr(exc.orig, "pgcode", None)

        if pgcode in OVERLAP_ERROR_CODES:
            # The service check passed but a concurrent request won: the race was caught by the DB.
            logger.warning("Concurrent booking overlap rejected by database (pgcode=%s)", pgcode)
            raise BookingConflictError(BOOKING_CONFLICT_MESSAGE) from exc

        raise

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
        raise BookingNotFoundError("Бронь не найдена")

    if booking.user_id != user_id:
        raise BookingAccessDeniedError("У вас нет доступа к этой брони")

    if booking.status == BookingStatus.CANCELED:
        raise BookingAlreadyCanceledError("Бронь уже отменена")

    return booking