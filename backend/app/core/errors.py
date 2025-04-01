from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class BaseZephyrPayError(Exception):
    """Base exception class for ZephyrPay"""
    def __init__(
        self, 
        message: str = "An unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        return {"detail": self.message}


class AuthError(BaseZephyrPayError):
    """Authentication related errors"""
    def __init__(
        self, 
        message: str = "Authentication error", 
        status_code: int = status.HTTP_401_UNAUTHORIZED
    ):
        super().__init__(message, status_code)


class NotFoundError(BaseZephyrPayError):
    """Resource not found errors"""
    def __init__(
        self, 
        message: str = "Resource not found", 
        status_code: int = status.HTTP_404_NOT_FOUND
    ):
        super().__init__(message, status_code)


class DuplicateError(BaseZephyrPayError):
    """Duplicate resource errors"""
    def __init__(
        self, 
        message: str = "Resource already exists", 
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        super().__init__(message, status_code)


class ValidationError(BaseZephyrPayError):
    """Input validation errors"""
    def __init__(
        self, 
        message: str = "Validation error", 
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors: Optional[Dict[str, Any]] = None
    ):
        self.errors = errors
        super().__init__(message, status_code)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary with validation details"""
        result = super().to_dict()
        if self.errors:
            result["errors"] = self.errors
        return result


class PaymentError(BaseZephyrPayError):
    """Payment processing errors"""
    def __init__(
        self, 
        message: str = "Payment processing error", 
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        super().__init__(message, status_code)


# Convenience functions for raising HTTP exceptions
def raise_unauthorized(detail: str = "Not authenticated") -> None:
    """Raise 401 Unauthorized error"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )


def raise_forbidden(detail: str = "Not enough permissions") -> None:
    """Raise 403 Forbidden error"""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )


def raise_not_found(detail: str = "Item not found") -> None:
    """Raise 404 Not Found error"""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )


def raise_bad_request(detail: str = "Bad request") -> None:
    """Raise 400 Bad Request error"""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )