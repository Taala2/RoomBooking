from pydantic import BaseModel, Field


class RoomCreateReponse(BaseModel):
    id: int
    name: str = Field(min_length=3, max_length=255)
    capacity: int
    description: str | None

class RoomCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    capacity: int
    description: str | None

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