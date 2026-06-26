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