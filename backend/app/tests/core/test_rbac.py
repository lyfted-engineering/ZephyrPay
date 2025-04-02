import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, AsyncMock, patch, call

from backend.app.core.rbac import rbac_required, is_admin, is_operator_or_admin
from backend.app.core.errors import PermissionError
from backend.app.schemas.role import RoleEnum


class TestRBAC:
    """Unit tests for RBAC functionality"""
    
    def test_is_admin_with_admin_user(self):
        """
        Scenario: Admin user passes admin check
        Given I have an admin user
        When I check if they are an admin
        Then the function should return the user
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = "ADMIN"
        
        # Act/Assert
        assert is_admin(mock_user) == mock_user
    
    def test_is_admin_with_non_admin_user(self):
        """
        Scenario: Non-admin user fails admin check
        Given I have a non-admin user
        When I check if they are an admin
        Then the function should raise a PermissionError
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = "MEMBER"
        
        # Act/Assert
        with pytest.raises(PermissionError) as exc_info:
            is_admin(mock_user)
        
        assert "Admin role required" in str(exc_info.value)
    
    def test_is_operator_or_admin_with_admin(self):
        """
        Scenario: Admin user passes operator or admin check
        Given I have an admin user
        When I check if they are an operator or admin
        Then the function should return the user
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = "ADMIN"
        
        # Act/Assert
        assert is_operator_or_admin(mock_user) == mock_user
    
    def test_is_operator_or_admin_with_operator(self):
        """
        Scenario: Operator user passes operator or admin check
        Given I have an operator user
        When I check if they are an operator or admin
        Then the function should return the user
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = "OPERATOR"
        
        # Act/Assert
        assert is_operator_or_admin(mock_user) == mock_user
    
    def test_is_operator_or_admin_with_member(self):
        """
        Scenario: Member user fails operator or admin check
        Given I have a member user
        When I check if they are an operator or admin
        Then the function should raise a PermissionError
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = "MEMBER"
        
        # Act/Assert
        with pytest.raises(PermissionError) as exc_info:
            is_operator_or_admin(mock_user)
        
        assert "Operator or Admin role required" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rbac_required_decorator_with_allowed_role(self):
        """
        Scenario: User with allowed role accesses decorated function
        Given I have a user with an allowed role
        When I call a function decorated with rbac_required
        Then the function should be called
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = RoleEnum.ADMIN
        
        @rbac_required([RoleEnum.ADMIN])
        async def test_function(current_user):
            return "Function called"
        
        # Act
        result = await test_function(current_user=mock_user)
        
        # Assert
        assert result == "Function called"
    
    @pytest.mark.asyncio
    async def test_rbac_required_decorator_with_disallowed_role(self):
        """
        Scenario: User with disallowed role attempts to access decorated function
        Given I have a user with a disallowed role
        When I call a function decorated with rbac_required
        Then a PermissionError should be raised
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = RoleEnum.MEMBER
        
        @rbac_required([RoleEnum.ADMIN])
        async def test_function(current_user):
            return "Function called"
        
        # Act/Assert
        with pytest.raises(PermissionError) as exc_info:
            await test_function(current_user=mock_user)
        
        assert "not authorized" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rbac_required_decorator_with_multiple_allowed_roles(self):
        """
        Scenario: Users with different allowed roles access decorated function
        Given I have users with different allowed roles
        When I call a function decorated with rbac_required
        Then the function should be called for all allowed roles
        """
        # Arrange
        admin_user = MagicMock()
        admin_user.role = RoleEnum.ADMIN
        
        operator_user = MagicMock()
        operator_user.role = RoleEnum.OPERATOR
        
        @rbac_required([RoleEnum.ADMIN, RoleEnum.OPERATOR])
        async def test_function(current_user):
            return f"Function called by {current_user.role}"
        
        # Act
        admin_result = await test_function(current_user=admin_user)
        operator_result = await test_function(current_user=operator_user)
        
        # Assert
        assert admin_result == f"Function called by {RoleEnum.ADMIN}"
        assert operator_result == f"Function called by {RoleEnum.OPERATOR}"
    
    @pytest.mark.asyncio
    async def test_rbac_required_with_empty_allowed_roles(self):
        """
        Scenario: RBAC decorator with empty allowed roles
        Given I have a function with RBAC decorator with empty allowed roles list
        When I call the function with any user
        Then a PermissionError should be raised
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = RoleEnum.ADMIN
        
        @rbac_required([])  # Empty allowed roles list
        async def test_function(current_user):
            return "Function called"
        
        # Act/Assert
        with pytest.raises(PermissionError) as exc_info:
            await test_function(current_user=mock_user)
        
        assert "not authorized" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rbac_required_with_nonexistent_role(self):
        """
        Scenario: User with role not in enum tries to access decorated function
        Given I have a user with a role not defined in RoleEnum
        When I call a function decorated with rbac_required
        Then a PermissionError should be raised
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = "NONEXISTENT_ROLE"  # Role not in RoleEnum
        
        @rbac_required([RoleEnum.ADMIN, RoleEnum.OPERATOR])
        async def test_function(current_user):
            return "Function called"
        
        # Act/Assert
        with pytest.raises(PermissionError) as exc_info:
            await test_function(current_user=mock_user)
        
        assert "not authorized" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rbac_required_preserves_function_signature(self):
        """
        Scenario: RBAC decorator preserves function signature
        Given I have a function with complex signature
        When I decorate it with rbac_required
        Then the decorated function should maintain the original signature
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = RoleEnum.ADMIN
        
        @rbac_required([RoleEnum.ADMIN])
        async def complex_function(arg1, arg2, current_user, kwarg1=None):
            return f"Function called with {arg1}, {arg2}, {kwarg1}"
        
        # Act
        result = await complex_function("value1", "value2", current_user=mock_user, kwarg1="kwvalue")
        
        # Assert
        assert result == "Function called with value1, value2, kwvalue"
    
    @pytest.mark.asyncio
    async def test_rbac_required_with_case_sensitivity(self):
        """
        Scenario: RBAC checks are case sensitive
        Given I have a user with role in different case than allowed roles
        When I call a function decorated with rbac_required
        Then a PermissionError should be raised
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = "admin"  # Lowercase instead of ADMIN
        
        @rbac_required([RoleEnum.ADMIN])  # ADMIN is uppercase in enum
        async def test_function(current_user):
            return "Function called"
        
        # Act/Assert
        with pytest.raises(PermissionError) as exc_info:
            await test_function(current_user=mock_user)
        
        assert "not authorized" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rbac_required_with_none_role(self):
        """
        Scenario: User with None role tries to access decorated function
        Given I have a user with None as their role
        When I call a function decorated with rbac_required
        Then a PermissionError should be raised
        """
        # Arrange
        mock_user = MagicMock()
        mock_user.role = None
        
        @rbac_required([RoleEnum.ADMIN, RoleEnum.OPERATOR])
        async def test_function(current_user):
            return "Function called"
        
        # Act/Assert
        with pytest.raises(PermissionError) as exc_info:
            await test_function(current_user=mock_user)
        
        assert "not authorized" in str(exc_info.value)
