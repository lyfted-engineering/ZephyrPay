import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.endpoints.auth import user_register, user_login
from backend.app.core.errors import DuplicateError, AuthError
from backend.app.schemas.user import UserCreate, LoginRequest, Token


class TestAuthDirectInstrumentation:
    """
    Feature: Authentication Controller Direct Instrumentation
    
    These tests are designed to directly target specific lines in the auth.py file 
    that coverage reports are showing as not covered. This approach allows us to 
    ensure we're hitting every line of code, including error handling paths.
    """
    
    @pytest.mark.asyncio
    async def test_register_exception_handler_direct_instrumentation(self, db: AsyncSession):
        """Test lines 39-42 directly by mocking register_user to raise DuplicateError"""
        # Create test data
        user_data = UserCreate(
            email="test@example.com",
            password="StrongP@ssw0rd", 
            username="directtest"
        )
        
        # Mock the register_user function to raise DuplicateError
        # This directly tests the exception handler in lines 39-42
        with patch("backend.app.api.v1.endpoints.auth.register_user", 
                  AsyncMock(side_effect=DuplicateError(message="Email already exists"))) as mock_register:
            
            # We expect this to raise AuthError which we'll catch
            with pytest.raises(AuthError) as exc_info:
                await user_register(user_data=user_data, db=db)
            
            # Verify the exception was raised properly
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Email already exists" in str(exc_info.value)
            
            # Verify our mock was called
            mock_register.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_exception_line_39_specific(self):
        """Target line 39 specifically with direct instrumentation"""
        # Create test data
        user_data = UserCreate(
            email="line39@example.com",
            password="StrongP@ssw0rd", 
            username="line39test"
        )
        
        # Create a mock db
        mock_db = AsyncMock()
        
        # Mock the specific try section to make sure we handle line 39
        # This approach ensures coverage of line 39 specifically
        with patch("backend.app.api.v1.endpoints.auth.register_user",
                  new=AsyncMock()) as mock_register:
            
            # Set up the mock to return a value on the first call 
            # and raise an exception on the second call to ensure both paths are tested
            mock_register.side_effect = [
                Token(access_token="test_token", token_type="bearer"),
                DuplicateError(message="Line 39 test")
            ]
            
            # First call, normal return
            result = await user_register(user_data=user_data, db=mock_db)
            assert result.access_token == "test_token"
            
            # Second call to trigger the exception handling
            with pytest.raises(AuthError) as exc_info:
                await user_register(user_data=user_data, db=mock_db)
            
            # Verify we hit the line 39 exception handler
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Line 39 test" in str(exc_info.value)
            
            # Verify our mock was called twice
            assert mock_register.call_count == 2
    
    @pytest.mark.asyncio
    async def test_login_direct_token_return(self, db: AsyncSession):
        """Test line 70 directly by mocking login_user to return a token"""
        # Create test data
        login_data = LoginRequest(
            email="test@example.com",
            password="StrongP@ssw0rd"
        )
        
        # Create a mock token
        mock_token = Token(
            access_token="mocked_token",
            token_type="bearer"
        )
        
        # Mock the login_user function to return our token
        # This directly tests line 70
        with patch("backend.app.api.v1.endpoints.auth.login_user", 
                  AsyncMock(return_value=mock_token)) as mock_login:
            
            # Call the login endpoint
            result = await user_login(login_data=login_data, db=db)
            
            # Verify our mock was called
            mock_login.assert_called_once_with(db, login_data.email, login_data.password)
            
            # Verify we got back our token
            assert result == mock_token
            assert result.access_token == "mocked_token"
            assert result.token_type == "bearer"
