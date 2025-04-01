import pytest
from fastapi import status
from fastapi.testclient import TestClient

# BDD-style test class for user registration
class TestUserRegistration:
    """
    Feature: User Registration
    As a new user
    I want to register with my email and password
    So that I can create an account on ZephyrPay
    """
    
    def test_register_user_success(self, client: TestClient):
        """
        Scenario: Successful user registration
        Given a valid email and password
        When I submit the registration form
        Then the system should create a new user account
        And return a 201 Created status
        And include a JWT token in the response
        """
        # Arrange
        user_data = {
            "email": "test@example.com",
            "password": "StrongP@ssw0rd",
            "username": "testuser"
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert "access_token" in response.json()
        assert "token_type" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    def test_register_user_duplicate_email(self, client: TestClient):
        """
        Scenario: Registration with duplicate email
        Given an email that is already registered
        When I submit the registration form
        Then the system should reject the registration
        And return a 400 Bad Request status
        """
        # Arrange
        user_data = {
            "email": "duplicate@example.com",
            "password": "StrongP@ssw0rd",
            "username": "duplicateuser"
        }
        
        # Register a user first
        client.post("/api/v1/auth/register", json=user_data)
        
        # Act - Try to register again with same email
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()
    
    def test_register_user_invalid_email(self, client: TestClient):
        """
        Scenario: Registration with invalid email format
        Given an invalid email format
        When I submit the registration form
        Then the system should reject the registration
        And return a 422 Unprocessable Entity status
        """
        # Arrange
        user_data = {
            "email": "invalid-email",
            "password": "StrongP@ssw0rd",
            "username": "invaliduser"
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_user_weak_password(self, client: TestClient):
        """
        Scenario: Registration with weak password
        Given a password that doesn't meet strength requirements
        When I submit the registration form
        Then the system should reject the registration
        And return a 422 Unprocessable Entity status
        """
        # Arrange
        user_data = {
            "email": "test2@example.com",
            "password": "weak",
            "username": "weakpassuser"
        }
        
        # Act
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """
    Feature: User Login
    As a registered user
    I want to log in with my credentials
    So that I can access the platform
    """

    def test_login_success(self, client: TestClient):
        """
        Scenario: Successful login
        Given I am a registered user
        When I submit valid credentials
        Then I should receive a JWT token
        And the response status should be 200 OK
        """
        # Arrange - Create a test user
        register_data = {
            "email": "logintest@example.com",
            "password": "StrongP@ssw0rd",
            "username": "loginuser"
        }
        client.post("/api/v1/auth/register", json=register_data)
        
        # Act - Attempt to login
        login_data = {
            "email": "logintest@example.com",
            "password": "StrongP@ssw0rd"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
        assert "token_type" in response.json()
        assert response.json()["token_type"] == "bearer"
        
    def test_login_invalid_credentials(self, client: TestClient):
        """
        Scenario: Login with invalid credentials
        Given I am a registered user
        When I submit invalid credentials
        Then I should receive an error
        And the response status should be 401 Unauthorized
        """
        # Arrange - Create a test user
        register_data = {
            "email": "badlogin@example.com",
            "password": "StrongP@ssw0rd",
            "username": "badloginuser"
        }
        client.post("/api/v1/auth/register", json=register_data)
        
        # Act - Attempt to login with wrong password
        login_data = {
            "email": "badlogin@example.com",
            "password": "WrongP@ssw0rd"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()
        
    def test_login_nonexistent_user(self, client: TestClient):
        """
        Scenario: Login with email that doesn't exist
        Given I attempt to login
        When I submit an email that doesn't exist
        Then I should receive an error
        And the response status should be 401 Unauthorized
        """
        # Act - Attempt to login with non-existent email
        login_data = {
            "email": "nonexistent@example.com",
            "password": "AnyP@ssw0rd"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()