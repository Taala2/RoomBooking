from sqlalchemy.orm import Session

from core.security import create_access_token, hash_password
from rooms.rooms_models import Room
from rooms.rooms_repositories import create_room
from users.users_models import User
from users.users_repositories import create_user
from users.users_schemas import UserRole

TEST_PASSWORD = "password123"


def make_user(db: Session, login: str = "user", role: UserRole = UserRole.USER) -> User:
    user = User(
        login=login,
        email=f"{login}@example.com",
        hashed_password=hash_password(TEST_PASSWORD),
        role=role
    )
    return create_user(db, user)


def make_room(db: Session, name: str = "Переговорная", capacity: int = 10) -> Room:
    return create_room(db, Room(name=name, capacity=capacity))


def auth_headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(str(user.id))}"}
