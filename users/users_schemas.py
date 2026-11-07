from enum import Enum
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

# bcrypt hashes only the first 72 bytes and bcrypt>=5 raises on longer input.
MAX_PASSWORD_BYTES = 72


def password_fits_bcrypt(value: str) -> str:
    if len(value.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise ValueError(f"Пароль слишком длинный: не больше {MAX_PASSWORD_BYTES} байт")

    return value


class UserRole(str, Enum):
    USER = 'user'
    ADMIN = 'admin'

class UserCreateRequest(BaseModel):
    # "@" is reserved for emails: login and email share one input on sign-in.
    login: str = Field(min_length=3, max_length=255, pattern=r"^[^@]+$")
    # Emails are stored lowercase so Foo@x.com and foo@x.com are one address.
    email: Annotated[EmailStr, Field(min_length=3, max_length=255), AfterValidator(str.lower)]
    password: Annotated[str, Field(min_length=8, max_length=255), AfterValidator(password_fits_bcrypt)]

class UserCreateResponse(BaseModel):
    id: int
    login: str = Field(max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)

    model_config = ConfigDict(
        from_attributes=True
    )

class UserAuthenticateRequest(BaseModel):
    login_or_email: str = Field(min_length=3, max_length=255)
    password: Annotated[str, Field(min_length=3, max_length=255), AfterValidator(password_fits_bcrypt)]

class UserResponse(BaseModel):
    id: int
    login: str = Field(min_length=3, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    role: UserRole

    model_config = ConfigDict(
        from_attributes=True
    )

class ListUserResponse(BaseModel):
    items: list[UserResponse]
    total: int
    limit: int
    offset: int

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChangeUserRoleResponse(BaseModel):
    id: int
    login: str = Field(min_length=3, max_length=255)
    role: UserRole

    model_config = ConfigDict(
        from_attributes=True
    )

class ChangeUserRoleRequest(BaseModel):
    role: UserRole