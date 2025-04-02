from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class EthWalletBase(BaseModel):
    """Base model for Ethereum wallet operations"""
    eth_address: str = Field(..., description="Ethereum wallet address")
    
    @field_validator("eth_address")
    def validate_eth_address(cls, v: str) -> str:
        """Validate Ethereum address format"""
        # ETH address validation: 0x followed by 40 hex characters
        if not re.match(r"^0x[a-fA-F0-9]{40}$", v):
            raise ValueError("Invalid Ethereum address format. Must be 0x followed by 40 hexadecimal characters")
        return v


class LnWalletBase(BaseModel):
    """Base model for Lightning Network wallet operations"""
    ln_address: str = Field(..., description="Lightning Network wallet address or LNURL")
    
    @field_validator("ln_address")
    def validate_ln_address(cls, v: str) -> str:
        """Validate Lightning Network address format"""
        # Basic LNURL validation: starts with lnurl and contains valid characters
        if not re.match(r"^lnurl[a-zA-Z0-9]{1,}$", v):
            raise ValueError("Invalid Lightning Network address format. Must start with 'lnurl' followed by alphanumeric characters")
        return v


class WalletResponse(BaseModel):
    """Response model for wallet operations"""
    message: str


class UserWallets(BaseModel):
    """User wallet information model"""
    eth_address: Optional[str] = None
    ln_address: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }
