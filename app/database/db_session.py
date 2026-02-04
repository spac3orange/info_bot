from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import async_session_factory

AsyncSessionLocal = async_session_factory
