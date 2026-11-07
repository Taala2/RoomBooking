from fastapi import APIRouter, Query, status

from bookings.bookings_schemas import BusySlotResponse, UtcDatetime
from bookings.bookings_services import get_room_busy_slots_service
from core.dependencies import Current_admin, Current_session, Current_user, Page_offset
from rooms.rooms_schemas import ListRoomResponse, RoomChangeRequest, RoomRequest, RoomResponse
from rooms.rooms_services import count_rooms_service, create_room_service, delete_room_service, get_room_service, get_rooms_service, update_room_service


router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("/create", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
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
    offset: Page_offset = 0,
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

@router.get("/{room_id}/bookings", response_model=list[BusySlotResponse])
def room_busy_slots_router(
    room_id: int,
    start: UtcDatetime,
    end: UtcDatetime,
    _: Current_user,
    db: Current_session
):
    return get_room_busy_slots_service(db, room_id, start, end)

@router.patch("/change/{room_id}", response_model=RoomResponse)
def change_room_router(
    room_id: int,
    _: Current_admin,
    room: RoomChangeRequest,
    db: Current_session
):
    upd_room = update_room_service(
        db=db,
        room_id=room_id,
        changes=room.model_dump(exclude_unset=True)
    )

    return upd_room

@router.delete("/delete/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room_router(room_id: int, _: Current_admin, db: Current_session):
    delete_room_service(db, room_id)