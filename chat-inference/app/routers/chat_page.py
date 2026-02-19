import logging

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import decode_jwt
from app.database import get_db
from app.sync_service import register_sync_user
from app.templates import templates

router = APIRouter(tags=["chat-page"])
logger = logging.getLogger("chat_inference")

CHAT_ALLOWED_LANGS = frozenset({"en", "es", "ko", "zh", "ja"})


def _normalize_lang(lang: str | None) -> str | None:
    if not lang or not isinstance(lang, str):
        return None
    v = lang.strip().lower()[:5]
    return v if v in CHAT_ALLOWED_LANGS else None


def _render_chat_page(
    request: Request, token: str, identity, embed: bool = False, lang: str | None = None
) -> HTMLResponse:
    return templates.TemplateResponse(
        "chat_api.html",
        {
            "request": request,
            "token": token,
            "system_id": identity.system_id,
            "user_id": identity.user_id,
            "embed": embed,
            "lang": _normalize_lang(lang) or "",
        },
    )


@router.get("/chat", response_class=HTMLResponse)
async def chat_page(
    request: Request,
    token: str = "",
    embed: str = "",
    lang: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Chat page. embed=1 for widget. lang= en|es|ko|zh|ja for UI language; otherwise browser locale fallback."""
    logger.info("GET /chat: token_present=%s embed=%s lang=%s", bool(token), embed, lang or "(empty)")
    if not token:
        logger.warning("GET /chat: missing token")
        return HTMLResponse(
            content="<html><body><p>Missing <code>token</code> query parameter (JWT).</p></body></html>",
            status_code=400,
        )
    try:
        identity = decode_jwt(token)
    except HTTPException as e:
        logger.info("GET /chat: JWT rejected status=%s", e.status_code)
        return HTMLResponse(content=f"<html><body><p>{e.detail}</p></body></html>", status_code=e.status_code)
    try:
        await register_sync_user(db, identity.system_id, identity.user_id, identity.dify_user)
    except Exception as e:
        logger.exception("GET /chat: register_sync_user failed system_id=%s user_id=%s: %s", identity.system_id, identity.user_id, e)
        return HTMLResponse(
            content="<html><body><p>Database error. Please try again later.</p></body></html>",
            status_code=500,
        )
    try:
        logger.info("GET /chat: ok system_id=%s user_id=%s embed=%s", identity.system_id, identity.user_id, embed == "1")
        return _render_chat_page(request, token, identity, embed=(embed == "1"), lang=lang or None)
    except Exception as e:
        logger.exception("GET /chat: render failed system_id=%s user_id=%s: %s", identity.system_id, identity.user_id, e)
        return HTMLResponse(
            content="<html><body><p>Server error rendering page. Please try again later.</p></body></html>",
            status_code=500,
        )


@router.get("/chat-api", response_class=HTMLResponse)
async def chat_api_page(
    request: Request,
    token: str = "",
    embed: str = "",
    lang: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Chat page (same as /chat). embed=1 for widget. lang= en|es|ko|zh|ja."""
    logger.info("GET /chat-api: token_present=%s embed=%s lang=%s", bool(token), embed, lang or "(empty)")
    if not token:
        logger.warning("GET /chat-api: missing token")
        return HTMLResponse(
            content="<html><body><p>Missing <code>token</code> query parameter (JWT).</p></body></html>",
            status_code=400,
        )
    try:
        identity = decode_jwt(token)
    except HTTPException as e:
        logger.info("GET /chat-api: JWT rejected status=%s", e.status_code)
        return HTMLResponse(content=f"<html><body><p>{e.detail}</p></body></html>", status_code=e.status_code)
    try:
        await register_sync_user(db, identity.system_id, identity.user_id, identity.dify_user)
    except Exception as e:
        logger.exception("GET /chat-api: register_sync_user failed system_id=%s user_id=%s: %s", identity.system_id, identity.user_id, e)
        return HTMLResponse(
            content="<html><body><p>Database error. Please try again later.</p></body></html>",
            status_code=500,
        )
    try:
        logger.info("GET /chat-api: ok system_id=%s user_id=%s embed=%s", identity.system_id, identity.user_id, embed == "1")
        return _render_chat_page(request, token, identity, embed=(embed == "1"), lang=lang or None)
    except Exception as e:
        logger.exception("GET /chat-api: render failed system_id=%s user_id=%s: %s", identity.system_id, identity.user_id, e)
        return HTMLResponse(
            content="<html><body><p>Server error rendering page. Please try again later.</p></body></html>",
            status_code=500,
        )
