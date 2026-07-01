from fastapi import Request, status
from fastapi.responses import JSONResponse

from core.exceptions import AdminCannotDemoteSelfError, BookingAccessDeniedError, BookingAlreadyCanceledError, BookingConflictError, BookingNotFoundError, EmailAlreadyExistsError, IncorrectPasswordError, InvalidBookingTimeError, RoomNotFoundError, UserNotFoundError, UsernameAlreadyExistsError

def username_already_exists_handler(
    _: Request,
    exc: UsernameAlreadyExistsError
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Пользователь с таким именем уже зарегистрирован"}
    )

def email_already_exists_handler(
    _: Request,
    exc: EmailAlreadyExistsError
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "Пользователь с таким email уже зарегистрирован"}
    )

def user_not_found_handler(
        _: Request,
        exc: UserNotFoundError
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Неверный логин или пароль"}
    )

def incorrect_password_handler(
      _: Request,
      exc: IncorrectPasswordError
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Неверный логин или пароль"}
    )

def admin_cannot_demote_self_handler(
      _: Request,
      exc: AdminCannotDemoteSelfError
):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc)}
    )

def room_not_found_handler(
        _: Request,
        exc: RoomNotFoundError
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )

def booking_conflict_handler(
        _: Request,
        exc: BookingConflictError
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)}
    )

def booking_not_found_handler(
        _: Request,
        exc: BookingNotFoundError
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )

def booking_access_denied_handler(
        _: Request,
        exc: BookingAccessDeniedError
):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "нет доступа"}
    )

def booking_already_canceled_handler(
        _: Request,
        exc: BookingAlreadyCanceledError
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)}
    )

def invalid_booking_time_handler(
        _: Request,
        exc: InvalidBookingTimeError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

def register_exception_handlers(app):
    app.add_exception_handler(
        UsernameAlreadyExistsError,
        username_already_exists_handler
    )
    app.add_exception_handler(
        EmailAlreadyExistsError,
        email_already_exists_handler
    )
    app.add_exception_handler(
        UserNotFoundError,
        user_not_found_handler
    )
    app.add_exception_handler(
        IncorrectPasswordError,
        incorrect_password_handler
    )
    app.add_exception_handler(
        AdminCannotDemoteSelfError,
        admin_cannot_demote_self_handler
    )
    app.add_exception_handler(
        RoomNotFoundError,
        room_not_found_handler
    )
    app.add_exception_handler(
        BookingConflictError,
        booking_conflict_handler
    )
    app.add_exception_handler(
        BookingNotFoundError,
        booking_not_found_handler
    )
    app.add_exception_handler(
        BookingAccessDeniedError,
        booking_access_denied_handler
    )
    app.add_exception_handler(
        BookingAlreadyCanceledError,
        booking_already_canceled_handler
    )
    app.add_exception_handler(
        InvalidBookingTimeError,
        invalid_booking_time_handler
    )