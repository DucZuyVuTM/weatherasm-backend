from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import NotFoundError, ConflictError, UnauthorizedError, ExternalServiceError


def register_exception_handlers(app):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError):
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(ExternalServiceError)
    async def external_service_handler(request: Request, exc: ExternalServiceError):
        return JSONResponse(status_code=502, content={"detail": str(exc)})
