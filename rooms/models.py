from typing import List
from sqlalchemy import String, Text

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int]
    description: Mapped[str] = mapped_column(Text, nullable=True)

    bookings: Mapped[List["Booking"]] = relationship(back_populates="room")