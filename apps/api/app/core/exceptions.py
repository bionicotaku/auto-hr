import logging
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    status_code = 400
    code = "app_error"

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class DomainValidationError(AppError):
    status_code = 422
    code = "domain_validation_error"


def _error_payload(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


def _humanize_validation_error(exc: RequestValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "Request validation failed."

    first_error = errors[0]
    raw_loc = first_error.get("loc", ())
    if isinstance(raw_loc, (list, tuple)):
        field_path = ".".join(str(part) for part in raw_loc if part != "body")
    else:
        field_path = str(raw_loc)

    message = str(first_error.get("msg", "Request validation failed."))
    if field_path:
        return f"{field_path}: {message}"
    return message


async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(exc.code, exc.message, exc.details),
    )


async def handle_request_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    serialized_errors = jsonable_encoder(exc.errors())
    return JSONResponse(
        status_code=422,
        content=_error_payload(
            "invalid_request",
            _humanize_validation_error(exc),
            {"errors": serialized_errors},
        ),
    )


async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content=_error_payload("internal_error", "Internal server error."),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
