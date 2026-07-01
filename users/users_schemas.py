from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    USER = 'user'
    ADMIN = 'admin'

class UserCreateRequest(BaseModel):
    login: str = Field(min_length=3, max_length=255)
    email: EmailStr = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=255)

class UserCreateResponse(BaseModel):
    id: int
    login: str = Field(max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)

    model_config = ConfigDict(
        from_attributes=True
    )

class UserAuthenticateRequest(BaseModel):
    login_or_email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=3, max_length=255)

class UserResponse(BaseModel):
    id: int
    login: str = Field(min_length=3, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    role: UserRole

    model_config = ConfigDict(
        from_attributes=True
    )

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChangeUserRoleRespone(BaseModel):
    id: int
    login: str = Field(min_length=3, max_length=255)
    role: UserRole

    model_config = ConfigDict(
        from_attributes=True
    )

class ChangeUserRoleRequest(BaseModel):
    role: UserRole