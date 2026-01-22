from sqlmodel import Session, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from sqlalchemy.ext.asyncio import create_async_engine
import os

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_dev.db")

# Create engines based on URL type
if DATABASE_URL.startswith("sqlite"):
    # For SQLite, convert to aiosqlite format
    if "aiosqlite" not in DATABASE_URL:
        # Convert sqlite:///path to sqlite+aiosqlite:///path
        sqlite_path = DATABASE_URL.split("sqlite:///")[1]  # Get the path part after sqlite:///
        ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///./{sqlite_path}"
    else:
        ASYNC_DATABASE_URL = DATABASE_URL
    async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
elif DATABASE_URL.startswith("postgresql://"):
    # Convert postgresql:// to postgresql+asyncpg:// for async support
    # Also convert sslmode=require to asyncpg-compatible format
    url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    url = url.replace("?sslmode=require", "?ssl=require")
    url = url.replace("&sslmode=require", "&ssl=require")
    ASYNC_DATABASE_URL = url
    async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
else:
    # For other databases, use async engine directly
    async_engine = create_async_engine(DATABASE_URL, echo=True)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session for FastAPI."""
    async with AsyncSession(async_engine) as session:
        yield session

async def init_db():
    """Initialize the database by creating all tables."""
    from sqlmodel import SQLModel
    # Import all models so SQLModel knows about them
    from src.models.task import Task, User  # noqa: F401
    from src.models.conversation import Conversation  # noqa: F401
    from src.models.message import Message  # noqa: F401
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)