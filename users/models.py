from typing import List
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bookings.models import Booking
from core.database import Base
from users.schemas import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)

    bookings: Mapped[List["Booking"]] = relationship(back_populates="user")