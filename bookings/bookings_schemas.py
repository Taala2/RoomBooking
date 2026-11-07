from datetime import UTC, datetime
from enum import Enum
from typing import Annotated

from pydantic import AfterValidator, AwareDatetime, BaseModel, ConfigDict


class BookingStatus(str, Enum):
    ACTIVE = 'active'
    CANCELED = 'canceled'

# Time without an offset is rejected (422); any offset is normalized to UTC.
UtcDatetime = Annotated[AwareDatetime, AfterValidator(lambda value: value.astimezone(UTC))]

class BookingRequest(BaseModel):
    room_id: int
    start_time: UtcDatetime
    end_time: UtcDatetime

class BookingResponse(BaseModel):
    id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class BookingCancelRequest(BaseModel):
    booking_id: int

class BookingTimeChangeRequest(BaseModel):
    booking_id: int
    start_time: UtcDatetime
    end_time: UtcDatetime
