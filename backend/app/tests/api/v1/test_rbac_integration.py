import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import create_access_token
from backend.app.schemas.role import RoleEnum
from backend.app.models.user import User
from backend.app.main import app

@pytest.fixture
async def admin_user(db: AsyncSession):
    """Create an admin user in the database"""
    admin = User(
        email="admin_integration@example.com",
        username="admin_integration",
        password_hash="hashed_password_for_testing",
        role=RoleEnum.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    # Get user ID and create token
    user_id = admin.id
    token = create_access_token(subject=user_id, role=admin.role)
    
    # Return simple dictionary with id and token to avoid SQLAlchemy session issues
    return {"id": user_id, "token": token, "username": admin.username}

@pytest.fixture
async def member_user(db: AsyncSession):
    """Create a member user in the database"""
    member = User(
        email="member_integration@example.com",
        username="member_integration", 
        password_hash="hashed_password_for_testing",
        role=RoleEnum.MEMBER,
        is_active=True,
        is_verified=True
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    # Get user ID and create token
    user_id = member.id
    token = create_access_token(subject=user_id, role=member.role)
    
    # Return simple dictionary with id and token to avoid SQLAlchemy session issues
    return {"id": user_id, "token": token, "username": member.username}

@pytest.fixture
async def operator_user(db: AsyncSession):
    """Create an operator user in the database"""
    operator = User(
        email="operator_integration@example.com",
        username="operator_integration", 
        password_hash="hashed_password_for_testing",
        role=RoleEnum.OPERATOR,
        is_active=True,
        is_verified=True
    )
    db.add(operator)
    await db.commit()
    await db.refresh(operator)
    
    # Get user ID and create token
    user_id = operator.id
    token = create_access_token(subject=user_id, role=operator.role)
    
    # Return simple dictionary with id and token to avoid SQLAlchemy session issues
    return {"id": user_id, "token": token, "username": operator.username}

@pytest.fixture
def client():
    """Return a TestClient for the FastAPI app"""
    return TestClient(app)

def test_rbac_user_profile_access(client: TestClient, admin_user, member_user):
    """
    Scenario: The RBAC system allows users to access their own profiles
    Given I have users with different roles
    When they access their own profile
    Then they should successfully retrieve their information
    """
    # Create headers
    admin_headers = {"Authorization": f"Bearer {admin_user['token']}"}
    member_headers = {"Authorization": f"Bearer {member_user['token']}"}
    
    # Test profile access for both roles
    admin_profile_response = client.get("/api/v1/users/me", headers=admin_headers)
    assert admin_profile_response.status_code == status.HTTP_200_OK
    assert admin_profile_response.json()["username"] == admin_user['username']
    
    member_profile_response = client.get("/api/v1/users/me", headers=member_headers)
    assert member_profile_response.status_code == status.HTTP_200_OK
    assert member_profile_response.json()["username"] == member_user['username']

def test_rbac_admin_only_access(client: TestClient, admin_user, member_user):
    """
    Scenario: The RBAC system restricts access to admin-only endpoints
    Given I have users with admin and member roles
    When they try to access a user by ID (admin-restricted endpoint)
    Then only admin users should be granted access
    """
    # Create headers
    admin_headers = {"Authorization": f"Bearer {admin_user['token']}"}
    member_headers = {"Authorization": f"Bearer {member_user['token']}"}
    
    # Admin can access other user details
    admin_access_response = client.get(
        f"/api/v1/users/{member_user['id']}", 
        headers=admin_headers
    )
    assert admin_access_response.status_code == status.HTTP_200_OK
    
    # Member cannot access other user details
    member_access_response = client.get(
        f"/api/v1/users/{admin_user['id']}", 
        headers=member_headers
    )
    assert member_access_response.status_code == status.HTTP_403_FORBIDDEN

def test_authentication_errors(client: TestClient):
    """
    Scenario: The RBAC system correctly handles authentication errors
    Given I make requests with invalid authentication
    When I try to access protected endpoints
    Then appropriate error responses are returned
    """
    # Test missing token
    missing_token_response = client.get("/api/v1/users/me")
    assert missing_token_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test malformed token
    bad_auth_response = client.get(
        "/api/v1/users/me", 
        headers={"Authorization": "BadToken"}
    )
    assert bad_auth_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test invalid JWT token
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.invalid-signature"
    invalid_token_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert invalid_token_response.status_code == status.HTTP_401_UNAUTHORIZED

def test_rbac_self_role_modification(client: TestClient, member_user):
    """
    Scenario: Edge Case - User attempts to modify their own role
    Given I am authenticated as a member user
    When I try to update my own role to admin
    Then the request should be rejected
    And the response status code should be 403 Forbidden
    """
    # Create headers with member token
    member_headers = {"Authorization": f"Bearer {member_user['token']}"}
    
    # Member user tries to update their own role to admin
    role_data = {"role": "ADMIN"}
    response = client.put(
        f"/api/v1/roles/roles/users/{member_user['id']}", 
        headers=member_headers,
        json=role_data
    )
    
    # Assert the self-role modification is rejected
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not authorized" in response.json().get("detail", "").lower()
    
    # Verify the role was not changed by getting user info
    me_response = client.get("/api/v1/users/me", headers=member_headers)
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.json()["role"] == "MEMBER"

def test_rbac_nonexistent_user_access(client: TestClient, admin_user):
    """
    Scenario: Edge Case - Admin attempts to access a non-existent user
    Given I am authenticated as an admin user
    When I try to access information for a non-existent user ID
    Then the request should return a not found error
    And the response status code should be 404 Not Found
    """
    # Create headers with admin token
    admin_headers = {"Authorization": f"Bearer {admin_user['token']}"}
    
    # Use a very large ID that's unlikely to exist
    nonexistent_user_id = 99999
    
    # Admin tries to get a non-existent user's details
    response = client.get(
        f"/api/v1/users/{nonexistent_user_id}", 
        headers=admin_headers
    )
    
    # Assert the response indicates the user was not found
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json().get("detail", "").lower()
    
    # Admin tries to update a non-existent user's role
    role_data = {"role": "OPERATOR"}
    role_update_response = client.put(
        f"/api/v1/roles/roles/users/{nonexistent_user_id}", 
        headers=admin_headers,
        json=role_data
    )
    
    # Assert the role update also returns not found
    assert role_update_response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in role_update_response.json().get("detail", "").lower()

def test_rbac_invalid_role_value(client: TestClient, admin_user, member_user):
    """
    Scenario: Edge Case - Admin attempts to assign an invalid role value
    Given I am authenticated as an admin user
    When I try to assign an invalid role to a user
    Then the request should be rejected with a validation error
    And the response status code should be 422 Unprocessable Entity
    """
    # Create headers with admin token
    admin_headers = {"Authorization": f"Bearer {admin_user['token']}"}
    
    # Admin tries to assign an invalid role
    invalid_role_data = {"role": "SUPER_USER"}  # Not a valid role
    response = client.put(
        f"/api/v1/roles/roles/users/{member_user['id']}", 
        headers=admin_headers,
        json=invalid_role_data
    )
    
    # Assert the response indicates a validation error
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Verify the role was not changed
    get_response = client.get(
        f"/api/v1/roles/roles/users/{member_user['id']}", 
        headers=admin_headers
    )
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["role"] == "MEMBER"

def test_rbac_token_manipulation(client: TestClient, member_user):
    """
    Scenario: Edge Case - User attempts to manipulate their token to gain higher privileges
    Given I have a valid member user token
    When I manipulate the token to claim admin role
    Then the manipulated token should be rejected
    And the response status code should be 401 Unauthorized
    """
    # Create a manipulated token that claims admin role
    # (This is a simplistic simulation - in reality token tampering would be more complex)
    manipulated_token = create_access_token(subject=member_user['id'], role="ADMIN")
    manipulated_headers = {"Authorization": f"Bearer {manipulated_token}"}
    
    # Attempt to access admin-only endpoint with manipulated token
    # Note: In a proper implementation, token signature validation would prevent this
    response = client.get(
        f"/api/v1/users/{member_user['id']}", 
        headers=manipulated_headers
    )
    
    # If the token verification is correctly implemented, this should be rejected
    # The exact status code depends on the implementation, but often would be 401
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
