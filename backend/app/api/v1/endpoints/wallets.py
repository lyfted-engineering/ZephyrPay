from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.core.auth import get_current_active_user
from backend.app.schemas.wallet import (
    EthWalletBase, 
    LnWalletBase, 
    WalletResponse, 
    UserWallets
)
from backend.app.services.wallet import link_eth_wallet, link_ln_wallet, get_user_wallets
from backend.app.core.errors import AuthError


# Create router
router = APIRouter(tags=["wallets"])


@router.post(
    "/eth",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
    summary="Link Ethereum wallet",
    description="""
    Link an Ethereum wallet to your ZephyrPay account.
    
    - Validates ETH address format (0x followed by 40 hex characters)
    - Links the wallet to your user profile
    """
)
async def link_ethereum_wallet(
    wallet_data: EthWalletBase,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Link an Ethereum wallet to the current user's account.
    
    Returns a success message.
    """
    try:
        await link_eth_wallet(db, current_user.id, wallet_data.eth_address)
        return WalletResponse(message="Ethereum wallet linked successfully")
    except AuthError as e:
        # Re-raise as HTTPException with appropriate status code
        raise e


@router.post(
    "/ln",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
    summary="Link Lightning wallet",
    description="""
    Link a Lightning Network wallet to your ZephyrPay account.
    
    - Validates Lightning Network address format
    - Links the wallet to your user profile
    """
)
async def link_lightning_wallet(
    wallet_data: LnWalletBase,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Link a Lightning Network wallet to the current user's account.
    
    Returns a success message.
    """
    try:
        await link_ln_wallet(db, current_user.id, wallet_data.ln_address)
        return WalletResponse(message="Lightning wallet linked successfully")
    except AuthError as e:
        # Re-raise as HTTPException with appropriate status code
        raise e


@router.put(
    "/eth",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Ethereum wallet",
    description="""
    Update your Ethereum wallet address.
    
    - Validates ETH address format
    - Updates the wallet in your user profile
    """
)
async def update_ethereum_wallet(
    wallet_data: EthWalletBase,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the current user's Ethereum wallet address.
    
    Returns a success message.
    """
    try:
        await link_eth_wallet(db, current_user.id, wallet_data.eth_address)
        return WalletResponse(message="Ethereum wallet updated successfully")
    except AuthError as e:
        # Re-raise as HTTPException with appropriate status code
        raise e


@router.put(
    "/ln",
    response_model=WalletResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Lightning wallet",
    description="""
    Update your Lightning Network wallet address.
    
    - Validates Lightning Network address format
    - Updates the wallet in your user profile
    """
)
async def update_lightning_wallet(
    wallet_data: LnWalletBase,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the current user's Lightning Network wallet address.
    
    Returns a success message.
    """
    try:
        await link_ln_wallet(db, current_user.id, wallet_data.ln_address)
        return WalletResponse(message="Lightning wallet updated successfully")
    except AuthError as e:
        # Re-raise as HTTPException with appropriate status code
        raise e


@router.get(
    "/",
    response_model=UserWallets,
    status_code=status.HTTP_200_OK,
    summary="Get user wallets",
    description="""
    Retrieve your linked wallet addresses.
    
    - Returns ETH and LN wallet addresses if available
    """
)
async def get_user_wallet_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current user's wallet information.
    
    Returns the user's ETH and LN wallet addresses.
    """
    try:
        wallet_info = await get_user_wallets(db, current_user.id)
        return UserWallets(**wallet_info)
    except AuthError as e:
        # Re-raise as HTTPException with appropriate status code
        raise e
