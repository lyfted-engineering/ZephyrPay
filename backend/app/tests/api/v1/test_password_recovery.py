import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from backend.app.core.security import create_password_reset_token
from backend.app.models.user import User


class TestPasswordRecovery:
    """
    Feature: Password Recovery
    As a user
    I want to recover my account if I forget my password
    So that I can regain access securely
    """
    
    def test_request_password_reset(self, client: TestClient, db: AsyncSession):
        """
        Scenario: Request password reset
        Given I am a registered user
        When I request a password reset for my email
        Then the system should generate a reset token
        And return a success message
        """
        # Arrange - Create a test user
        test_user_data = {
            "email": "resettest@example.com",
            "password": "StrongP@ssw0rd",
            "username": "resetuser"
        }
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Act - Request password reset
        response = client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": "resettest@example.com"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        assert "reset_token" in response.json()  # For testing only, in production this would be emailed
    
    def test_request_password_reset_nonexistent_email(self, client: TestClient):
        """
        Scenario: Request password reset for non-existent email
        Given I am not a registered user
        When I request a password reset
        Then the system should still return a success message for security
        """
        # Act - Request password reset for non-existent email
        response = client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": "nonexistent@example.com"}
        )
        
        # Assert - Still return 200 for security reasons (don't leak user existence)
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
    
    def test_reset_password_with_valid_token(self, client: TestClient, db: AsyncSession):
        """
        Scenario: Reset password with valid token
        Given I have received a password reset token
        When I submit a new password with the token
        Then my password should be updated
        And I should receive a confirmation message
        """
        # Arrange - Create a test user
        test_user_data = {
            "email": "validtoken@example.com",
            "password": "StrongP@ssw0rd",
            "username": "validtokenuser"
        }
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Request reset token
        token_response = client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": "validtoken@example.com"}
        )
        reset_token = token_response.json()["reset_token"]
        
        # Act - Reset password with token
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "NewStrongP@ssw0rd"
            }
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        
        # Verify login with new password works
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "validtoken@example.com",
                "password": "NewStrongP@ssw0rd"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
    
    def test_reset_password_with_invalid_token(self, client: TestClient):
        """
        Scenario: Reset password with invalid token
        Given I have an invalid reset token
        When I try to reset my password
        Then the system should reject the request
        """
        # Act - Try to reset with invalid token
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid-token",
                "new_password": "NewStrongP@ssw0rd"
            }
        )
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()
    
    def test_reset_password_with_expired_token(self, client: TestClient, db: AsyncSession):
        """
        Scenario: Reset password with expired token
        Given I have an expired reset token
        When I try to reset my password
        Then the system should reject the request
        """
        # Arrange - Create a test user
        test_user_data = {
            "email": "expiredtoken@example.com",
            "password": "StrongP@ssw0rd",
            "username": "expiredtokenuser"
        }
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Generate an expired token directly (for testing)
        expired_token = create_password_reset_token(
            email="expiredtoken@example.com",
            expires_delta=timedelta(minutes=-10)  # Expired 10 minutes ago
        )
        
        # Act - Try to reset with expired token
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": expired_token,
                "new_password": "NewStrongP@ssw0rd"
            }
        )
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()
    
    def test_reset_password_weak_password(self, client: TestClient, db: AsyncSession):
        """
        Scenario: Reset password with weak password
        Given I have a valid reset token
        When I submit a weak password
        Then the system should reject the request
        """
        # Arrange - Create a test user
        test_user_data = {
            "email": "weakpassreset@example.com",
            "password": "StrongP@ssw0rd",
            "username": "weakpassuser"
        }
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Request reset token
        token_response = client.post(
            "/api/v1/auth/password-reset-request",
            json={"email": "weakpassreset@example.com"}
        )
        reset_token = token_response.json()["reset_token"]
        
        # Act - Try to reset with weak password
        response = client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": reset_token,
                "new_password": "weak"
            }
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
