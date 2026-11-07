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

    # passive_deletes: the database removes bookings (ON DELETE CASCADE), not the ORM.
    bookings: Mapped[List["Booking"]] = relationship(back_populates="room", passive_deletes=True)