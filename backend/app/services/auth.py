from typing import Optional
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, Token
from backend.app.core.security import get_password_hash, verify_password, create_access_token, create_password_reset_token, verify_password_reset_token
from backend.app.core.config import settings
from backend.app.core.errors import DuplicateError, AuthError


async def register_user(db: AsyncSession, user_data: UserCreate) -> Token:
    """
    Register a new user
    
    Args:
        db: Async database session
        user_data: Validated user creation data
        
    Returns:
        Authentication token
        
    Raises:
        DuplicateError: If a user with the same email already exists
    """
    # Check if user already exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise DuplicateError(message=f"User with email {user_data.email} already exists")
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        role="MEMBER"  # Default role
    )
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise DuplicateError(message="User with this email or username already exists")
    
    # Create access token
    access_token = create_access_token(
        subject=new_user.id,
        role=new_user.role
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Optional[User]:
    """
    Authenticate a user with email and password
    
    Args:
        db: Async database session
        email: User email
        password: User password
        
    Returns:
        User object if authentication is successful, None otherwise
    """
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user or not verify_password(password, user.password_hash):
        return None
    
    if not user.is_active:
        return None
    
    return user


async def login_user(db: AsyncSession, email: str, password: str) -> Token:
    """
    Login a user and generate JWT token
    
    Args:
        db: AsyncSession
        email: User email
        password: User password
        
    Returns:
        Authentication token
        
    Raises:
        AuthError: If authentication fails
    """
    user = await authenticate_user(db, email, password)
    
    if not user:
        raise AuthError(message="Incorrect email or password")
    
    access_token = create_access_token(
        subject=user.id,
        role=user.role
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )


async def request_password_reset(db: AsyncSession, email: str) -> Optional[str]:
    """
    Request a password reset token
    
    Args:
        db: AsyncSession
        email: User email
        
    Returns:
        Password reset token if user exists, otherwise None
    """
    # Check if user exists
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        return None
    
    # Generate password reset token
    reset_token = create_password_reset_token(email=email)
    
    # In a real application, we would send an email here
    # For example: await send_reset_email(user.email, reset_token)
    
    return reset_token


async def reset_password(db: AsyncSession, token: str, new_password: str) -> bool:
    """
    Reset user password with token
    
    Args:
        db: AsyncSession
        token: Password reset token
        new_password: New password
        
    Returns:
        True if password was reset, False otherwise
        
    Raises:
        AuthError: If token is invalid or expired
    """
    # Verify token
    email = verify_password_reset_token(token)
    if not email:
        raise AuthError(message="Invalid or expired token", status_code=400)
    
    # Find user
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise AuthError(message="User not found", status_code=404)
    
    # Update password
    user.password_hash = get_password_hash(new_password)
    await db.commit()
    
    return True