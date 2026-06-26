from fastapi import APIRouter

from bookings.schemas import BookingRequest
from bookings.services import create_booking_service
from core.dependencies import Current_session, Current_user


router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/")
def booking_rooms(curent_user: Current_user, booking: BookingRequest, db: Current_session):
    new_booking = create_booking_service(
        db=db,
        user_id=curent_user.id,
        room_id=booking.room_id,
        start_time=booking.start_time,
        end_time=booking.end_time
    )

    return new_booking