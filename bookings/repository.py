from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from bookings.models import Booking
from bookings.schemas import BookingStatus


def get_booking_by_id(db: Session, booking_id: int):
    return db.get(Booking, booking_id)

def get_booking_by_user_id(db: Session, user_id: int):
    stmt = select(Booking).where(Booking.user_id==user_id)
    return db.execute(stmt).scalars().all()

def create_booking(db: Session, booking: Booking):
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def delete_booking(db: Session, booking: Booking):
    db.delete(booking)
    db.commit()
    return True

def update_booking(db: Session, booking: Booking):
    db.commit()
    db.refresh(booking)
    return booking

def get_conflict_booking(
        db: Session,
        room_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id=None
):
    stmt = select(Booking).where(
            Booking.room_id == room_id,
            Booking.status == BookingStatus.ACTIVE,
            Booking.start_time < end_time,
            Booking.end_time > start_time
        )

    if exclude_booking_id:
        stmt = stmt.where(Booking.id != exclude_booking_id)

    return db.execute(stmt).scalar_one_or_none()