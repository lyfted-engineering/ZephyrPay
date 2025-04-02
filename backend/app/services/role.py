from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from backend.app.models.user import User
from backend.app.schemas.role import RoleEnum, RoleUpdate, RoleRead
from backend.app.core.errors import NotFoundError, PermissionError


async def get_user_role(db: AsyncSession, user_id: int) -> RoleRead:
    """
    Get a user's current role
    
    Args:
        db: Async database session
        user_id: ID of the user
        
    Returns:
        RoleRead schema with user ID and role
        
    Raises:
        NotFoundError: If user doesn't exist
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise NotFoundError(message=f"User with ID {user_id} not found")
    
    return RoleRead(
        user_id=user.id,
        role=user.role
    )


async def update_user_role(
    db: AsyncSession,
    user_id: int,
    role_update: RoleUpdate,
    current_user_role: str
) -> RoleRead:
    """
    Update a user's role
    
    Args:
        db: Async database session
        user_id: ID of the user to update
        role_update: New role data
        current_user_role: Role of the user making the request
        
    Returns:
        Updated RoleRead schema
        
    Raises:
        NotFoundError: If user doesn't exist
        PermissionError: If current user doesn't have permission to change roles
    """
    # Only admins can change roles
    if current_user_role != RoleEnum.ADMIN:
        raise PermissionError(message="Only administrators can change user roles")
    
    # Get user to update
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise NotFoundError(message=f"User with ID {user_id} not found")
    
    # Update role
    user.role = role_update.role
    await db.commit()
    await db.refresh(user)
    
    return RoleRead(
        user_id=user.id,
        role=user.role
    )


async def assign_initial_role(
    db: AsyncSession,
    user_id: int,
    role: RoleEnum = RoleEnum.MEMBER
) -> RoleRead:
    """
    Assign initial role to a newly created user
    
    Args:
        db: Async database session
        user_id: ID of the user
        role: Role to assign (defaults to MEMBER)
        
    Returns:
        RoleRead schema with user ID and assigned role
        
    Raises:
        NotFoundError: If user doesn't exist
    """
    # Get user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise NotFoundError(message=f"User with ID {user_id} not found")
    
    # Assign role
    user.role = role
    await db.commit()
    await db.refresh(user)
    
    return RoleRead(
        user_id=user.id,
        role=user.role
    )
