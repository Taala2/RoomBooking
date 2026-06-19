from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import Current_admin, Current_user, create_access_token

from users.schemas import ChangeUserRoleRequest, ChangeUserRoleRespone, TokenResponse, UserAuthenticateRequest, UserCreateRequest, UserCreateResponse, UserResponse
from users.services import authenticate_user, change_user_by_id, create_user, get_user_by_register

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/auth/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreateRequest, db: Session = Depends(get_db)):
    existing_user = get_user_by_register(
        db=db,
        login=user.login,
        email=user.email
    )

    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Почта занят"
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Логин занят"
            )

    new_user_obj = create_user(
        db=db,
        login=user.login,
        email=user.email,
        password=user.password
    )

    return new_user_obj

@router.post("/auth/login", response_model=TokenResponse)
def login_user(auth_data: UserAuthenticateRequest, db: Session = Depends(get_db)):
    user = authenticate_user(
        db=db,
        login_or_email=auth_data.login_or_email,
        password=auth_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")

    token = create_access_token(user_id=str(user.id))

    return TokenResponse(access_token=token)

@router.get("/me", response_model=UserResponse)
def profile_user(user: Current_user):
    return UserResponse(
        id=user.id,
        login=user.login,
        email=user.email,
        role=user.role
    )

@router.patch("/{user_id}/role", response_model=ChangeUserRoleRespone)
def change_role(
    user_id: int,
    role: ChangeUserRoleRequest,
    current_user: Current_admin,
    db: Session = Depends(get_db)
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нельзя поменять свои права"
        )

    res = change_user_by_id(
        db=db,
        user_id=user_id,
        role=role.role
    )

    if res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    return ChangeUserRoleRespone(
        id=res.id,
        login=res.login,
        role=res.role
    )