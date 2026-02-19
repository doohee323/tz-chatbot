from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()
engine = create_async_engine(
    settings.effective_database_url,
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def _migrate_admin_users(sync_conn):
    """Add name, email to admin_users if missing (for existing DBs)."""
    from sqlalchemy import text
    try:
        sync_conn.execute(text("ALTER TABLE admin_users ADD COLUMN name VARCHAR(128) DEFAULT ''"))
    except Exception:
        pass
    try:
        sync_conn.execute(text("ALTER TABLE admin_users ADD COLUMN email VARCHAR(256) DEFAULT ''"))
    except Exception:
        pass


def _run_one_alter(sync_conn, stmt):
    from sqlalchemy import text
    sync_conn.execute(text(stmt))


async def _migrate_chat_systems_separate():
    """Add columns to chat_systems in separate transactions so one failure doesn't abort the rest."""
    import logging
    log = logging.getLogger("chat_admin.migrate")
    steps = [
        ("dify_chatbot_token", "ALTER TABLE chat_systems ADD COLUMN IF NOT EXISTS dify_chatbot_token VARCHAR(128) DEFAULT ''"),
        ("created_by", "ALTER TABLE chat_systems ADD COLUMN IF NOT EXISTS created_by VARCHAR(64)"),
        ("chat_api_url", "ALTER TABLE chat_systems ADD COLUMN IF NOT EXISTS chat_api_url VARCHAR(512) DEFAULT ''"),
    ]
    for name, stmt in steps:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(lambda c: _run_one_alter(c, stmt))
        except Exception as e:
            log.warning("Migration step skipped (may already be applied): chat_systems.%s: %s", name, e)


async def init_db():
    import app.models  # noqa: F401 - register models with Base.metadata before create_all
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_admin_users)
    await _migrate_chat_systems_separate()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
