from sqlalchemy import func, select
from sqlalchemy.orm import Session

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

# db = SessionLocal()
# try:
#     room = create_room(db, name="Games", capacity=5, description="Thissidadgselmsefl")
#     rooms = get_rooms(db, 100, 0)
# finally:
#     db.close()

# for room in rooms:
#     print(
#         room.id,
#         room.name,
#         room.capacity,
#         room.description
#     )

# print(room.description)