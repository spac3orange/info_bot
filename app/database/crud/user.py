from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None = None,
    deep_link: str | None = None,
) -> User:
    """Get user by telegram_id or create with username, created_at and optional deep_link."""
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is not None:
        if username is not None and user.username != username:
            user.username = username
            await session.commit()
            await session.refresh(user)
        return user
    user = User(telegram_id=telegram_id, username=username, deep_link=deep_link)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_all_telegram_ids(session: AsyncSession) -> list[int]:
    """Return list of all user telegram_ids for broadcast."""
    result = await session.execute(select(User.telegram_id))
    return list(result.scalars().all())


async def get_users_count(session: AsyncSession) -> int:
    """Return total number of users in DB."""
    result = await session.execute(select(func.count()).select_from(User))
    return result.scalar() or 0


async def get_all_users(session: AsyncSession) -> list[User]:
    """Return all users (telegram_id, username, created_at, deep_link) ordered by id."""
    result = await session.execute(select(User).order_by(User.id))
    return list(result.scalars().unique().all())


async def get_users_count_by_deep_link(session: AsyncSession) -> list[tuple[str | None, int]]:
    """Return list of (deep_link, count) for admin stats. None = без ссылки."""
    result = await session.execute(
        select(User.deep_link, func.count(User.id)).select_from(User).group_by(User.deep_link)
    )
    return [(row[0], row[1]) for row in result.all()]
