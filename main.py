from fastapi import FastAPI

from core.database import Base, engine
from users.routers import router as users_router
from rooms.routers import router as rooms_router
from bookings.routers import router as bookings_router

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(users_router)
app.include_router(rooms_router)
app.include_router(bookings_router)