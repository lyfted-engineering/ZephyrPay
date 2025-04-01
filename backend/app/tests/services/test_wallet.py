import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.user import User
from backend.app.services.wallet import link_eth_wallet, link_ln_wallet, get_user_wallets
from backend.app.core.errors import AuthError


class TestWalletService:
    """Tests for the wallet service functions"""
    
    async def test_link_eth_wallet_success(self, db: AsyncSession):
        """
        Test successful linking of an Ethereum wallet
        """
        # Arrange - Create a test user
        test_user = User(
            email="ethuser@example.com",
            username="ethuser",
            password_hash="hashed_password",
            role="MEMBER"
        )
        db.add(test_user)
        await db.commit()
        await db.refresh(test_user)
        
        eth_address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
        
        # Act - Link ETH wallet
        result = await link_eth_wallet(db, test_user.id, eth_address)
        
        # Assert
        assert result is True
        
        # Verify address was saved
        stmt = select(User).where(User.id == test_user.id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        assert user.eth_address == eth_address
    
    async def test_link_ln_wallet_success(self, db: AsyncSession):
        """
        Test successful linking of a Lightning Network wallet
        """
        # Arrange - Create a test user
        test_user = User(
            email="lnuser@example.com",
            username="lnuser",
            password_hash="hashed_password",
            role="MEMBER"
        )
        db.add(test_user)
        await db.commit()
        await db.refresh(test_user)
        
        ln_address = "lnurl1dp68gurn8ghj7um9wfmxjcm99e3k7mf0v9cxj0m385ekvcenxc6r2c35xvukxefcv5"
        
        # Act - Link LN wallet
        result = await link_ln_wallet(db, test_user.id, ln_address)
        
        # Assert
        assert result is True
        
        # Verify address was saved
        stmt = select(User).where(User.id == test_user.id)
        result = await db.execute(stmt)
        user = result.scalars().first()
        assert user.ln_address == ln_address
    
    async def test_get_user_wallets(self, db: AsyncSession):
        """
        Test retrieving user wallet information
        """
        # Arrange - Create a test user with wallets
        eth_address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
        ln_address = "lnurl1dp68gurn8ghj7um9wfmxjcm99e3k7mf0v9cxj0m385ekvcenxc6r2c35xvukxefcv5"
        
        test_user = User(
            email="walletuser@example.com",
            username="walletuser",
            password_hash="hashed_password",
            role="MEMBER",
            eth_address=eth_address,
            ln_address=ln_address
        )
        db.add(test_user)
        await db.commit()
        await db.refresh(test_user)
        
        # Act - Get wallet info
        wallet_info = await get_user_wallets(db, test_user.id)
        
        # Assert
        assert wallet_info["eth_address"] == eth_address
        assert wallet_info["ln_address"] == ln_address
    
    async def test_link_eth_wallet_nonexistent_user(self, db: AsyncSession):
        """
        Test linking an Ethereum wallet to a non-existent user
        """
        # Act & Assert - Try to link wallet to non-existent user
        with pytest.raises(AuthError):
            await link_eth_wallet(db, 9999, "0x71C7656EC7ab88b098defB751B7401B5f6d8976F")
    
    async def test_link_ln_wallet_nonexistent_user(self, db: AsyncSession):
        """
        Test linking a Lightning Network wallet to a non-existent user
        """
        # Act & Assert - Try to link wallet to non-existent user
        with pytest.raises(AuthError):
            await link_ln_wallet(db, 9999, "lnurl1dp68gurn8ghj7um9wfmxjcm99e3k7mf0v9cxj0m385")
    
    async def test_get_user_wallets_nonexistent_user(self, db: AsyncSession):
        """
        Test retrieving wallet information for a non-existent user
        """
        # Act & Assert - Try to get wallet info for non-existent user
        with pytest.raises(AuthError):
            await get_user_wallets(db, 9999)
