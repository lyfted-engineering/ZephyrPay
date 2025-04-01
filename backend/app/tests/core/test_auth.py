import pytest
from fastapi import HTTPException, status
from jose import jwt
from unittest.mock import AsyncMock, patch

from backend.app.core.auth import get_current_user, get_current_active_user
from backend.app.models.user import User
from backend.app.core.config import settings


class TestAuth:
    """Tests for authentication functionality"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """
        Test successful retrieval of current user from token
        """
        # Arrange - Create a mock user and token
        mock_user = User(
            id=1,
            email="test@example.com",
            username="testuser",
            password_hash="hashedpassword",
            role="MEMBER",
            is_active=True
        )
        
        # Create a real token
        payload = {
            "sub": "1",
            "role": "MEMBER",
            "exp": 9999999999  # Far future
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        
        # Mock the database query to return our test user
        mock_db = AsyncMock()
        mock_execute = AsyncMock()
        mock_execute.return_value.scalars.return_value.first.return_value = mock_user
        mock_db.execute = mock_execute
        
        # Act
        user = await get_current_user(token=token, db=mock_db)
        
        # Assert
        assert user == mock_user
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """
        Test retrieving current user with invalid token
        """
        # Arrange
        mock_db = AsyncMock()
        
        # Act / Assert
        with pytest.raises(HTTPException) as exc:
            await get_current_user(token="invalid-token", db=mock_db)
        
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate credentials" in exc.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self):
        """
        Test retrieving current user when user doesn't exist
        """
        # Arrange - Create a valid token but no matching user
        payload = {
            "sub": "999",
            "role": "MEMBER",
            "exp": 9999999999
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        
        # Mock the database to return None for the user
        mock_db = AsyncMock()
        mock_execute = AsyncMock()
        mock_execute.return_value.scalars.return_value.first.return_value = None
        mock_db.execute = mock_execute
        
        # Act / Assert
        with pytest.raises(HTTPException) as exc:
            await get_current_user(token=token, db=mock_db)
        
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in exc.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self):
        """
        Test retrieving current user when user is inactive
        """
        # Arrange - Create a valid token but for an inactive user
        mock_user = User(
            id=1,
            email="inactive@example.com",
            username="inactiveuser",
            password_hash="hashedpassword",
            role="MEMBER",
            is_active=False
        )
        
        payload = {
            "sub": "1",
            "role": "MEMBER",
            "exp": 9999999999
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        
        # Mock the database to return an inactive user
        mock_db = AsyncMock()
        mock_execute = AsyncMock()
        mock_execute.return_value.scalars.return_value.first.return_value = mock_user
        mock_db.execute = mock_execute
        
        # Act / Assert
        with pytest.raises(HTTPException) as exc:
            await get_current_user(token=token, db=mock_db)
        
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Inactive user" in exc.value.detail
    
    @pytest.mark.asyncio
    async def test_get_current_active_user(self):
        """
        Test getting current active user
        """
        # Arrange - Create a mock active user
        mock_user = User(
            id=1,
            email="active@example.com",
            username="activeuser",
            password_hash="hashedpassword",
            role="MEMBER",
            is_active=True
        )
        
        # Act
        result = await get_current_active_user(current_user=mock_user)
        
        # Assert
        assert result == mock_user
    
    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self):
        """
        Test getting current active user with an inactive user
        """
        # Arrange - Create a mock inactive user
        mock_user = User(
            id=1,
            email="inactive@example.com",
            username="inactiveuser",
            password_hash="hashedpassword",
            role="MEMBER",
            is_active=False
        )
        
        # Act / Assert
        with pytest.raises(HTTPException) as exc:
            await get_current_active_user(current_user=mock_user)
        
        assert exc.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Inactive user" in exc.value.detail
