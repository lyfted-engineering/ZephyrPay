from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.core.auth import get_current_active_user
from backend.app.schemas.user import UserResponse


# Create router
router = APIRouter(tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="""
    Get information about the currently authenticated user.
    
    - Returns user profile including wallet addresses
    """
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current user's profile information.
    
    Returns the user's profile including wallet information.
    """
    return current_user
