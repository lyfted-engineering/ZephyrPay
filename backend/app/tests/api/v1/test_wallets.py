import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User


class TestWalletLinking:
    """
    Feature: Link ETH & LN Wallets
    As a user
    I want to link my Ethereum and Lightning wallets
    So that I can use crypto features
    """
    
    def test_link_eth_wallet(self, client: TestClient, authenticated_user):
        """
        Scenario: Link Ethereum wallet
        Given I am a logged in user
        When I link my Ethereum wallet
        Then the system should store my wallet address
        And return a success message
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
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
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        assert response.json()["message"] == "Ethereum wallet linked successfully"
        
        # Check if wallet was actually stored
        user_response = client.get(
            "/api/v1/users/me", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert user_response.json()["eth_address"] == eth_data["eth_address"]
    
    def test_link_ln_wallet(self, client: TestClient, authenticated_user):
        """
        Scenario: Link Lightning Network wallet
        Given I am a logged in user
        When I link my Lightning Network wallet
        Then the system should store my wallet key
        And return a success message
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
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
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        assert response.json()["message"] == "Lightning wallet linked successfully"
        
        # Check if wallet was actually stored
        user_response = client.get(
            "/api/v1/users/me", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert user_response.json()["ln_address"] == ln_data["ln_address"]
    
    def test_link_invalid_eth_wallet(self, client: TestClient, authenticated_user):
        """
        Scenario: Link invalid Ethereum wallet
        Given I am a logged in user
        When I submit an invalid Ethereum address
        Then the system should reject it
        And return a validation error
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Act - Link invalid ETH wallet
        eth_data = {
            "eth_address": "invalid-eth-address"
        }
        response = client.post(
            "/api/v1/wallets/eth",
            json=eth_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
    def test_link_invalid_ln_wallet(self, client: TestClient, authenticated_user):
        """
        Scenario: Link invalid Lightning wallet
        Given I am a logged in user
        When I submit an invalid Lightning address
        Then the system should reject it
        And return a validation error
        """
        # Arrange - We use the authenticated_user fixture
        user_id, token = authenticated_user
        
        # Act - Link invalid LN wallet
        ln_data = {
            "ln_address": "invalid-ln-address"
        }
        response = client.post(
            "/api/v1/wallets/ln",
            json=ln_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
    def test_update_eth_wallet(self, client: TestClient, authenticated_user_with_wallets):
        """
        Scenario: Update Ethereum wallet
        Given I am a logged in user with a linked wallet
        When I update my Ethereum wallet address
        Then the system should update my wallet address
        And return a success message
        """
        # Arrange - We use the authenticated_user_with_wallets fixture
        user_id, token, eth_address, ln_address = authenticated_user_with_wallets
        
        # Act - Update ETH wallet
        new_eth_data = {
            "eth_address": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B"
        }
        response = client.put(
            "/api/v1/wallets/eth",
            json=new_eth_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        
        # Check if wallet was actually updated
        user_response = client.get(
            "/api/v1/users/me", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert user_response.json()["eth_address"] == new_eth_data["eth_address"]
        
    def test_update_ln_wallet(self, client: TestClient, authenticated_user_with_wallets):
        """
        Scenario: Update Lightning Network wallet
        Given I am a logged in user with a linked wallet
        When I update my Lightning Network wallet key
        Then the system should update my wallet key
        And return a success message
        """
        # Arrange - We use the authenticated_user_with_wallets fixture
        user_id, token, eth_address, ln_address = authenticated_user_with_wallets
        
        # Act - Update LN wallet
        new_ln_data = {
            "ln_address": "lnurl1dp68gurn8ghj7ur5v93kketjv9ejx2enxvunsdpz7urp09akxuemvde6hyun9e3k7mf0w36x2cn9vc6j2umnd9jhxctrde3jxvexxcmzxc3jxtnrvvekxumrww5j7jfvy7"
        }
        response = client.put(
            "/api/v1/wallets/ln",
            json=new_ln_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
        
        # Check if wallet was actually updated
        user_response = client.get(
            "/api/v1/users/me", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert user_response.json()["ln_address"] == new_ln_data["ln_address"]
