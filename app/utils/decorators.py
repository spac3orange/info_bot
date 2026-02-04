from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_session import AsyncSessionLocal

T = TypeVar("T")


def with_session(
    func: Callable[..., Awaitable[T]],
) -> Callable[..., Awaitable[T]]:
    """Decorator that injects AsyncSession and closes it after the function call."""

    @wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        async with AsyncSessionLocal() as session:
            return await func(*args, session=session, **kwargs)

    return wrapper
