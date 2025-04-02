import pytest
import time
from datetime import datetime, timedelta
from jose import jwt, JWTError
from unittest.mock import patch, MagicMock

from backend.app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    ALGORITHM
)
from backend.app.core.config import settings


class TestSecurity:
    """
    Feature: Core Security Module
    As a developer
    I want to ensure the core security functions are fully tested
    So that the cryptocurrency payment platform is secure
    """
    
    def test_get_password_hash(self):
        """
        Scenario: Password hashing
        Given a plain text password
        When I hash the password
        Then I should get a secure bcrypt hash
        And the hash should not match the original password
        """
        # Arrange
        password = "SecurePassword123"
        
        # Act
        hashed = get_password_hash(password)
        
        # Assert
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt hash prefix
        assert len(hashed) > 50  # Reasonable bcrypt hash length

    def test_verify_password_success(self):
        """
        Scenario: Password verification - success
        Given a password and its correct hash
        When I verify the password
        Then the verification should succeed
        """
        # Arrange
        password = "SecurePassword123"
        hashed = get_password_hash(password)
        
        # Act
        result = verify_password(password, hashed)
        
        # Assert
        assert result is True

    def test_verify_password_failure(self):
        """
        Scenario: Password verification - failure
        Given a password and an incorrect hash
        When I verify the password
        Then the verification should fail
        """
        # Arrange
        password = "SecurePassword123"
        wrong_password = "WrongPassword456"
        hashed = get_password_hash(password)
        
        # Act
        result = verify_password(wrong_password, hashed)
        
        # Assert
        assert result is False

    def test_create_access_token_default_expiry(self):
        """
        Scenario: Create JWT token with default expiry
        Given a user ID and role
        When I create an access token without custom expiry
        Then the token should be a valid JWT with correct fields
        """
        # Arrange
        user_id = 123
        role = "ADMIN"
        
        # Act
        token = create_access_token(subject=user_id, role=role)
        
        # Assert
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_exp": False}  # Disable expiration verification
        )
        
        # Verify essential fields
        assert payload["sub"] == str(user_id)
        assert payload["role"] == role
        
        # Verify expiry field exists and is in the future
        assert "exp" in payload
        assert payload["exp"] > int(time.time())
        
        # Verify issued-at timestamp exists
        assert "iat" in payload
        
        # Expiry should be approximately ACCESS_TOKEN_EXPIRE_MINUTES from issued-at
        # with some flexibility for test execution time
        assert abs(payload["exp"] - payload["iat"] - (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)) < 10

    def test_create_access_token_custom_expiry(self):
        """
        Scenario: Create JWT token with custom expiry
        Given a user ID, role and custom expiry time
        When I create an access token with custom expiry
        Then the token should be a valid JWT with correct fields
        """
        # Arrange
        user_id = 123
        role = "MEMBER"
        custom_expiry = timedelta(hours=1)
        
        # Act
        token = create_access_token(
            subject=user_id, 
            role=role,
            expires_delta=custom_expiry
        )
        
        # Assert
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_exp": False}  # Disable expiration verification
        )
        
        # Verify essential fields
        assert payload["sub"] == str(user_id)
        assert payload["role"] == role
        
        # Verify expiry field exists and is in the future
        assert "exp" in payload
        assert payload["exp"] > int(time.time())
        
        # Verify issued-at timestamp exists
        assert "iat" in payload
        
        # Expiry should be approximately custom_expiry from issued-at
        # with some flexibility for test execution time
        assert abs(payload["exp"] - payload["iat"] - (3600)) < 10  # 1 hour in seconds

    def test_create_access_token_with_different_roles(self):
        """
        Scenario: Create JWT tokens with different roles
        Given different user roles
        When I create access tokens for each role
        Then each token should contain the correct role in payload
        """
        # Arrange
        user_id = 123
        roles = ["ADMIN", "OPERATOR", "MEMBER"]
        
        for role in roles:
            # Act
            token = create_access_token(subject=user_id, role=role)
            
            # Assert
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[ALGORITHM],
                options={"verify_exp": False}  # Disable expiration verification
            )
            
            assert payload["sub"] == str(user_id)
            assert payload["role"] == role

    def test_token_validation_failure(self):
        """
        Scenario: JWT validation failure
        Given a valid token and an incorrect key
        When I attempt to decode the token with the wrong key
        Then the validation should fail
        """
        # Arrange
        user_id = 123
        role = "ADMIN"
        token = create_access_token(subject=user_id, role=role)
        wrong_key = "wrong_secret_key"
        
        # Act & Assert
        with pytest.raises(JWTError):
            jwt.decode(
                token, 
                wrong_key, 
                algorithms=[ALGORITHM],
                options={"verify_exp": False}  # Disable expiration verification
            )

    def test_issued_at_timestamp(self):
        """
        Scenario: JWT token includes issued at timestamp
        Given a token creation request
        When the token is created
        Then the token should include an 'iat' claim with current time
        """
        # Arrange - get current timestamp for comparison
        now = int(time.time())
        
        # Act
        token = create_access_token(subject=123, role="MEMBER")
        
        # Assert
        payload = jwt.decode(
            token,
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_exp": False}  # Disable expiration verification
        )
        
        # Verify the issued-at timestamp exists and is close to current time
        assert "iat" in payload
        # Allow a 10-second window for test execution
        assert abs(payload["iat"] - now) < 10
