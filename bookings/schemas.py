from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class BookingStatus(str, Enum):
    ACTIVE = 'active'
    CANCELED = 'complated'

class BookingRequest(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime

class BookingResponse(BaseModel):
    id: int
    room_id: int
    start_time: datetime
    end_time: datetime

class BookingCancelRequest(BaseModel):
    booking_id: int

class BookinTimeChangeRequest(BaseModel):
    booking_id: int
    start_time: datetime
    end_time: datetime