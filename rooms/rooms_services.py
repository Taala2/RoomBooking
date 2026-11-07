from datetime import UTC, datetime

from sqlalchemy.orm import Session

from bookings.bookings_repositories import has_upcoming_bookings
from core.exceptions import RoomHasActiveBookingsError, RoomNotFoundError
from rooms.rooms_models import Room
from rooms.rooms_repositories import count_rooms, create_room, delete_room, get_room_by_id, get_rooms, update_room

ROOM_NOT_FOUND_MESSAGE = "Комната не найдена"


def create_room_service(db: Session, name: str, capacity: int, description: str | None):
    return create_room(
        db=db,
        room=Room(
            name=name,
            capacity=capacity,
            description=description
        )
    )

def get_room_service(db: Session, room_id: int):
    room = get_room_by_id(db, room_id)

    if not room:
        raise RoomNotFoundError(ROOM_NOT_FOUND_MESSAGE)

    return room

def get_rooms_service(db: Session, limit: int, offset: int):
    return get_rooms(db, limit, offset)

def count_rooms_service(db: Session):
    return count_rooms(db)

def delete_room_service(db: Session, room_id: int) -> None:
    room = get_room_service(db, room_id)

    if has_upcoming_bookings(db, room_id, datetime.now(UTC)):
        raise RoomHasActiveBookingsError("Нельзя удалить комнату с предстоящими бронями")

    # Past and canceled bookings are removed by ON DELETE CASCADE.
    delete_room(db, room)

def update_room_service(db: Session, room_id: int, changes: dict):
    room = get_room_service(db, room_id)

    for field, value in changes.items():
        setattr(room, field, value)

    return update_room(db, room)