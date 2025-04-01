import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing import Generator, AsyncGenerator
import os
import jwt

# Override settings before importing app
os.environ["TESTING"] = "True"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "11520"

from backend.app.db.base import Base
from backend.app.core.config import settings

# Override settings for testing
settings.SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///:memory:"
settings.ASYNC_SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite:///:memory:"

# Import app after settings override to ensure test config is used
from backend.app.main import app
from backend.app.db.session import get_db

# Use an in-memory SQLite database for testing
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True,
)

TestingSessionLocal = sessionmaker(
    class_=AsyncSession, autocommit=False, autoflush=False, bind=engine
)


# Create tables once for all tests
@pytest.fixture(scope="session", autouse=True)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to override the get_db dependency during testing"""
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """Create an instance of the default event loop for each test case"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Get a testing database session"""
    async with TestingSessionLocal() as session:
        # Clear data between tests
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"DELETE FROM {table.name}"))
        await session.commit()
        
        yield session


@pytest.fixture(scope="function")
def client(db) -> Generator[TestClient, None, None]:
    """Get a synchronous test client for the FastAPI app with a clean database"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_user(client: TestClient, db: AsyncSession):
    """
    Create a user and return the user_id and authentication token.
    Used for tests that require an authenticated user.
    """
    # Register a test user
    register_data = {
        "email": "authuser@example.com",
        "password": "StrongP@ssw0rd",
        "username": "authuser"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    
    token = response.json()["access_token"]
    
    # Get user ID from token
    payload = jwt.decode(
        token, 
        settings.SECRET_KEY, 
        algorithms=["HS256"]
    )
    user_id = int(payload["sub"])
    
    return user_id, token


@pytest.fixture
def authenticated_user_with_wallets(client: TestClient, authenticated_user):
    """
    Create a user with linked wallets and return user_id, token, and wallet addresses.
    Used for wallet update tests.
    """
    user_id, token = authenticated_user
    
    # Link ETH wallet
    eth_data = {
        "eth_address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
    }
    client.post(
        "/api/v1/wallets/eth",
        json=eth_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Link LN wallet
    ln_data = {
        "ln_address": "lnurl1dp68gurn8ghj7um9wfmxjcm99e3k7mf0v9cxj0m385ekvcenxc6r2c35xvukxefcv5mkvv34x5ekzd3ev56nyd3hxqurzepexejxxepnxscrvwfnv9nz7umn9cejxt5j7jfvy7"
    }
    client.post(
        "/api/v1/wallets/ln",
        json=ln_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    return user_id, token, eth_data["eth_address"], ln_data["ln_address"]
