from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.schemas.role import RoleRead, RoleUpdate
from backend.app.services.role import get_user_role, update_user_role
from backend.app.core.auth import get_current_user
from backend.app.core.rbac import rbac_required
from backend.app.models.user import User
from backend.app.schemas.role import RoleEnum
from backend.app.core.errors import PermissionError


# Create router
router = APIRouter(prefix="/roles", tags=["roles"])


@router.get(
    "/users/{user_id}",
    response_model=RoleRead,
    status_code=status.HTTP_200_OK,
    summary="Get a user's role",
    description="""
    Retrieve the current role for a specific user.
    
    - Requires authentication
    - Admin can view any user's role
    - Operators can view non-admin roles
    - Members can only view their own role
    """
)
async def read_user_role(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a user's current role.
    
    Admin users can view any user's role.
    Operators can view non-admin user roles.
    Members can only view their own role.
    """
    # Members can only view their own role
    if current_user.role == RoleEnum.MEMBER and current_user.id != user_id:
        raise PermissionError(message="You can only view your own role")
    
    # Operators cannot view admin roles
    if current_user.role == RoleEnum.OPERATOR:
        target_role = await get_user_role(db, user_id)
        if target_role.role == RoleEnum.ADMIN and current_user.id != user_id:
            raise PermissionError(message="Insufficient permissions to view admin roles")
    
    return await get_user_role(db, user_id)


@router.put(
    "/users/{user_id}",
    response_model=RoleRead,
    status_code=status.HTTP_200_OK,
    summary="Update a user's role",
    description="""
    Update the role for a specific user.
    
    - Requires admin role
    - Only admins can update roles
    - Role must be one of: ADMIN, OPERATOR, MEMBER
    """
)
@rbac_required([RoleEnum.ADMIN])
async def update_role(
    user_id: int,
    role_update: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's role.
    
    Only admin users can update roles.
    """
    return await update_user_role(
        db=db,
        user_id=user_id,
        role_update=role_update,
        current_user_role=current_user.role
    )
