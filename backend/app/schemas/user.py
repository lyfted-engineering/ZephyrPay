from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, Field
import re


class UserBase(BaseModel):
    """Base schema for User data"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for user creation/registration"""
    password: str = Field(..., min_length=8)

    @field_validator('password')
    def password_strength_check(cls, v):
        """
        Validate password strength:
        - At least 8 characters
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one number
        - Contains at least one special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v


class UserRead(UserBase):
    """Schema for reading user data (response model)"""
    id: int
    role: str
    is_active: bool
    eth_address: Optional[str] = None
    ln_pubkey: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class UserUpdate(BaseModel):
    """Schema for updating user data"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    
    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Schema for token payload (JWT contents)"""
    user_id: int
    role: str


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str