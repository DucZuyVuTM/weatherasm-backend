class AppError(Exception):
    """Base application error."""


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass


class UnauthorizedError(AppError):
    pass


class ExternalServiceError(AppError):
    pass
