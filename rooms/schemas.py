from pydantic import BaseModel, Field


class RoomRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    capacity: int = Field(gt=0, le=100)
    description: str | None = Field(default=None, max_length=1000)

class RoomChangeRequest(BaseModel):
    room_id: int
    name: str | None = Field(default=None, min_length=3, max_length=100)
    capacity: int | None = Field(default=None, gt=0, le=100)
    description: str | None = Field(default=None, max_length=1000)

class RoomResponse(BaseModel):
    id: int
    name: str = Field(min_length=3, max_length=255)
    capacity: int
    description: str | None

    model_config = {
        "from_attributes": True
    }

class ListRoomResponse(BaseModel):
    items: list[RoomResponse]
    total: int
    limit: int
    offset: int