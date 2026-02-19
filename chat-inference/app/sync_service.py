"""Sync: register users, record chat to DB. No Dify sync (standalone)."""
import logging
import uuid
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import ConversationCache, ConversationMapping, MessageCache, SyncUser

logger = logging.getLogger("chat_inference")


def _upsert_insert(table):
    url = get_settings().effective_database_url
    if "postgresql" in url:
        from sqlalchemy.dialects.postgresql import insert
        return insert(table)
    from sqlalchemy.dialects.sqlite import insert
    return insert(table)


async def _upsert_message(
    db: AsyncSession,
    conversation_id: str,
    message_id: str,
    role: str,
    content: str,
    created_at: datetime | None,
) -> None:
    stmt = _upsert_insert(MessageCache).values(
        conversation_id=conversation_id,
        message_id=message_id,
        role=role,
        content=content,
        created_at=created_at,
        synced_at=datetime.utcnow(),
    ).on_conflict_do_update(
        index_elements=["message_id"],
        set_={"content": content, "created_at": created_at, "synced_at": datetime.utcnow()},
    )
    await db.execute(stmt)


async def record_chat_to_db(
    db: AsyncSession,
    system_id: str,
    user_id: str,
    dify_user: str,
    conversation_id: str,
    message_id: str | None,
    user_query: str,
    assistant_answer: str,
) -> None:
    """Record one chat to DB right after pipeline response."""
    now = datetime.utcnow()
    stmt = _upsert_insert(ConversationCache).values(
        system_id=system_id,
        user_id=user_id,
        dify_user=dify_user,
        conversation_id=conversation_id,
        name=None,
        created_at=now,
        synced_at=now,
    ).on_conflict_do_update(
        index_elements=["conversation_id"],
        set_={"synced_at": now},
    )
    await db.execute(stmt)
    mid = message_id or f"local-{uuid.uuid4().hex[:12]}"
    await _upsert_message(db, conversation_id, f"{mid}_user", "user", user_query or "", now)
    await _upsert_message(db, conversation_id, f"{mid}_assistant", "assistant", assistant_answer or "", now)


async def register_sync_user(
    db: AsyncSession,
    system_id: str,
    user_id: str,
    dify_user: str,
) -> None:
    stmt = _upsert_insert(SyncUser).values(
        system_id=system_id,
        user_id=user_id,
        dify_user=dify_user,
        updated_at=datetime.utcnow(),
    ).on_conflict_do_update(
        index_elements=["system_id", "user_id"],
        set_={"dify_user": dify_user, "updated_at": datetime.utcnow()},
    )
    await db.execute(stmt)
