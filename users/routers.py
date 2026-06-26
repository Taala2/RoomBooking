from fastapi import APIRouter, HTTPException, status

from core.dependencies import Current_admin, Current_session, Current_user
from core.security import create_access_token
from users.schemas import ChangeUserRoleRequest, ChangeUserRoleRespone, TokenResponse, UserAuthenticateRequest, UserCreateRequest, UserCreateResponse, UserResponse
from users.services import authenticate_user_service, change_user_role_service, create_user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/auth/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def register_router(user: UserCreateRequest, db: Current_session):
    new_user = create_user_service(
        db=db,
        login=user.login,
        email=user.email,
        password=user.password
    )

    if new_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Логин или почта занят"
        )

    return new_user

@router.post("/auth/login", response_model=TokenResponse)
def login_router(auth_data: UserAuthenticateRequest, db: Current_session):
    user = authenticate_user_service(
        db=db,
        login_or_email=auth_data.login_or_email,
        password=auth_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Пользователь не найден"
        )

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

    if upd_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден или вы не можете поменять свою роль"
        )

    return upd_user