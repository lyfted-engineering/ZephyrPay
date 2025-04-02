import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.core.security import create_access_token
from backend.app.schemas.role import RoleEnum
from backend.app.db.session import get_db
from backend.app.main import app

@pytest.fixture
async def admin_user_fixture(db: AsyncSession):
    """Create an admin user in the database for targeted tests"""
    admin = User(
        email="admin_target@example.com",
        username="admin_target",
        password_hash="hashed_password_for_testing",
        role=RoleEnum.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    # Return ID to avoid session issues
    return admin.id

@pytest.fixture
async def operator_user_fixture(db: AsyncSession):
    """Create an operator user in the database for targeted tests"""
    operator = User(
        email="operator_target@example.com",
        username="operator_target",
        password_hash="hashed_password_for_testing",
        role=RoleEnum.OPERATOR,
        is_active=True,
        is_verified=True
    )
    db.add(operator)
    await db.commit()
    await db.refresh(operator)
    
    # Create token with the operator role
    token = create_access_token(subject=operator.id, role=operator.role)
    
    # Return both ID and token to avoid session issues
    return {"id": operator.id, "token": token}

@pytest.fixture
async def member_user_fixture(db: AsyncSession):
    """Create a member user in the database for targeted tests"""
    member = User(
        email="member_target@example.com",
        username="member_target",
        password_hash="hashed_password_for_testing",
        role=RoleEnum.MEMBER,
        is_active=True,
        is_verified=True
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    # Create token with the member role
    token = create_access_token(subject=member.id, role=member.role)
    
    # Return both ID and token to avoid session issues
    return {"id": member.id, "token": token}

def test_operator_cannot_view_admin_role(client: TestClient, admin_user_fixture, operator_user_fixture):
    """
    Scenario: Operator tries to view an admin's role (targeted for line 51-52)
    Given I have an operator user and an admin user
    When the operator tries to access the admin's role
    Then a permission error should be raised
    And the response should be 403 Forbidden
    """
    # Arrange
    operator_headers = {"Authorization": f"Bearer {operator_user_fixture['token']}"}
    
    # Create the GET request with the operator trying to get an admin's role
    response = client.get(
        f"/api/v1/roles/roles/users/{admin_user_fixture}", 
        headers=operator_headers
    )
    
    # Assert the specific error message from line 51
    assert response.status_code == status.HTTP_403_FORBIDDEN
    error_detail = response.json().get("detail", "")
    assert "Insufficient permissions to view admin roles" in error_detail

@pytest.mark.asyncio
async def test_direct_line_51_52_coverage(client: TestClient, operator_user_fixture, db: AsyncSession):
    """
    Scenario: Direct test for lines 51-52 in roles.py
    Given an operator user tries to view an admin's role
    When the specific code path is executed
    Then the permission error should be triggered from lines 51-52
    """
    from unittest.mock import patch, MagicMock
    from backend.app.core.errors import PermissionError
    from backend.app.schemas.role import RoleRead
    from backend.app.api.v1.endpoints.roles import read_user_role
    
    # Create a mock user with operator role
    mock_current_user = MagicMock()
    mock_current_user.role = "OPERATOR"
    mock_current_user.id = operator_user_fixture['id']
    
    # Create a mock admin user that will be returned by get_user_role
    mock_admin_role = RoleRead(role="ADMIN", user_id=999)
    
    # Mock the get_user_role service function to return an admin role
    with patch('backend.app.api.v1.endpoints.roles.get_user_role') as mock_get_role:
        # This will trigger the condition in lines 51-52
        mock_get_role.return_value = mock_admin_role
        
        # Now call the endpoint function directly to execute lines 51-52
        with pytest.raises(PermissionError) as exc:
            await read_user_role(
                user_id=999,  # An admin user's ID
                current_user=mock_current_user,
                db=db
            )
        
        # Verify the specific error message from line 51
        assert "Insufficient permissions to view admin roles" in str(exc.value)
        # Verify that our mock was called, confirming execution path
        mock_get_role.assert_called_once()

def test_member_cannot_view_others_roles(client: TestClient, admin_user_fixture, member_user_fixture):
    """
    Scenario: Member tries to view someone else's role (targeted for line 46)
    Given I have a member user and an admin user
    When the member tries to access another user's role
    Then a permission error should be raised
    And the response should be 403 Forbidden
    """
    # Arrange
    member_headers = {"Authorization": f"Bearer {member_user_fixture['token']}"}
    
    # Act
    # Member tries to get another user's role (admin in this case)
    response = client.get(
        f"/api/v1/roles/roles/users/{admin_user_fixture}", 
        headers=member_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    error_detail = response.json().get("detail", "")
    assert "You can only view your own role" in error_detail

def test_admin_updates_user_role(client: TestClient, member_user_fixture, admin_user_fixture):
    """
    Scenario: Admin updates a user's role (targeted for line 82)
    Given I have an admin user and a member user
    When the admin changes the member's role to operator
    Then the update should be successful
    And the response should be 200 OK with the new role
    """
    # Create admin token
    admin_token = create_access_token(subject=admin_user_fixture, role=RoleEnum.ADMIN)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Act
    # Admin updates a member's role to operator
    response = client.put(
        f"/api/v1/roles/roles/users/{member_user_fixture['id']}", 
        headers=admin_headers,
        json={"role": "OPERATOR"}
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == "OPERATOR"
    
    # Verify the change was applied by getting the user's role
    get_response = client.get(
        f"/api/v1/roles/roles/users/{member_user_fixture['id']}", 
        headers=admin_headers
    )
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["role"] == "OPERATOR"

def test_operator_can_view_member_role(client: TestClient, operator_user_fixture, member_user_fixture):
    """
    Scenario: Operator can view a member's role
    Given I have an operator user and a member user
    When the operator tries to access the member's role
    Then it should be successful
    And the response should be 200 OK
    """
    # Arrange
    operator_headers = {"Authorization": f"Bearer {operator_user_fixture['token']}"}
    
    # Act
    # Operator tries to get a member user's role (should be allowed)
    response = client.get(
        f"/api/v1/roles/roles/users/{member_user_fixture['id']}", 
        headers=operator_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == "MEMBER"

def test_member_can_view_own_role(client: TestClient, member_user_fixture):
    """
    Scenario: Member can view their own role
    Given I have a member user
    When they try to access their own role
    Then it should be successful
    And the response should be 200 OK with their role
    """
    # Arrange
    member_headers = {"Authorization": f"Bearer {member_user_fixture['token']}"}
    
    # Act
    # Member views their own role
    response = client.get(
        f"/api/v1/roles/roles/users/{member_user_fixture['id']}", 
        headers=member_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == "MEMBER"

def test_admin_can_view_all_roles(client: TestClient, admin_user_fixture, operator_user_fixture, member_user_fixture):
    """
    Scenario: Admin can view roles of all user types
    Given I have an admin user and users of different roles
    When the admin tries to access their roles
    Then it should be successful for all user types
    And all responses should be 200 OK
    """
    # Create admin token
    admin_token = create_access_token(subject=admin_user_fixture, role=RoleEnum.ADMIN)
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Act & Assert - Admin can view member's role
    member_response = client.get(
        f"/api/v1/roles/roles/users/{member_user_fixture['id']}", 
        headers=admin_headers
    )
    assert member_response.status_code == status.HTTP_200_OK
    assert member_response.json()["role"] == "MEMBER"
    
    # Act & Assert - Admin can view operator's role
    operator_response = client.get(
        f"/api/v1/roles/roles/users/{operator_user_fixture['id']}", 
        headers=admin_headers
    )
    assert operator_response.status_code == status.HTTP_200_OK
    assert operator_response.json()["role"] == "OPERATOR"
    
    # Act & Assert - Admin can view another admin's role (or their own role)
    admin_response = client.get(
        f"/api/v1/roles/roles/users/{admin_user_fixture}", 
        headers=admin_headers
    )
    assert admin_response.status_code == status.HTTP_200_OK
    assert admin_response.json()["role"] == "ADMIN"

def test_operator_can_view_own_role(client: TestClient, operator_user_fixture):
    """
    Scenario: Operator can view their own role even if they're an admin
    Given I have an operator user
    When they try to access their own role
    Then it should be successful
    And the response should be 200 OK with their role
    """
    # Arrange
    operator_headers = {"Authorization": f"Bearer {operator_user_fixture['token']}"}
    
    # Act
    # Operator views their own role
    response = client.get(
        f"/api/v1/roles/roles/users/{operator_user_fixture['id']}", 
        headers=operator_headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == "OPERATOR"
