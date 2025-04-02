from enum import Enum
from pydantic import BaseModel, Field


class RoleEnum(str, Enum):
    """
    Enumeration of valid user roles in the system.
    
    - ADMIN: Full system access, can manage users and assign roles
    - OPERATOR: Can manage content and perform operational tasks
    - MEMBER: Regular user with limited access
    """
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    MEMBER = "MEMBER"


class RoleUpdate(BaseModel):
    """
    Schema for updating a user's role.
    
    Attributes:
        role: The new role to assign to the user
    """
    role: RoleEnum = Field(..., description="Role to assign to the user")


class RoleRead(BaseModel):
    """
    Schema for reading a user's role information.
    
    Attributes:
        user_id: The user's ID
        role: The user's current role
    """
    user_id: int
    role: RoleEnum
    
    model_config = {
        "from_attributes": True
    }
