from fastapi import APIRouter, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.schemas.user import UserCreate, Token, LoginRequest, PasswordResetRequest, PasswordReset, PasswordResetResponse
from backend.app.services.auth import register_user, login_user, request_password_reset, reset_password
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


@router.post(
    "/password-reset-request",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="""
    Request a password reset token.
    
    - Checks if the email exists
    - Generates a password reset token
    - In production, sends an email with the reset link
    """
)
async def password_reset_request(
    reset_data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset.
    
    Returns a success message and, for testing purposes, the reset token.
    In a production environment, the token would be sent by email instead.
    """
    reset_token = await request_password_reset(db, reset_data.email)
    
    # Always return success for security (don't leak user existence)
    # In testing, include the token for convenience
    return PasswordResetResponse(
        message="If your email is registered, you will receive a password reset link",
        reset_token=reset_token  # In production, remove this and send via email
    )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password with token",
    description="""
    Reset a user's password using a valid reset token.
    
    - Validates the token
    - Updates the password if the token is valid
    """
)
async def reset_password_with_token(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset a password using a valid token.
    
    Returns a success message or an error if the token is invalid.
    """
    try:
        await reset_password(db, reset_data.token, reset_data.new_password)
        return PasswordResetResponse(
            message="Your password has been successfully updated"
        )
    except AuthError as e:
        # Re-raise the error
        raise e