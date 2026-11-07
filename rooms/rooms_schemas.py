from pydantic import BaseModel, Field, field_validator


class RoomRequest(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    capacity: int = Field(gt=0, le=100)
    description: str | None = Field(default=None, max_length=1000)

class RoomChangeRequest(BaseModel):
    """Partial update: only sent fields change; description can be cleared with null."""
    name: str | None = Field(default=None, min_length=3, max_length=100)
    capacity: int | None = Field(default=None, gt=0, le=100)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("name", "capacity")
    @classmethod
    def required_field_is_not_null(cls, value):
        if value is None:
            raise ValueError("Поле не может быть пустым")

        return value

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