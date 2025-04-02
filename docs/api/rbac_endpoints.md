# ZephyrPay Role-Based Access Control (RBAC) API Documentation

This document details the Role-Based Access Control (RBAC) endpoints in the ZephyrPay API, explaining the available operations, required permissions, and expected responses.

## Overview

The RBAC system in ZephyrPay provides three role levels:

- **ADMIN**: Full system access, including user management and role assignments
- **OPERATOR**: Operational access for payment processing and limited user management
- **MEMBER**: Standard user access for basic account functions

## Endpoints

### Get User Role

Retrieves a user's current role.

```
GET /api/v1/roles/roles/users/{user_id}
```

#### Authentication
- Bearer token required

#### Authorization
- ADMIN: Can view any user's role
- OPERATOR: Can view roles of users with MEMBER role
- MEMBER: Can only view their own role

#### Path Parameters
- `user_id` (integer, required): The ID of the user whose role to retrieve

#### Responses
- `200 OK`: Successfully retrieved the role
  ```json
  {
    "user_id": 123,
    "role": "MEMBER"
  }
  ```
- `403 Forbidden`: Insufficient permissions to view the requested role
- `404 Not Found`: User with specified ID not found

### Update User Role

Updates a user's role to a new value.

```
PUT /api/v1/roles/roles/users/{user_id}
```

#### Authentication
- Bearer token required

#### Authorization
- ADMIN only: Only administrators can change user roles

#### Path Parameters
- `user_id` (integer, required): The ID of the user whose role to update

#### Request Body
```json
{
  "role": "OPERATOR"
}
```

#### Responses
- `200 OK`: Successfully updated the role
  ```json
  {
    "user_id": 123,
    "role": "OPERATOR"
  }
  ```
- `400 Bad Request`: Invalid role provided
- `403 Forbidden`: Not authorized to change roles
- `404 Not Found`: User with specified ID not found

### Assign Role During User Creation

When creating a new user, you can specify their initial role.

```
POST /api/v1/users?role={role}
```

#### Authentication
- Bearer token required

#### Authorization
- ADMIN only: Only administrators can specify a custom role during user creation
- All other roles: Users are created with the default MEMBER role

#### Query Parameters
- `role` (string, optional): Role to assign to the new user ("ADMIN", "OPERATOR", or "MEMBER")
  - Default: "MEMBER"

#### Request Body
```json
{
  "email": "user@example.com",
  "username": "newuser",
  "password": "SecurePassword123"
}
```

#### Responses
- `201 Created`: User successfully created with specified role
  ```json
  {
    "id": 123,
    "email": "user@example.com",
    "username": "newuser",
    "role": "OPERATOR",
    "is_active": true
  }
  ```
- `400 Bad Request`: Invalid input data
- `403 Forbidden`: Not authorized to create users with custom roles
- `409 Conflict`: Email or username already exists

## Error Handling

All RBAC endpoints use consistent error handling:

- Permission errors return HTTP 403 with a descriptive message
- Not found errors return HTTP 404 with a descriptive message
- Validation errors return HTTP 400 with details about the invalid fields

## Testing Coverage

All RBAC components have been thoroughly tested with:

- Core RBAC Middleware: 100% coverage
- Role Schemas: 100% coverage
- Role Services: 100% coverage
- API Endpoints: 92% coverage
- Overall RBAC Coverage: 98%

A minimum of 90% test coverage is maintained for all RBAC features to ensure security in this financial application.
