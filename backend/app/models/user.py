from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql import func

from backend.app.db.base import Base


class User(Base):
    """
    SQLAlchemy User model
    
    Represents users in the database including their authentication details
    and wallet information (ETH address and Lightning Network pubkey)
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Crypto wallet addresses
    eth_address = Column(String, nullable=True)
    ln_pubkey = Column(String, nullable=True)
    
    # Role-based access control (Admin, Operator, Member)
    role = Column(String, nullable=False, default="MEMBER")
    
    # Account status
    is_active = Column(Boolean(), default=True)
    is_verified = Column(Boolean(), default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())