import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from fastapi import status

from backend.app.models.user import User
from backend.app.core.security import create_access_token, get_password_hash
from backend.app.schemas.role import RoleEnum


@pytest.fixture
async def admin_token(db: AsyncSession):
    """Create an admin user and return a valid token"""
    admin = User(
        email="rbac_admin@example.com",
        username="rbac_admin",
        password_hash=get_password_hash("StrongP@ssw0rd"),
        role=RoleEnum.ADMIN
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    token = create_access_token(subject=admin.id, role=admin.role)
    return token, admin.id


@pytest.fixture
async def operator_token(db: AsyncSession):
    """Create an operator user and return a valid token"""
    operator = User(
        email="rbac_operator@example.com",
        username="rbac_operator",
        password_hash=get_password_hash("StrongP@ssw0rd"),
        role=RoleEnum.OPERATOR
    )
    db.add(operator)
    await db.commit()
    await db.refresh(operator)
    
    token = create_access_token(subject=operator.id, role=operator.role)
    return token, operator.id


@pytest.fixture
async def member_token(db: AsyncSession):
    """Create a member user and return a valid token"""
    member = User(
        email="rbac_member@example.com",
        username="rbac_member",
        password_hash=get_password_hash("StrongP@ssw0rd"),
        role=RoleEnum.MEMBER
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    token = create_access_token(subject=member.id, role=member.role)
    return token, member.id


@pytest.fixture
async def test_user(db: AsyncSession):
    """Create a test user to operate on"""
    user = User(
        email="rbac_test@example.com",
        username="rbac_test",
        password_hash=get_password_hash("StrongP@ssw0rd"),
        role=RoleEnum.MEMBER
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user.id


def test_admin_can_list_users(client: TestClient, admin_token):
    """
    Scenario: Admin can list all users
    Given I am authenticated as an admin
    When I request the list of all users
    Then I should receive the list of users
    And the response status should be 200 OK
    """
    # Arrange
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.get("/api/v1/users", headers=headers)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_operator_can_list_users(client: TestClient, operator_token):
    """
    Scenario: Operator can list all users
    Given I am authenticated as an operator
    When I request the list of all users
    Then I should receive the list of users
    And the response status should be 200 OK
    """
    # Arrange
    token, _ = operator_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.get("/api/v1/users", headers=headers)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_member_cannot_list_users(client: TestClient, member_token):
    """
    Scenario: Member cannot list all users
    Given I am authenticated as a member
    When I request the list of all users
    Then I should receive a forbidden error
    And the response status should be 403 Forbidden
    """
    # Arrange
    token, _ = member_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.get("/api/v1/users", headers=headers)
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_get_user_by_id(client: TestClient, admin_token, test_user):
    """
    Scenario: Admin can get a user by ID
    Given I am authenticated as an admin
    When I request a specific user by ID
    Then I should receive the user details
    And the response status should be 200 OK
    """
    # Arrange
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.get(f"/api/v1/users/{test_user}", headers=headers)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_user


def test_operator_can_get_user_by_id(client: TestClient, operator_token, test_user):
    """
    Scenario: Operator can get a user by ID
    Given I am authenticated as an operator
    When I request a specific user by ID
    Then I should receive the user details
    And the response status should be 200 OK
    """
    # Arrange
    token, _ = operator_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.get(f"/api/v1/users/{test_user}", headers=headers)
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_user


def test_member_cannot_get_user_by_id(client: TestClient, member_token, test_user):
    """
    Scenario: Member cannot get a user by ID
    Given I am authenticated as a member
    When I request a specific user by ID
    Then I should receive a forbidden error
    And the response status should be 403 Forbidden
    """
    # Arrange
    token, _ = member_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.get(f"/api/v1/users/{test_user}", headers=headers)
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_create_user(client: TestClient, admin_token):
    """
    Scenario: Admin can create a new user
    Given I am authenticated as an admin
    When I create a new user
    Then the user should be created successfully
    And the response status should be 201 Created
    """
    # Arrange
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "StrongP@ssw0rd1"
    }
    
    # Act
    response = client.post(
        "/api/v1/users",
        headers=headers,
        json=user_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == user_data["email"]


def test_admin_can_create_user_with_role(client: TestClient, admin_token):
    """
    Scenario: Admin can create a new user with a specific role
    Given I am authenticated as an admin
    When I create a new user with the OPERATOR role
    Then the user should be created with the OPERATOR role
    And the response status should be 201 Created
    """
    # Arrange
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    user_data = {
        "email": "newoperator@example.com",
        "username": "newoperator",
        "password": "StrongP@ssw0rd1"
    }
    
    # Act
    response = client.post(
        "/api/v1/users?role=OPERATOR",
        headers=headers,
        json=user_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == user_data["email"]
    assert response.json()["role"] == "OPERATOR"


def test_operator_cannot_create_user(client: TestClient, operator_token):
    """
    Scenario: Operator cannot create a new user
    Given I am authenticated as an operator
    When I try to create a new user
    Then I should receive a forbidden error
    And the response status should be 403 Forbidden
    """
    # Arrange
    token, _ = operator_token
    headers = {"Authorization": f"Bearer {token}"}
    user_data = {
        "email": "operatorcreated@example.com",
        "username": "opcreated",
        "password": "StrongP@ssw0rd1"
    }
    
    # Act
    response = client.post(
        "/api/v1/users",
        headers=headers,
        json=user_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_member_cannot_create_user(client: TestClient, member_token):
    """
    Scenario: Member cannot create a new user
    Given I am authenticated as a member
    When I try to create a new user
    Then I should receive a forbidden error
    And the response status should be 403 Forbidden
    """
    # Arrange
    token, _ = member_token
    headers = {"Authorization": f"Bearer {token}"}
    user_data = {
        "email": "membercreated@example.com",
        "username": "memcreated",
        "password": "StrongP@ssw0rd1"
    }
    
    # Act
    response = client.post(
        "/api/v1/users",
        headers=headers,
        json=user_data
    )
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_delete_user(client: TestClient, admin_token, test_user):
    """
    Scenario: Admin can delete a user
    Given I am authenticated as an admin
    When I delete a user
    Then the user should be deleted successfully
    And the response status should be 204 No Content
    """
    # Arrange
    token, _ = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.delete(
        f"/api/v1/users/{test_user}",
        headers=headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify user is deleted
    get_response = client.get(
        f"/api/v1/users/{test_user}",
        headers=headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_admin_cannot_delete_self(client: TestClient, admin_token):
    """
    Scenario: Admin cannot delete their own account
    Given I am authenticated as an admin
    When I try to delete my own account
    Then I should receive an error
    And the response status should be 403 Forbidden
    """
    # Arrange
    token, admin_id = admin_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.delete(
        f"/api/v1/users/{admin_id}",
        headers=headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "Cannot delete your own account" in response.json()["detail"]


def test_operator_cannot_delete_user(client: TestClient, operator_token, test_user):
    """
    Scenario: Operator cannot delete a user
    Given I am authenticated as an operator
    When I try to delete a user
    Then I should receive a forbidden error
    And the response status should be 403 Forbidden
    """
    # Arrange
    token, _ = operator_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.delete(
        f"/api/v1/users/{test_user}",
        headers=headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_member_cannot_delete_user(client: TestClient, member_token, test_user):
    """
    Scenario: Member cannot delete a user
    Given I am authenticated as a member
    When I try to delete a user
    Then I should receive a forbidden error
    And the response status should be 403 Forbidden
    """
    # Arrange
    token, _ = member_token
    headers = {"Authorization": f"Bearer {token}"}
    
    # Act
    response = client.delete(
        f"/api/v1/users/{test_user}",
        headers=headers
    )
    
    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
