class UsernameAlreadyExistsError(Exception):
    pass

class EmailAlreadyExistsError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

class IncorrectPasswordError(Exception):
    pass

class AdminCannotDemoteSelfError(Exception):
    pass

class RoomNotFoundError(Exception):
    pass

class BookingConflictError(Exception):
    pass

class BookingNotFoundError(Exception):
    pass

class BookingAccessDeniedError(Exception):
    pass

class BookingAlreadyCanceledError(Exception):
    pass

class InvalidBookingTimeError(Exception):
    pass