from fastapi import APIRouter

from bookings.schemas import BookinTimeChangeRequest, BookingCancelRequest, BookingRequest, BookingResponse
from bookings.services import cancel_booking_service, change_booking_time_service, create_booking_service, get_my_booking_service
from core.dependencies import Current_session, Current_user


router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", response_model=BookingResponse)
def booking_rooms_router(
    current_user: Current_user,
    booking: BookingRequest,
    db: Current_session
):
    new_booking = create_booking_service(
        db=db,
        user_id=current_user.id,
        room_id=booking.room_id,
        start_time=booking.start_time,
        end_time=booking.end_time
    )

    return new_booking

@router.get("/")
def get_bookings_router(current_user: Current_user, db: Current_session):
    return get_my_booking_service(db, current_user.id)

@router.post("/cancel")
def cancel_booking_router(
    current_user: Current_user,
    booking_id: BookingCancelRequest,
    db:Current_session
):
    booking = cancel_booking_service(db, current_user.id, booking_id.booking_id)

    return booking

@router.post("/change")
def change_booking_router(
    current_user: Current_user,
    booking_change: BookinTimeChangeRequest,
    db: Current_session
):
    booking = change_booking_time_service(
        db=db,
        user_id=current_user.id,
        booking_id=booking_change.booking_id,
        start_time=booking_change.start_time,
        end_time=booking_change.end_time
    )

    return booking