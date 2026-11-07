from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, column, func, literal_column, text
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bookings.bookings_schemas import BookingStatus
from core.database import Base


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        # Created by migration 0003: no overlapping active bookings per room.
        ExcludeConstraint(
            ("room_id", "="),
            (func.tstzrange(column("start_time"), column("end_time"), literal_column("'[)'")), "&&"),
            name="bookings_no_overlap",
            using="gist",
            where=text("status = 'ACTIVE'")
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="bookings")
    room: Mapped["Room"] = relationship(back_populates="bookings")