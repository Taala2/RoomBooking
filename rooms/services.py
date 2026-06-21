from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from core.database import SessionLocal
from rooms.models import Room

def create_room(db: Session, name: str, capacity: int, description: str | None):
    room = Room(
        name=name,
        capacity=capacity,
        description=description
    )

    db.add(room)
    db.commit()
    db.refresh(room)
    return room

def get_room_by_id(db: Session, room_id: int):
    return db.get(Room, room_id)

def get_rooms(db: Session, limit: int, offset: int):
    stmt = (
        select(Room)
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())

def count_rooms(db: Session):
    stmt = select(func.count()).select_from(Room)

    return db.scalar(stmt) or 0

def delete_room_by_id(db: Session, room_id: int):
    room = db.get(Room, room_id)

    if room:
        db.delete(room)
        db.commit()

    return room

def update_room_by_id(
        db: Session,
        room_id: int,
        name: str | None,
        capacity: int | None,
        description: str | None
):
    room = db.get(Room, room_id)

    if room is None:
        return None

    if name: room.name = name
    if capacity: room.capacity = capacity
    if description: room.description = description

    db.commit()
    db.refresh(room)

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