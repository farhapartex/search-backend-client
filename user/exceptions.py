class UserException(Exception):
    pass


class UserAlreadyExistsException(UserException):
    pass


class UserNotFoundException(UserException):
    pass


class InvalidCredentialsException(UserException):
    pass


class AccountNotActiveException(UserException):
    pass


class ActivationException(Exception):
    pass


class InvalidActivationCodeException(ActivationException):
    pass


class ActivationCodeExpiredException(ActivationException):
    pass
