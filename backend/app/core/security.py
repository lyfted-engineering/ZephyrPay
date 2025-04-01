from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext

from backend.app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token settings
ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], role: str, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    
    Args:
        subject: The subject of the token (typically user ID)
        role: User role for RBAC
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token as string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire, 
        "sub": str(subject), 
        "role": role,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=ALGORITHM
    )
    
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)