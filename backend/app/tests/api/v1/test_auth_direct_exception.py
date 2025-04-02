import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.errors import DuplicateError, AuthError
from backend.app.schemas.user import UserCreate


class TestDirectExceptionHandling:
    """
    Feature: Direct Exception Handler Testing
    As a developer
    I want to ensure the exact exception handling paths are tested
    So that we achieve 100% test coverage of security-critical components
    """
    
    def test_duplicate_error_exact_line_coverage(self, client: TestClient):
        """
        Scenario: Exact coverage of exception handler at line 39
        Given a request to register a user
        When the register_user service raises a DuplicateError
        Then the exception handler at line 39 should be triggered
        And convert the error to an AuthError with status 400
        """
        # Arrange - Setup test data
        user_data = {
            "email": "duplicate_line39@example.com",
            "password": "StrongP@ssw0rd",
            "username": "line39user"
        }
        
        # We'll directly patch the specific function that would raise the error
        # This ensures line 39 is hit in the except DuplicateError block
        with patch('backend.app.services.auth.register_user', 
                  side_effect=DuplicateError("Exact line 39 test")):
            # Act - Make request that will trigger the exception handler
            response = client.post("/api/v1/auth/register", json=user_data)
            
            # Assert - Verify the correct error response
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "detail" in response.json()
            assert response.json()["detail"] == "Exact line 39 test"
            
            # This ensures the DuplicateError was raised and caught at line 39
