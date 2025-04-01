import pytest
from fastapi import HTTPException, status

from backend.app.core.errors import (
    BaseZephyrPayError, 
    AuthError,
    NotFoundError,
    DuplicateError,
    ValidationError,
    PaymentError,
    raise_unauthorized,
    raise_forbidden,
    raise_not_found,
    raise_bad_request
)


class TestErrorClasses:
    """
    Feature: Custom Error Classes
    As a developer
    I want to have standardized error handling across the application
    So that API responses are consistent and informative
    """
    
    def test_base_error(self):
        """
        Scenario: Create a base error with default values
        Given no custom parameters
        When I create a BaseZephyrPayError
        Then it should have default message and status code
        And can be converted to a dictionary
        """
        error = BaseZephyrPayError()
        assert error.message == "An unexpected error occurred"
        assert error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert error.to_dict() == {"detail": "An unexpected error occurred"}
    
    def test_base_error_with_custom_message(self):
        """
        Scenario: Create a base error with custom message
        Given a custom error message
        When I create a BaseZephyrPayError
        Then it should have the custom message
        """
        error = BaseZephyrPayError(message="Custom error message")
        assert error.message == "Custom error message"
        assert error.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert error.to_dict() == {"detail": "Custom error message"}
    
    def test_auth_error(self):
        """
        Scenario: Create an authentication error
        Given default parameters
        When I create an AuthError
        Then it should have the correct message and status code
        """
        error = AuthError()
        assert error.message == "Authentication error"
        assert error.status_code == status.HTTP_401_UNAUTHORIZED
        assert error.to_dict() == {"detail": "Authentication error"}
    
    def test_not_found_error(self):
        """
        Scenario: Create a not found error
        Given default parameters
        When I create a NotFoundError
        Then it should have the correct message and status code
        """
        error = NotFoundError()
        assert error.message == "Resource not found"
        assert error.status_code == status.HTTP_404_NOT_FOUND
        assert error.to_dict() == {"detail": "Resource not found"}
    
    def test_duplicate_error(self):
        """
        Scenario: Create a duplicate resource error
        Given default parameters
        When I create a DuplicateError
        Then it should have the correct message and status code
        """
        error = DuplicateError()
        assert error.message == "Resource already exists"
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.to_dict() == {"detail": "Resource already exists"}
    
    def test_validation_error(self):
        """
        Scenario: Create a validation error with additional errors
        Given a validation error message and error details
        When I create a ValidationError
        Then it should include both the message and error details
        """
        errors = {"field1": "Invalid value", "field2": "Required"}
        error = ValidationError(message="Validation failed", errors=errors)
        assert error.message == "Validation failed"
        assert error.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert error.to_dict() == {
            "detail": "Validation failed",
            "errors": errors
        }
    
    def test_payment_error(self):
        """
        Scenario: Create a payment processing error
        Given a custom error message
        When I create a PaymentError
        Then it should have the correct message and status code
        """
        error = PaymentError(message="Payment declined")
        assert error.message == "Payment declined"
        assert error.status_code == status.HTTP_400_BAD_REQUEST
        assert error.to_dict() == {"detail": "Payment declined"}


class TestErrorHelpers:
    """
    Feature: Error Helper Functions
    As a developer
    I want to have utility functions to raise HTTP exceptions
    So that I can handle common error scenarios consistently
    """
    
    def test_raise_unauthorized(self):
        """
        Scenario: Raise an unauthorized error
        Given a custom error message
        When I call raise_unauthorized
        Then it should raise an HTTPException with the correct status and headers
        """
        with pytest.raises(HTTPException) as excinfo:
            raise_unauthorized("Custom unauthorized message")
        
        exception = excinfo.value
        assert exception.status_code == status.HTTP_401_UNAUTHORIZED
        assert exception.detail == "Custom unauthorized message"
        assert exception.headers == {"WWW-Authenticate": "Bearer"}
    
    def test_raise_forbidden(self):
        """
        Scenario: Raise a forbidden error
        Given a custom error message
        When I call raise_forbidden
        Then it should raise an HTTPException with the correct status
        """
        with pytest.raises(HTTPException) as excinfo:
            raise_forbidden("Custom forbidden message")
        
        exception = excinfo.value
        assert exception.status_code == status.HTTP_403_FORBIDDEN
        assert exception.detail == "Custom forbidden message"
    
    def test_raise_not_found(self):
        """
        Scenario: Raise a not found error
        Given a custom error message
        When I call raise_not_found
        Then it should raise an HTTPException with the correct status
        """
        with pytest.raises(HTTPException) as excinfo:
            raise_not_found("Custom not found message")
        
        exception = excinfo.value
        assert exception.status_code == status.HTTP_404_NOT_FOUND
        assert exception.detail == "Custom not found message"
    
    def test_raise_bad_request(self):
        """
        Scenario: Raise a bad request error
        Given a custom error message
        When I call raise_bad_request
        Then it should raise an HTTPException with the correct status
        """
        with pytest.raises(HTTPException) as excinfo:
            raise_bad_request("Custom bad request message")
        
        exception = excinfo.value
        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert exception.detail == "Custom bad request message"
