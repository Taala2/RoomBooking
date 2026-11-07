from fastapi import APIRouter, Query, status

from core.dependencies import Current_admin, Current_session, Current_user, Page_offset
from core.security import create_access_token
from users.users_schemas import ChangeUserRoleRequest, ChangeUserRoleResponse, ListUserResponse, TokenResponse, UserAuthenticateRequest, UserCreateRequest, UserCreateResponse, UserResponse
from users.users_services import authenticate_user_service, change_user_role_service, count_users_service, create_user_service, get_users_service


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

@router.get("/list", response_model=ListUserResponse)
def list_users_router(
    _: Current_admin,
    db: Current_session,
    limit: int = Query(default=20, ge=1, le=100),
    offset: Page_offset = 0,
):
    return {
        "items": get_users_service(db, limit, offset),
        "total": count_users_service(db),
        "limit": limit,
        "offset": offset,
    }

@router.patch("/{user_id}/role", response_model=ChangeUserRoleResponse)
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