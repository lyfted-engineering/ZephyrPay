from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.user import User
from backend.app.core.errors import AuthError


async def link_eth_wallet(db: AsyncSession, user_id: int, eth_address: str) -> bool:
    """
    Link an Ethereum wallet to a user account
    
    Args:
        db: AsyncSession
        user_id: User ID
        eth_address: Ethereum address to link
        
    Returns:
        True if wallet was linked successfully
        
    Raises:
        AuthError: If user not found
    """
    # Get user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise AuthError(message="User not found", status_code=404)
    
    # Update user's ETH address
    user.eth_address = eth_address
    await db.commit()
    
    return True


async def link_ln_wallet(db: AsyncSession, user_id: int, ln_address: str) -> bool:
    """
    Link a Lightning Network wallet to a user account
    
    Args:
        db: AsyncSession
        user_id: User ID
        ln_address: Lightning Network address to link
        
    Returns:
        True if wallet was linked successfully
        
    Raises:
        AuthError: If user not found
    """
    # Get user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise AuthError(message="User not found", status_code=404)
    
    # Update user's LN address
    user.ln_address = ln_address
    await db.commit()
    
    return True


async def get_user_wallets(db: AsyncSession, user_id: int) -> dict:
    """
    Get a user's wallet information
    
    Args:
        db: AsyncSession
        user_id: User ID
        
    Returns:
        Dictionary containing wallet information
        
    Raises:
        AuthError: If user not found
    """
    # Get user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise AuthError(message="User not found", status_code=404)
    
    return {
        "eth_address": user.eth_address,
        "ln_address": user.ln_address
    }
