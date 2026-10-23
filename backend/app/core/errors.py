from typing import Any, Optional
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger("app.errors")


class AppException(Exception):
    """Base application exception with structured error data."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "ERROR",
        detail: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.detail = detail
        super().__init__(message)


class BadRequestError(AppException):
    def __init__(self, message: str = "Bad request", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            code="BAD_REQUEST",
            detail=detail,
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            detail=detail,
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "Access forbidden", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            detail=detail,
        )


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            detail=detail,
        )


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT",
            detail=detail,
        )


class CSRFValidationError(AppException):
    def __init__(self, message: str = "CSRF verification failed", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="CSRF_INVALID",
            detail=detail or "Missing or invalid X-CSRF-Token header",
        )


def raise_error(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    detail: Optional[Any] = None,
    code: Optional[str] = None,
) -> None:
    """Helper to raise modular application errors in a single line."""
    if code is None:
        if status_code == 400:
            code = "BAD_REQUEST"
        elif status_code == 401:
            code = "UNAUTHORIZED"
        elif status_code == 403:
            code = "FORBIDDEN"
        elif status_code == 404:
            code = "NOT_FOUND"
        elif status_code == 409:
            code = "CONFLICT"
        else:
            code = "ERROR"
    raise AppException(message=message, status_code=status_code, code=code, detail=detail)


def register_error_handlers(app: FastAPI) -> None:
    """Register uniform global exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "Application error: [%s] %s on %s %s",
            exc.code,
            exc.message,
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": exc.code,
                "detail": exc.message,
                "meta": exc.detail,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        logger.warning("HTTP error %d on %s %s: %s", exc.status_code, request.method, request.url.path, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": f"HTTP_{exc.status_code}",
                "detail": str(exc.detail),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("Validation error on %s %s: %s", request.method, request.url.path, exc.errors())
        first_error = exc.errors()[0] if exc.errors() else {}
        loc = " -> ".join(str(item) for item in first_error.get("loc", []))
        msg = first_error.get("msg", "Invalid input")
        formatted_message = f"{loc}: {msg}" if loc else msg

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "code": "VALIDATION_ERROR",
                "detail": formatted_message,
                "meta": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server exception on %s %s: %s", request.method, request.url.path, str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "code": "INTERNAL_SERVER_ERROR",
                "detail": "An internal error occurred. Please try again later.",
            },
        )
