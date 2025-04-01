import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.user import UserCreate
from backend.app.services.auth import register_user, authenticate_user, login_user
from backend.app.core.errors import DuplicateError, AuthError


# BDD-style test class for auth service
class TestAuthService:
    """
    Feature: User Authentication Service
    As the backend service
    I want to handle user registration and authentication
    So that users can securely access the system
    """
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, db: AsyncSession):
        """
        Scenario: Successful user registration
        Given a valid email, username, and password
        When I call the register_user service
        Then a new user should be created in the database
        And an authentication token should be returned
        """
        # Arrange
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="StrongP@ss123"
        )
        
        # Act
        token = await register_user(db, user_data)
        
        # Assert
        assert token is not None
        assert token.access_token is not None
        assert token.token_type == "bearer"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_user(self, db: AsyncSession):
        """
        Scenario: Registration with duplicate email
        Given I already have a user registered
        When I try to register another user with the same email
        Then the service should raise a DuplicateError
        """
        # Arrange
        user_data = UserCreate(
            email="duplicate@example.com",
            username="dupuser",
            password="StrongP@ss123"
        )
        
        # Register first user
        await register_user(db, user_data)
        
        # Act & Assert - Try to register again
        with pytest.raises(DuplicateError):
            await register_user(db, user_data)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db: AsyncSession):
        """
        Scenario: Successful user authentication
        Given a registered user
        When I call authenticate_user with correct credentials
        Then the user object should be returned
        """
        # Arrange - Create a user
        user_data = UserCreate(
            email="auth@example.com",
            username="authuser",
            password="StrongP@ss123"
        )
        await register_user(db, user_data)
        
        # Act
        user = await authenticate_user(db, "auth@example.com", "StrongP@ss123")
        
        # Assert
        assert user is not None
        assert user.email == "auth@example.com"
        assert user.username == "authuser"
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db: AsyncSession):
        """
        Scenario: Failed authentication with wrong password
        Given a registered user
        When I call authenticate_user with incorrect password
        Then None should be returned
        """
        # Arrange - Create a user
        user_data = UserCreate(
            email="wrong@example.com",
            username="wrongpass",
            password="StrongP@ss123"
        )
        await register_user(db, user_data)
        
        # Act
        user = await authenticate_user(db, "wrong@example.com", "WrongPassword")
        
        # Assert
        assert user is None
    
    @pytest.mark.asyncio
    async def test_login_user_success(self, db: AsyncSession):
        """
        Scenario: Successful user login
        Given a registered user
        When I call login_user with correct credentials
        Then an authentication token should be returned
        """
        # Arrange - Create a user
        user_data = UserCreate(
            email="login@example.com",
            username="loginuser",
            password="StrongP@ss123"
        )
        await register_user(db, user_data)
        
        # Act
        token = await login_user(db, "login@example.com", "StrongP@ss123")
        
        # Assert
        assert token is not None
        assert token.access_token is not None
        assert token.token_type == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_user_wrong_credentials(self, db: AsyncSession):
        """
        Scenario: Failed login with wrong credentials
        Given a registered user
        When I call login_user with incorrect credentials
        Then an AuthError should be raised
        """
        # Arrange - Create a user
        user_data = UserCreate(
            email="fail@example.com",
            username="failuser",
            password="StrongP@ss123"
        )
        await register_user(db, user_data)
        
        # Act & Assert
        with pytest.raises(AuthError):
            await login_user(db, "fail@example.com", "WrongPassword")