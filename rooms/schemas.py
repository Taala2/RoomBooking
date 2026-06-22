from pydantic import BaseModel, ConfigDict, Field

class RoomRequest(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    capacity: int
    description: str | None

class RoomChangeRequest(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=255)
    capacity: int | None = None
    description: str | None = None

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