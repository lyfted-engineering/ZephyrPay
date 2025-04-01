from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import settings

# Create SQLAlchemy engines - one for sync and one for async operations
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    echo=settings.DEBUG
)

async_engine = create_async_engine(
    str(settings.ASYNC_SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create sessionmaker for sync and async sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine, 
    class_=AsyncSession
)


async def get_db():
    """
    Dependency for getting an async DB session
    
    This function is intended to be used as a FastAPI dependency to get
    a database session that will be automatically closed when the request is finished.
    """
    async_session = AsyncSessionLocal()
    try:
        yield async_session
    finally:
        await async_session.close()