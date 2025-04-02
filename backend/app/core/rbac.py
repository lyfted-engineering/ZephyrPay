from typing import List, Callable
from functools import wraps

from fastapi import Depends, HTTPException, status
from backend.app.models.user import User
from backend.app.core.auth import get_current_user
from backend.app.core.errors import PermissionError


def rbac_required(allowed_roles: List[str]) -> Callable:
    """
    Role-based access control dependency.
    
    This decorator checks if the current user has one of the allowed roles.
    If not, it raises a 403 Forbidden exception.
    
    Args:
        allowed_roles: List of roles that are allowed to access the endpoint
        
    Returns:
        Dependency function that checks user's role
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role not in allowed_roles:
                raise PermissionError(
                    message=f"Role {current_user.role} not authorized to perform this action"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def is_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Check if the current user is an admin.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        The current user if they are an admin
        
    Raises:
        PermissionError: If the user is not an admin
    """
    if current_user.role != "ADMIN":
        raise PermissionError(message="Admin role required")
    return current_user


def is_operator_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Check if the current user is an operator or admin.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        The current user if they are an operator or admin
        
    Raises:
        PermissionError: If the user is not an operator or admin
    """
    if current_user.role not in ["ADMIN", "OPERATOR"]:
        raise PermissionError(message="Operator or Admin role required")
    return current_user
