import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.handlers import register_exception_handlers
from users.users_routers import router as users_router
from rooms.rooms_routers import router as rooms_router
from bookings.bookings_routers import router as bookings_router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

app = FastAPI()

if settings.cors_origins:
    # The frontend sends the JWT in the Authorization header, cookies are not used.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"]
    )

register_exception_handlers(app)

app.include_router(users_router)
app.include_router(rooms_router)
app.include_router(bookings_router)