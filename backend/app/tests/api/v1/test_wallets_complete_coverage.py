import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.core.errors import AuthError
from backend.app.api.v1.endpoints.wallets import (
    link_ethereum_wallet,
    link_lightning_wallet,
    update_ethereum_wallet,
    update_lightning_wallet,
    get_user_wallet_info
)
from backend.app.schemas.wallet import (
    EthWalletBase, 
    LnWalletBase, 
    WalletResponse, 
    UserWallets
)


class TestWalletEndpoints:
    """
    Feature: Wallet Endpoint Test Coverage
    As a developer
    I want to ensure all wallet endpoints are fully tested
    So that the financial security of the system is maintained
    """
    
    @pytest.mark.asyncio
    async def test_link_ethereum_wallet_success(self, client: TestClient, authenticated_user, db: AsyncSession):
        """
        Scenario: Successfully link ETH wallet
        Given I am a logged in user
        When I link my Ethereum wallet with a valid address
        Then the system should store my wallet address
        And return a success message
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Create a mock for the service function
        with patch('backend.app.api.v1.endpoints.wallets.link_eth_wallet', new_callable=AsyncMock) as mock_link:
            # Set up mock to return success
            mock_link.return_value = True
            
            # Act - Link ETH wallet
            eth_data = {
                "eth_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
            }
            response = client.post(
                "/api/v1/wallets/eth",
                json=eth_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Assert - Response
            assert response.status_code == status.HTTP_200_OK
            assert "message" in response.json()
            assert response.json()["message"] == "Ethereum wallet linked successfully"
            
            # Assert - Mock called
            mock_link.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_link_ethereum_wallet_error(self, client: TestClient, authenticated_user, db: AsyncSession):
        """
        Scenario: Error linking ETH wallet
        Given I am a logged in user
        When the system encounters an error linking my wallet
        Then the appropriate error should be returned
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Create a mock for the service function
        with patch('backend.app.api.v1.endpoints.wallets.link_eth_wallet', new_callable=AsyncMock) as mock_link:
            # Set up mock to raise an error
            mock_link.side_effect = AuthError(message="Test error", status_code=400)
            
            # Act - Link ETH wallet
            eth_data = {
                "eth_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
            }
            response = client.post(
                "/api/v1/wallets/eth",
                json=eth_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Assert
            assert response.status_code == 400
            assert "detail" in response.json()
            assert response.json()["detail"] == "Test error"
    
    @pytest.mark.asyncio
    async def test_link_lightning_wallet_success(self, client: TestClient, authenticated_user, db: AsyncSession):
        """
        Scenario: Successfully link LN wallet
        Given I am a logged in user
        When I link my Lightning wallet with a valid address
        Then the system should store my wallet address
        And return a success message
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Create a mock for the service function
        with patch('backend.app.api.v1.endpoints.wallets.link_ln_wallet', new_callable=AsyncMock) as mock_link:
            # Set up mock to return success
            mock_link.return_value = True
            
            # Act - Link LN wallet
            ln_data = {
                "ln_address": "lnurl1dp68gurn8ghj7um9wfmxjcm99e3k7mf0v9cxj0m385ekvcenxc6r2c35xvukxefcv5mkvv34x5ekzd3ev56nyd3hxqurzepexejxxepnxscrvwfnv9nz7umn9cejxt5j7jfvy7"
            }
            response = client.post(
                "/api/v1/wallets/ln",
                json=ln_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Assert - Response
            assert response.status_code == status.HTTP_200_OK
            assert "message" in response.json()
            assert response.json()["message"] == "Lightning wallet linked successfully"
            
            # Assert - Mock called
            mock_link.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_link_lightning_wallet_error(self, client: TestClient, authenticated_user, db: AsyncSession):
        """
        Scenario: Error linking LN wallet
        Given I am a logged in user
        When the system encounters an error linking my wallet
        Then the appropriate error should be returned
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Create a mock for the service function
        with patch('backend.app.api.v1.endpoints.wallets.link_ln_wallet', new_callable=AsyncMock) as mock_link:
            # Set up mock to raise an error
            mock_link.side_effect = AuthError(message="Test error", status_code=400)
            
            # Act - Link LN wallet
            ln_data = {
                "ln_address": "lnurl1dp68gurn8ghj7um9wfmxjcm99e3k7mf0v9cxj0m385ekvcenxc6r2c35xvukxefcv5mkvv34x5ekzd3ev56nyd3hxqurzepexejxxepnxscrvwfnv9nz7umn9cejxt5j7jfvy7"
            }
            response = client.post(
                "/api/v1/wallets/ln",
                json=ln_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Assert
            assert response.status_code == 400
            assert "detail" in response.json()
            assert response.json()["detail"] == "Test error"
    
    @pytest.mark.asyncio
    async def test_update_ethereum_wallet_success(self, client: TestClient, authenticated_user, db: AsyncSession):
        """
        Scenario: Successfully update ETH wallet
        Given I am a logged in user
        When I update my Ethereum wallet with a valid address
        Then the system should update my wallet address
        And return a success message
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Create a mock for the service function
        with patch('backend.app.api.v1.endpoints.wallets.link_eth_wallet', new_callable=AsyncMock) as mock_update:
            # Set up mock to return success
            mock_update.return_value = True
            
            # Act - Update ETH wallet
            eth_data = {
                "eth_address": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
            }
            response = client.put(
                "/api/v1/wallets/eth",
                json=eth_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Assert - Response
            assert response.status_code == status.HTTP_200_OK
            assert "message" in response.json()
            assert response.json()["message"] == "Ethereum wallet updated successfully"
            
            # Assert - Mock called
            mock_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_ethereum_wallet_error(self, client: TestClient, authenticated_user, db: AsyncSession):
        """
        Scenario: Error updating ETH wallet
        Given I am a logged in user
        When the system encounters an error updating my wallet
        Then the appropriate error should be returned
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Create a mock for the service function
        with patch('backend.app.api.v1.endpoints.wallets.link_eth_wallet', new_callable=AsyncMock) as mock_update:
            # Set up mock to raise an error
            mock_update.side_effect = AuthError(message="Update error", status_code=400)
            
            # Act - Update ETH wallet
            eth_data = {
                "eth_address": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
            }
            response = client.put(
                "/api/v1/wallets/eth",
                json=eth_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Assert
            assert response.status_code == 400
            assert "detail" in response.json()
            assert response.json()["detail"] == "Update error"
    
    @pytest.mark.asyncio
    async def test_update_lightning_wallet_success(self, client: TestClient, authenticated_user, db: AsyncSession):
        """
        Scenario: Successfully update LN wallet
        Given I am a logged in user
        When I update my Lightning wallet with a valid address
        Then the system should update my wallet address
        And return a success message
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Create a mock for the service function
        with patch('backend.app.api.v1.endpoints.wallets.link_ln_wallet', new_callable=AsyncMock) as mock_update:
            # Set up mock to return success
            mock_update.return_value = True
            
            # Act - Update LN wallet
            ln_data = {
                "ln_address": "lnurl1dp68gurn8ghj7ur5v93kketjv9ejx2enxvunsdpz7urp09akxuemvde6hyun9e3k7mf0w36x2cn9vc6j2umnd9jhxctrde3jxvexxcmzxc3jxtnrvvekxumrww5j7jfvy7"
            }
            response = client.put(
                "/api/v1/wallets/ln",
                json=ln_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Assert - Response
            assert response.status_code == status.HTTP_200_OK
            assert "message" in response.json()
            assert response.json()["message"] == "Lightning wallet updated successfully"
            
            # Assert - Mock called
            mock_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_lightning_wallet_error(self, client: TestClient, authenticated_user, db: AsyncSession):
        """
        Scenario: Error updating LN wallet
        Given I am a logged in user
        When the system encounters an error updating my wallet
        Then the appropriate error should be returned
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Create a mock for the service function
        with patch('backend.app.api.v1.endpoints.wallets.link_ln_wallet', new_callable=AsyncMock) as mock_update:
            # Set up mock to raise an error
            mock_update.side_effect = AuthError(message="Update error", status_code=400)
            
            # Act - Update LN wallet
            ln_data = {
                "ln_address": "lnurl1dp68gurn8ghj7ur5v93kketjv9ejx2enxvunsdpz7urp09akxuemvde6hyun9e3k7mf0w36x2cn9vc6j2umnd9jhxctrde3jxvexxcmzxc3jxtnrvvekxumrww5j7jfvy7"
            }
            response = client.put(
                "/api/v1/wallets/ln",
                json=ln_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Assert
            assert response.status_code == 400
            assert "detail" in response.json()
            assert response.json()["detail"] == "Update error"
    
    @pytest.mark.asyncio
    async def test_get_user_wallet_info_success(self, client: TestClient, authenticated_user, db: AsyncSession):
        """
        Scenario: Successfully retrieve wallet info
        Given I am a logged in user
        When I request my wallet information
        Then the system should return my wallet addresses
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Create a mock for the service function
        with patch('backend.app.api.v1.endpoints.wallets.get_user_wallets', new_callable=AsyncMock) as mock_get:
            # Set up mock to return wallet info
            mock_get.return_value = {
                "eth_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "ln_address": "lnurl1dp68gurn8ghj7um9wfmxjcm99e3k7mf0v9cxj0m385ekvcenxc6r2c35xvukxefcv5mkvv34x5ekzd3ev56nyd3hxqurzepexejxxepnxscrvwfnv9nz7umn9cejxt5j7jfvy7"
            }
            
            # Act - Get wallet info
            response = client.get(
                "/api/v1/wallets/",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Assert - Response
            assert response.status_code == status.HTTP_200_OK
            assert "eth_address" in response.json()
            assert "ln_address" in response.json()
            
            # Assert - Mock called
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_wallet_info_error(self, client: TestClient, authenticated_user, db: AsyncSession):
        """
        Scenario: Error retrieving wallet info
        Given I am a logged in user
        When the system encounters an error retrieving my wallet info
        Then the appropriate error should be returned
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Create a mock for the service function
        with patch('backend.app.api.v1.endpoints.wallets.get_user_wallets', new_callable=AsyncMock) as mock_get:
            # Set up mock to raise an error
            mock_get.side_effect = AuthError(message="Retrieval error", status_code=400)
            
            # Act - Get wallet info
            response = client.get(
                "/api/v1/wallets/",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Assert
            assert response.status_code == 400
            assert "detail" in response.json()
            assert response.json()["detail"] == "Retrieval error"
    
    @pytest.mark.asyncio
    async def test_direct_endpoint_calls(self, db: AsyncSession):
        """
        Scenario: Direct endpoint function coverage
        When endpoint functions are called directly
        Then they should handle the requests correctly
        """
        # Create a mock user
        mock_user = User(id=1, email="test@example.com", username="testuser")
        
        # Test link_ethereum_wallet endpoint function
        with patch('backend.app.api.v1.endpoints.wallets.link_eth_wallet', new_callable=AsyncMock) as mock_link_eth:
            mock_link_eth.return_value = True
            wallet_data = EthWalletBase(eth_address="0x71C7656EC7ab88b098defB751B7401B5f6d8976F")
            result = await link_ethereum_wallet(wallet_data, mock_user, db)
            assert isinstance(result, WalletResponse)
            assert result.message == "Ethereum wallet linked successfully"
        
        # Test link_lightning_wallet endpoint function
        with patch('backend.app.api.v1.endpoints.wallets.link_ln_wallet', new_callable=AsyncMock) as mock_link_ln:
            mock_link_ln.return_value = True
            wallet_data = LnWalletBase(ln_address="lnurl1dp68gurn8ghj7um9wfmxjcm99e3k7mf0v9cxj0m385ekvcenxc6r2c35xvukxefcv5mkvv34x5ekzd3ev56nyd3hxqurzepexejxxepnxscrvwfnv9nz7umn9cejxt5j7jfvy7")
            result = await link_lightning_wallet(wallet_data, mock_user, db)
            assert isinstance(result, WalletResponse)
            assert result.message == "Lightning wallet linked successfully"
        
        # Test update_ethereum_wallet endpoint function
        with patch('backend.app.api.v1.endpoints.wallets.link_eth_wallet', new_callable=AsyncMock) as mock_upd_eth:
            mock_upd_eth.return_value = True
            wallet_data = EthWalletBase(eth_address="0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B")
            result = await update_ethereum_wallet(wallet_data, mock_user, db)
            assert isinstance(result, WalletResponse)
            assert result.message == "Ethereum wallet updated successfully"
        
        # Test update_lightning_wallet endpoint function
        with patch('backend.app.api.v1.endpoints.wallets.link_ln_wallet', new_callable=AsyncMock) as mock_upd_ln:
            mock_upd_ln.return_value = True
            wallet_data = LnWalletBase(ln_address="lnurl1dp68gurn8ghj7ur5v93kketjv9ejx2enxvunsdpz7urp09akxuemvde6hyun9e3k7mf0w36x2cn9vc6j2umnd9jhxctrde3jxvexxcmzxc3jxtnrvvekxumrww5j7jfvy7")
            result = await update_lightning_wallet(wallet_data, mock_user, db)
            assert isinstance(result, WalletResponse)
            assert result.message == "Lightning wallet updated successfully"
        
        # Test get_user_wallet_info endpoint function
        with patch('backend.app.api.v1.endpoints.wallets.get_user_wallets', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                "eth_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
                "ln_address": "lnurl1dp68gurn8ghj7um9wfmxjcm99e3k7mf0v9cxj0m385ekvcenxc6r2c35xvukxefcv5mkvv34x5ekzd3ev56nyd3hxqurzepexejxxepnxscrvwfnv9nz7umn9cejxt5j7jfvy7"
            }
            result = await get_user_wallet_info(mock_user, db)
            assert isinstance(result, UserWallets)
            assert result.eth_address == "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
