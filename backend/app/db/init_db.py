import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import engine, AsyncSessionLocal
from backend.app.db.base import Base
from backend.app.models.user import User
from backend.app.core.security import get_password_hash

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Initialize database with tables and default admin user"""
    try:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create a session
        async with AsyncSessionLocal() as db:
            # Check if admin user exists
            result = await db.execute(
                "SELECT * FROM users WHERE email = 'admin@zephyrpay.com'"
            )
            user = result.fetchone()
            
            # Create admin user if not exists
            if user is None:
                logger.info("Creating admin user")
                admin_user = User(
                    email="admin@zephyrpay.com",
                    username="admin",
                    password_hash=get_password_hash("Admin@ZephyrPay123"),
                    role="ADMIN",
                    is_active=True,
                    is_verified=True
                )
                db.add(admin_user)
                await db.commit()
                logger.info("Admin user created")
            else:
                logger.info("Admin user already exists")
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_db())
