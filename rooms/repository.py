from sqlalchemy import func, select
from sqlalchemy.orm import Session

from rooms.models import Room


def get_room_by_id(db: Session, room_id: int):
    room = db.get(Room, room_id)
    return room

def create_room(db: Session, room: Room):
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

def update_room(db: Session, room: Room):
    db.commit()
    db.refresh(room)
    return room

def delete_room(db: Session, room: Room) -> None:
    db.delete(room)
    db.commit()

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