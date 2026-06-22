from sqlalchemy import func, select
from sqlalchemy.orm import Session

from rooms.models import Room
from rooms.repository import count_rooms, create_room, delete_room, get_room_by_id, get_rooms, update_room

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
    return get_room_by_id(db, room_id)

def get_rooms_service(db: Session, limit: int, offset: int):
    return get_rooms(db, limit, offset)

def count_rooms_service(db: Session):
    return count_rooms(db)

def delete_room_service(db: Session, room_id: int):
    room = get_room_by_id(db, room_id)

    if room is None:
        return None

    delete_room(db, room)

    return True

def update_room_service(
        db: Session,
        room_id: int,
        name: str | None,
        capacity: int | None,
        description: str | None
):
    room = get_room_by_id(db, room_id)

    if room is None:
        return None

    if name: room.name = name
    if capacity: room.capacity = capacity
    if description: room.description = description

    update_room(db, room)

    return room


# db = SessionLocal()
# try:
#     room = delete_room_by_id(db, 3)
# finally:
#     db.close()

# if room is None:
#     print("нет")
# else:
#     print(room.name)