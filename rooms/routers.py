from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import Current_admin
from rooms.schemas import ListRoomResponse, RoomCreateReponse, RoomCreateRequest, RoomResponse
from rooms.services import count_rooms, create_room, get_room_by_id, get_rooms

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

@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    res = get_room_by_id(db, room_id)

    if res is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Комната не найдено")

    return RoomResponse(
        id=res.id,
        name=res.name,
        capacity=res.capacity,
        description=res.description
    )
