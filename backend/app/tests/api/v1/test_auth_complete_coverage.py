import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.errors import AuthError, DuplicateError
from backend.app.schemas.user import UserCreate, Token, LoginRequest


class TestAuthEndpointsCoverage:
    """
    Feature: Authentication Endpoints Complete Coverage
    As a developer
    I want to ensure complete test coverage of authentication endpoints
    So that the security-critical components are fully tested
    """
    
    @pytest.mark.asyncio
    async def test_register_service_error_path(self, client: TestClient, db: AsyncSession):
        """
        Scenario: Registration service throws DuplicateError
        Given the registration service raises a DuplicateError
        When I attempt to register
        Then the API should return a 400 Bad Request
        And properly convert the error to an AuthError
        This test specifically targets line 39 in auth.py
        """
        # Arrange - Prepare test data
        user_data = {
            "email": "coverage@example.com",
            "password": "StrongP@ssw0rd",
            "username": "coverageuser"
        }
        
        # Mock the register_user service to raise a DuplicateError
        # Specifically targeting the exception handler on line 39
        with patch('backend.app.api.v1.endpoints.auth.register_user', new_callable=AsyncMock) as mock_register:
            # Configure mock to raise DuplicateError which should trigger line 39
            mock_register.side_effect = DuplicateError("Email already exists")
            
            # Act - Make the request
            response = client.post("/api/v1/auth/register", json=user_data)
            
            # Assert - Check that the error is properly converted to HTTP 400
            # This verifies that the exception was caught by the handler on line 39
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "detail" in response.json()
            assert response.json()["detail"] == "Email already exists"
            
            # This also confirms the exception type that triggered line 39
            mock_register.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_service_direct_path(self, client: TestClient, db: AsyncSession):
        """
        Scenario: Direct login service path
        Given I want to test the login endpoint directly
        When I call login_user service with valid credentials
        Then the endpoint should return a valid token
        """
        # Mock the login_user service to return a token directly
        # This targets line 70 (direct return path)
        with patch('backend.app.api.v1.endpoints.auth.login_user', new_callable=AsyncMock) as mock_login:
            # Configure mock to return a token
            mock_token = Token(access_token="test_token", token_type="bearer")
            mock_login.return_value = mock_token
            
            # Act - Make the request
            login_data = {
                "email": "direct@example.com",
                "password": "StrongP@ssw0rd"
            }
            response = client.post("/api/v1/auth/login", json=login_data)
            
            # Assert - Check that token is returned
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["access_token"] == "test_token"
            assert response.json()["token_type"] == "bearer"
            
            # Verify the mock was called with correct parameters
            mock_login.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_request_validation(self, client: TestClient, db: AsyncSession):
        """
        Scenario: Request validation for login
        Given an invalid login request format
        When I submit the request
        Then the API should validate it and return 422
        """
        # Act - Test with invalid login format (missing required fields)
        response = client.post(
            "/api/v1/auth/login",
            json={
                # Missing password field
                "email": "test@example.com" 
            }
        )
        
        # Assert - Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
        # Validation error contains information about missing password
        assert any("password" in str(error).lower() for error in response.json()["detail"])

    @pytest.mark.asyncio
    async def test_register_request_validation(self, client: TestClient, db: AsyncSession):
        """
        Scenario: Request validation for registration
        Given an invalid registration request format
        When I submit the request
        Then the API should validate it and return 422
        """
        # Act - Test with invalid registration format (missing required fields)
        response = client.post(
            "/api/v1/auth/register",
            json={
                # Missing email and username
                "password": "StrongP@ssw0rd"
            }
        )
        
        # Assert - Should return validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
        # Validation contains information about missing email
        assert any("email" in str(error).lower() for error in response.json()["detail"])

    @pytest.mark.asyncio
    async def test_register_service_with_custom_error_handling(self, client: TestClient, db: AsyncSession):
        """
        Scenario: Custom error handling in register endpoint
        Given a specific type of auth error
        When raised by the registration service
        Then it should be properly handled and returned
        """
        # Arrange - Create test data
        user_data = {
            "email": "error@example.com",
            "password": "StrongP@ssw0rd",
            "username": "erroruser"
        }
        
        # Directly test line 39 with a specific setup for error handling
        with patch('backend.app.api.v1.endpoints.auth.register_user', new_callable=AsyncMock) as mock_register:
            # Setup the AuthError directly which tests a different branch
            mock_register.side_effect = AuthError(message="Auth service error", status_code=403)
            
            # Act - Make the request
            response = client.post("/api/v1/auth/register", json=user_data)
            
            # Assert - Check proper status code and error message
            assert response.status_code == 403
            assert "detail" in response.json()
            assert response.json()["detail"] == "Auth service error"
