from fastapi import APIRouter, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.schemas.user import UserCreate, Token, LoginRequest
from backend.app.services.auth import register_user, login_user
from backend.app.core.errors import AuthError, DuplicateError


# Create router
router = APIRouter(tags=["authentication"])


@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Register a new user in the ZephyrPay system.
    
    - Validates email format and password strength
    - Checks for duplicate emails
    - Returns a JWT token upon successful registration
    """
)
async def user_register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with email, username, and password.
    
    Returns a JWT token that can be used to authenticate future requests.
    """
    try:
        token = await register_user(db, user_data)
        return token
    except DuplicateError as e:
        # Re-raise as HTTPException with appropriate status code
        raise AuthError(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST
        )


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login for existing users",
    description="""
    Authenticate an existing user and issue a JWT token.
    
    - Validates credentials
    - Returns a JWT token upon successful authentication
    """
)
async def user_login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns a JWT token for authentication.
    """
    token = await login_user(db, login_data.email, login_data.password)
    return token