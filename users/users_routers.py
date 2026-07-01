from fastapi import APIRouter, status

from core.dependencies import Current_admin, Current_session, Current_user
from core.security import create_access_token
from users.users_schemas import ChangeUserRoleRequest, ChangeUserRoleRespone, TokenResponse, UserAuthenticateRequest, UserCreateRequest, UserCreateResponse, UserResponse
from users.users_services import authenticate_user_service, change_user_role_service, create_user_service


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/auth/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def register_router(user: UserCreateRequest, db: Current_session):
    new_user = create_user_service(
        db=db,
        login=user.login,
        email=user.email,
        password=user.password
    )

    return new_user

@router.post("/auth/login", response_model=TokenResponse)
def login_router(auth_data: UserAuthenticateRequest, db: Current_session):
    user = authenticate_user_service(
        db=db,
        login_or_email=auth_data.login_or_email,
        password=auth_data.password)

    token = create_access_token(user_id=str(user.id))

    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserResponse)
def profile_router(user: Current_user):
    return user

@router.patch("/{user_id}/role", response_model=ChangeUserRoleRespone)
def change_role_router(
    user_id: int,
    role: ChangeUserRoleRequest,
    current_user: Current_admin,
    db: Current_session
):
    upd_user = change_user_role_service(
        db=db,
        current_user=current_user,
        user_id=user_id,
        role=role.role
    )

    return upd_user