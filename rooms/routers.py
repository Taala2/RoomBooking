from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import Current_admin
from rooms.schemas import ListRoomResponse, RoomCreateReponse, RoomCreateRequest
from rooms.services import count_rooms, create_room, get_rooms
from users.schemas import UserRole


router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("/create", response_model=RoomCreateReponse)
def create_rooms(user: Current_admin, room: RoomCreateRequest, db: Session = Depends(get_db)):

    res = create_room(
        db=db,
        name=room.name,
        capacity=room.capacity,
        description=room.description
    )

    return RoomCreateReponse(
        id=res.id,
        name=res.name,
        capacity=res.capacity,
        description=res.description
    )

@router.get("/list", response_model=ListRoomResponse)
def list_rooms(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    rooms = get_rooms(
        db=db,
        limit=limit,
        offset=offset
    )

    total = count_rooms(db)

    return ListRoomResponse(
        items=rooms,
        total=total,
        limit=limit,
        offset=offset
    )
