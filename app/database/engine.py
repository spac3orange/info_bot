import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.base import Base

# Default SQLite URL if not set in env
DEFAULT_DATABASE_URL = "sqlite+aiosqlite:////app/data/bot.db"


def get_async_engine() -> "create_async_engine":
    """Create async engine for aiosqlite using DATABASE_URL from env or default."""
    database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    return create_async_engine(
        database_url,
        echo=False,
    )


async_engine = get_async_engine()

async_session_factory = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)
