import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing import Generator, AsyncGenerator
import os

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
