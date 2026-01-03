"""
Error Handler Middleware
Global exception handling and standardized error responses.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError


class FreshKeepException(Exception):
    """Base exception for FreshKeep application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR"
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class NotFoundError(FreshKeepException):
    """Resource not found error."""
    
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )


class UnauthorizedError(FreshKeepException):
    """Unauthorized access error."""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED"
        )


class ForbiddenError(FreshKeepException):
    """Forbidden access error."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN"
        )


class BadRequestError(FreshKeepException):
    """Bad request error."""
    
    def __init__(self, message: str = "Bad request"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST"
        )


class ExternalAPIError(FreshKeepException):
    """External API call failed."""
    
    def __init__(self, service: str, message: str = ""):
        super().__init__(
            message=f"{service} API error: {message}" if message else f"{service} API unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_API_ERROR"
        )


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: dict = None
) -> JSONResponse:
    """Create a standardized error response."""
    content = {
        "success": False,
        "error": {
            "code": error_code or "ERROR",
            "message": message,
        }
    }
    
    if details:
        content["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Set up global exception handlers for the FastAPI app."""
    
    @app.exception_handler(FreshKeepException)
    async def freshkeep_exception_handler(
        request: Request,
        exc: FreshKeepException
    ) -> JSONResponse:
        return create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"]
            })
        
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            error_code="VALIDATION_ERROR",
            details={"errors": errors}
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_exception_handler(
        request: Request,
        exc: ValidationError
    ) -> JSONResponse:
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()}
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        # Log the exception in production
        print(f"Unhandled exception: {exc}")
        
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred",
            error_code="INTERNAL_ERROR"
        )
