import os
import secrets
from typing import Any, Dict, Optional, List, Union

from pydantic import field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings for the ZephyrPay backend"""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Server settings
    SERVER_NAME: str = "ZephyrPay API"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]
    
    # Database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "zephyrpay")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # Redis (for caching) settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    
    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Crypto integration settings
    LNBITS_URL: str = os.getenv("LNBITS_URL", "https://legend.lnbits.com")
    LNBITS_API_KEY: str = os.getenv("LNBITS_API_KEY", "")
    ETHEREUM_RPC_URL: str = os.getenv("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/")
    
    # Construct database URIs
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    ASYNC_SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"postgresql://{info.data.get('POSTGRES_USER')}:{info.data.get('POSTGRES_PASSWORD')}@{info.data.get('POSTGRES_SERVER')}:{info.data.get('POSTGRES_PORT')}/{info.data.get('POSTGRES_DB')}"
    
    @field_validator("ASYNC_SQLALCHEMY_DATABASE_URI", mode="before")
    def assemble_async_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return f"postgresql+asyncpg://{info.data.get('POSTGRES_USER')}:{info.data.get('POSTGRES_PASSWORD')}@{info.data.get('POSTGRES_SERVER')}:{info.data.get('POSTGRES_PORT')}/{info.data.get('POSTGRES_DB')}"
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


# Create settings instance
settings = Settings()