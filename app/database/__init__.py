from sqlalchemy import text

from app.database.base import Base
from app.database.db_session import AsyncSessionLocal
from app.database.engine import async_engine
from app.database import models  # noqa: F401 - register models with Base


async def init_db() -> None:
    """Create all tables and run migrations. Call once at startup."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(
                text("ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT (datetime('now'))")
            )
        except Exception:
            pass
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN deep_link VARCHAR(255)"))
        except Exception:
            pass
    # SQLite auto-increments only INTEGER PRIMARY KEY. Recreate users if schema is wrong.
    async with async_engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(users)"))
        rows = result.fetchall()
    need_recreate = True
    if rows:
        # (cid, name, type, notnull, dflt_value, pk); id is first column
        id_type = (rows[0][2] or "").strip().lower()
        if id_type == "integer":
            need_recreate = False
    if need_recreate:
        async with async_engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS users"))
            await conn.run_sync(
                lambda sync_conn: Base.metadata.tables["users"].create(sync_conn)
            )
