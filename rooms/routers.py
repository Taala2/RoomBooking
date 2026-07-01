from fastapi import APIRouter, Query

from core.dependencies import Current_admin, Current_session
from rooms.schemas import ListRoomResponse, RoomChangeRequest, RoomRequest, RoomResponse
from rooms.services import count_rooms_service, create_room_service, delete_room_service, get_room_service, get_rooms_service, update_room_service


router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("/create", response_model=RoomResponse)
def create_room_router(_: Current_admin, room: RoomRequest, db: Current_session):
    new_room = create_room_service(
        db=db,
        name=room.name,
        capacity=room.capacity,
        description=room.description
    )

    return new_room

@router.get("/list", response_model=ListRoomResponse)
def list_rooms_router(
    db: Current_session,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    rooms = get_rooms_service(
        db=db,
        limit=limit,
        offset=offset
    )

    total = count_rooms_service(db)

    return {
        "items": rooms,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

@router.get("/{room_id}", response_model=RoomResponse)
def get_room_router(room_id: int, db: Current_session):
    room = get_room_service(db, room_id)

    return room

@router.patch("/change/{room_id}", response_model=RoomResponse)
def change_room_router(
    _: Current_admin,
    room: RoomChangeRequest,
    db: Current_session
):
    upd_room = update_room_service(
        db=db,
        room_id=room.room_id,
        name=room.name,
        capacity=room.capacity,
        description=room.description
    )

    return upd_room

@router.delete("delete/{room_id}")
def delete_room(room_id: int, db: Current_session):
    del_room = delete_room_service(db, room_id)

    return del_room