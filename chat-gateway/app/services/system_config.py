"""Allowed system_ids and Dify config from DB (chat_systems). Loaded on startup. Fallback to env."""
from __future__ import annotations

import logging

from sqlalchemy import text

from app.config import get_settings
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Cache: list of dicts with system_id, dify_base_url, dify_api_key
_systems_cache: list[dict] = []


def _get_system(system_id: str | None) -> dict | None:
    if not system_id:
        return None
    sid = system_id.lower().strip()
    for s in _systems_cache:
        if s["system_id"].lower() == sid:
            return s
    return None


async def refresh_allowed_systems() -> None:
    """Load enabled systems (system_id, dify_base_url, dify_api_key) from chat_systems. Called on startup."""
    global _systems_cache
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text(
                    "SELECT system_id, dify_base_url, dify_api_key FROM chat_systems WHERE enabled"
                )
            )
            rows = result.fetchall()
            _systems_cache = [
                {
                    "system_id": (r[0] or "").strip().lower(),
                    "dify_base_url": (r[1] or "").strip().rstrip("/"),
                    "dify_api_key": (r[2] or "").strip(),
                }
                for r in rows
                if r[0]
            ]
            ids = [s["system_id"] for s in _systems_cache]
            logger.info("Loaded systems from DB: %s", ids)
    except Exception as e:
        logger.warning("Could not load chat_systems from DB: %s. Using env fallback.", e)
        _systems_cache = []


def get_allowed_system_ids_list() -> list[str]:
    """Allowed system_ids. DB first, then env (ALLOWED_SYSTEM_IDS) fallback. Empty = allow all."""
    if _systems_cache:
        return [s["system_id"] for s in _systems_cache if s["system_id"]]
    return get_settings().allowed_system_ids_list


def get_dify_base_url(system_id: str | None) -> str:
    """Dify base URL for system. DB first, then env fallback."""
    s = _get_system(system_id)
    if s and s.get("dify_base_url"):
        return s["dify_base_url"]
    return (get_settings().get_dify_base_url(system_id) or "").strip().rstrip("/")


def get_dify_api_key(system_id: str | None) -> str:
    """Dify API key for system. DB first, then env fallback."""
    s = _get_system(system_id)
    if s and s.get("dify_api_key"):
        return s["dify_api_key"]
    return (get_settings().get_dify_api_key(system_id) or "").strip()
