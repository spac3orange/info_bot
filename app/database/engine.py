from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.base import Base

# Default SQLite URL if not set in env
DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./data/bot.db"


def get_async_engine(database_url: str = DEFAULT_DATABASE_URL):
    """Create async engine for aiosqlite."""
    return create_async_engine(
        database_url,
        echo=False,
    )


async_engine = get_async_engine()

async_session_factory = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)
