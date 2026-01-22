"""
Database initialization script.
Creates all tables based on SQLModel definitions.
"""
import asyncio
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

# Import all models so SQLModel knows about them
from src.models.task import Task, User  # noqa: F401

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_dev.db")

# Convert to async-compatible database URL
if DATABASE_URL.startswith("sqlite") and "aiosqlite" not in DATABASE_URL:
    # Convert sqlite:///path to sqlite+aiosqlite:///path
    sqlite_path = DATABASE_URL.split("sqlite:///")[1]
    # Remove leading ./ if present to avoid double ./ in path
    if sqlite_path.startswith("./"):
        sqlite_path = sqlite_path[2:]
    ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///./{sqlite_path}"
elif DATABASE_URL.startswith("postgresql://"):
    # Convert postgresql:// to postgresql+asyncpg:// for async support
    # Also convert sslmode=require to asyncpg-compatible format
    url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    # asyncpg uses 'ssl' instead of 'sslmode', and requires different format
    url = url.replace("?sslmode=require", "?ssl=require")
    url = url.replace("&sslmode=require", "&ssl=require")
    ASYNC_DATABASE_URL = url
else:
    ASYNC_DATABASE_URL = DATABASE_URL

async def init_db():
    """Initialize the database by creating all tables."""
    engine = create_async_engine(ASYNC_DATABASE_URL)

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)

    logger.info("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())