import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.future import select
from httpx import AsyncClient, ASGITransport

from backend.app.models.user import User
from backend.app.core.security import create_access_token
from backend.app.schemas.role import RoleEnum
from backend.app.db.session import get_db
from backend.app.main import app

@pytest.fixture
async def admin_token(db: AsyncSession):
    """Create an admin user and return a valid token"""
    # Create test admin user
    admin = User(
        email="admin@example.com",
        username="adminuser",
        password_hash="hashed_password_for_testing",
        role=RoleEnum.ADMIN
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    # Generate token
    token = create_access_token(subject=admin.id, role=admin.role)
    return token


@pytest.fixture
async def operator_token(db: AsyncSession):
    """Create an operator user and return a valid token"""
    # Create test operator user
    operator = User(
        email="operator@example.com",
        username="opuser",
        password_hash="hashed_password_for_testing",
        role=RoleEnum.OPERATOR
    )
    db.add(operator)
    await db.commit()
    await db.refresh(operator)
    
    # Generate token
    token = create_access_token(subject=operator.id, role=operator.role)
    return token


@pytest.fixture
async def member_token(db: AsyncSession):
    """Create a member user and return a valid token"""
    # Create test member user
    member = User(
        email="member@example.com",
        username="memberuser",
        password_hash="hashed_password_for_testing",
        role=RoleEnum.MEMBER
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    # Generate token
    token = create_access_token(subject=member.id, role=member.role)
    return token


@pytest.fixture
async def test_user_id(db: AsyncSession):
    """Create a regular user and return their ID for role tests"""
    user = User(
        email="roletest@example.com",
        username="roleuser",
        password_hash="hashed_password_for_testing",
        role=RoleEnum.MEMBER  # Default role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user.id


@pytest.fixture
async def admin_user_id(db: AsyncSession):
    """Create an admin user and return their ID for role tests"""
    user = User(
        email="admintest@example.com",
        username="admintest",
        password_hash="hashed_password_for_testing",
        role=RoleEnum.ADMIN  # Default role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user.id


@pytest.fixture
async def async_client():
    """Create an async test client for FastAPI"""
    from fastapi.testclient import TestClient
    from httpx import ASGITransport
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def admin_token_async():
    """Create an admin token for async tests"""
    return create_access_token(
        data={"sub": "999", "role": RoleEnum.ADMIN},
        expires_delta=None
    )


def test_assign_role_admin_success(client: TestClient, admin_token, test_user_id):
    """
    Scenario: Admin successfully assigns a role to a user
    Given I am authenticated as an admin
    When I assign the "OPERATOR" role to a user
    Then the user's role should be updated to "OPERATOR"
    And the response status should be 200 OK
    """
    # Arrange
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_data = {"role": "OPERATOR"}
    
    # Act
    endpoint = f"/api/v1/roles/roles/users/{test_user_id}"
    print(f"Trying to access endpoint: {endpoint}")
    response = client.put(
        endpoint,
        headers=headers,
        json=role_data
    )
    
    # Print response
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == "OPERATOR"
    
    # Verify updated role by making a GET request
    get_response = client.get(
        f"/api/v1/roles/roles/users/{test_user_id}",
        headers=headers
    )
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["role"] == "OPERATOR"


def test_assign_role_operator_forbidden(client: TestClient, operator_token, test_user_id):
    """
    Scenario: Operator attempts to assign a role
    Given I am authenticated as an operator
    When I try to assign a role to a user
    Then I should receive a forbidden error
    And the response status should be 403 Forbidden
    """
    # Arrange
    headers = {"Authorization": f"Bearer {operator_token}"}
    role_data = {"role": "ADMIN"}
    
    # Act
    endpoint = f"/api/v1/roles/roles/users/{test_user_id}"
    print(f"Trying to access endpoint: {endpoint}")
    response = client.put(
        endpoint,
        headers=headers,
        json=role_data
    )
    
    # Print response
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_assign_role_member_forbidden(client: TestClient, member_token, test_user_id):
    """
    Scenario: Member attempts to assign a role
    Given I am authenticated as a member
    When I try to assign a role to a user
    Then I should receive a forbidden error
    And the response status should be 403 Forbidden
    """
    # Arrange
    headers = {"Authorization": f"Bearer {member_token}"}
    role_data = {"role": "OPERATOR"}
    
    # Act
    endpoint = f"/api/v1/roles/roles/users/{test_user_id}"
    print(f"Trying to access endpoint: {endpoint}")
    response = client.put(
        endpoint,
        headers=headers,
        json=role_data
    )
    
    # Print response
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_assign_invalid_role(client: TestClient, admin_token, test_user_id):
    """
    Scenario: Admin attempts to assign an invalid role
    Given I am authenticated as an admin
    When I try to assign an invalid role to a user
    Then I should receive a validation error
    And the response status should be 422 Unprocessable Entity
    """
    # Arrange
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_data = {"role": "INVALID_ROLE"}
    
    # Act
    endpoint = f"/api/v1/roles/roles/users/{test_user_id}"
    print(f"Trying to access endpoint: {endpoint}")
    response = client.put(
        endpoint,
        headers=headers,
        json=role_data
    )
    
    # Print response
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_user_role(client: TestClient, admin_token, test_user_id):
    """
    Scenario: Admin retrieves a user's role
    Given I am authenticated as an admin
    When I request a user's role information
    Then I should receive the user's current role
    And the response status should be 200 OK
    """
    # Arrange
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Act
    endpoint = f"/api/v1/roles/roles/users/{test_user_id}"
    print(f"Trying to access endpoint: {endpoint}")
    response = client.get(
        endpoint,
        headers=headers
    )
    
    # Print response
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert "role" in response.json()


def test_get_nonexistent_user_role(client: TestClient, admin_token):
    """
    Scenario: Admin attempts to retrieve a non-existent user's role
    Given I am authenticated as an admin
    When I request a non-existent user's role information
    Then I should receive a not found error
    And the response status should be 404 Not Found
    """
    # Arrange
    headers = {"Authorization": f"Bearer {admin_token}"}
    non_existent_id = 99999
    
    # Act
    endpoint = f"/api/v1/roles/roles/users/{non_existent_id}"
    print(f"Trying to access endpoint: {endpoint}")
    response = client.get(
        endpoint,
        headers=headers
    )
    
    # Print response
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json().get("detail", "").lower()


def test_update_nonexistent_user_role(client: TestClient, admin_token):
    """
    Scenario: Admin attempts to update a non-existent user's role
    Given I am authenticated as an admin
    When I update a non-existent user's role
    Then I should receive a not found error
    And the response status should be 404 Not Found
    """
    # Arrange
    headers = {"Authorization": f"Bearer {admin_token}"}
    non_existent_id = 99999
    role_data = {"role": "OPERATOR"}
    
    # Act
    endpoint = f"/api/v1/roles/roles/users/{non_existent_id}"
    print(f"Trying to access endpoint: {endpoint}")
    response = client.put(
        endpoint,
        headers=headers,
        json=role_data
    )
    
    # Print response
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json().get("detail", "").lower()


def test_get_role_permission_errors_member(client: TestClient, member_token, test_user_id):
    """
    Scenario: Member tries to view someone else's role
    Given I am authenticated as a member
    When I try to view another user's role
    Then I should get a permission error
    """
    # Test case: Member tries to view someone else's role
    member_headers = {"Authorization": f"Bearer {member_token}"}
    response = client.get(
        f"/api/v1/roles/roles/users/{test_user_id}", 
        headers=member_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "only view your own role" in response.json().get("detail", "").lower()


def test_get_role_permission_errors_operator(client: TestClient, operator_token, admin_user_id):
    """
    Scenario: Operator tries to view an admin's role
    Given I am authenticated as an operator
    When I try to view an admin's role
    Then I should get a permission error
    """
    # Test case: Operator tries to view an admin's role
    operator_headers = {"Authorization": f"Bearer {operator_token}"}
    response = client.get(
        f"/api/v1/roles/roles/users/{admin_user_id}",
        headers=operator_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "insufficient permissions" in response.json().get("detail", "").lower()


def test_invalid_token_access(client: TestClient):
    """
    Scenario: User with invalid token tries to access role endpoints
    Given I have an invalid authentication token
    When I try to access role endpoints
    Then I should receive an unauthorized error
    And the response status should be 401 Unauthorized
    """
    # Arrange - Create invalid token
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    invalid_headers = {"Authorization": f"Bearer {invalid_token}"}
    
    # Test GET endpoint
    get_response = client.get(
        f"/api/v1/roles/roles/users/1",
        headers=invalid_headers
    )
    assert get_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test PUT endpoint
    put_response = client.put(
        f"/api/v1/roles/roles/users/1",
        headers=invalid_headers,
        json={"role": "OPERATOR"}
    )
    assert put_response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_with_role_direct_db_check(client: TestClient, admin_token):
    """
    Scenario: Admin creates a user with a specific role
    Given I am authenticated as an admin
    When I create a new user with the role "OPERATOR"
    Then the user should be created with the "OPERATOR" role
    And the response should indicate the correct role assignment
    """
    # Arrange
    headers = {"Authorization": f"Bearer {admin_token}"}
    user_data = {
        "email": "newop_direct@example.com",
        "username": "newop_direct",
        "password": "StrongP@ss123"
    }
    
    # Act
    response = client.post(
        "/api/v1/users?role=OPERATOR",
        headers=headers,
        json=user_data
    )
    
    # Assert HTTP response
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["role"] == "OPERATOR"
    
    # Get the user from the API to verify
    user_id = response.json()["id"]
    
    # Make a second API call to verify the role (instead of direct DB access)
    get_response = client.get(
        f"/api/v1/roles/roles/users/{user_id}",
        headers=headers
    )
    
    # Verify the role was properly set
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["role"] == "OPERATOR"
