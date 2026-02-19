"""Chat API: /v1/chat, /v1/chat-token, /v1/conversations. Same schema as chat-gateway."""
import asyncio
import logging
import time
import uuid
import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Security, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.auth import API_KEY_HEADER, get_identity_from_body, get_identity_optional, ChatIdentity
from app.config import CHAT_TOKEN_ORIGINS_DEFAULT, get_settings
from app.database import get_db
from app.models import ConversationCache, ConversationMapping, MessageCache
from app.services.system_config import get_allowed_system_ids_list, get_valid_chat_token_api_keys
from app.services.chat_quality_minio import record_chat_to_minio
from app.sync_service import record_chat_to_db

from app.classifier import build_classifier
from app.chains import build_rag_chain

router = APIRouter(prefix="/v1", tags=["chat"])
logger = logging.getLogger("chat_inference")


class ChatRequest(BaseModel):
    system_id: str | None = Field(None, min_length=1, max_length=64)
    user_id: str | None = Field(None, min_length=1, max_length=256)
    message: str = Field(..., min_length=1)
    conversation_id: str | None = None
    inputs: dict | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str | None = None
    answer: str | None = None
    metadata: dict | None = None


class ConversationItem(BaseModel):
    id: str
    name: str | None = None
    created_at: int | None = None


class MessageItem(BaseModel):
    id: str
    role: str
    content: str | None = None
    created_at: int | None = None


def _resolve_identity(
    identity: ChatIdentity | None,
    body: ChatRequest | None,
    api_key: str | None,
    system_id: str | None = None,
    user_id: str | None = None,
) -> ChatIdentity:
    if identity is not None:
        if system_id and user_id and (identity.system_id != system_id or identity.user_id != user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="system_id/user_id must match token")
        return identity
    settings = get_settings()
    if not api_key or (settings.api_keys_list and api_key not in settings.api_keys_list):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key or Bearer token required")
    if body and body.system_id and body.user_id:
        return get_identity_from_body(body.system_id, body.user_id)
    if system_id and user_id:
        return get_identity_from_body(system_id, user_id)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="system_id and user_id required in body or query when using API key")


settings = get_settings()
_classifier = None
_chain_after_sales = None
_chain_products = None


def _get_classifier():
    global _classifier
    if _classifier is None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY required")
        _classifier = build_classifier(settings)
    return _classifier


def _get_chains():
    global _chain_after_sales, _chain_products
    if _chain_after_sales is None:
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY required")
        _chain_after_sales = build_rag_chain(settings, settings.rag_collection_after_sales)
        _chain_products = build_rag_chain(settings, settings.rag_collection_products)
    return _chain_after_sales, _chain_products


def _run_pipeline(query: str) -> tuple[str, str | None]:
    """Returns (answer, collection_or_none). collection is RAG collection name when RAG used, else None."""
    classify = _get_classifier()
    label = classify(query)
    logger.info("Classifier result: %s", label)
    if label == settings.class_other:
        return settings.other_answer, None
    chain_a, chain_p = _get_chains()
    if label == settings.class_after_sales:
        return chain_a.invoke(query), settings.rag_collection_after_sales
    if label == settings.class_products:
        return chain_p.invoke(query), settings.rag_collection_products
    return settings.other_answer, None


@router.get("/status")
async def get_status():
    systems = {}
    for sid in get_allowed_system_ids_list():
        systems[sid] = {"backend": "chat_inference", "configured": True}
    return {"systems": systems}


@router.post("/chat", response_model=ChatResponse)
async def post_chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    identity: ChatIdentity | None = Depends(get_identity_optional),
    api_key: str = Security(API_KEY_HEADER),
):
    sid = body.system_id or (identity.system_id if identity else None)
    uid = body.user_id or (identity.user_id if identity else None)
    ident = _resolve_identity(identity, body, api_key, system_id=sid, user_id=uid)

    t0 = time.perf_counter()
    try:
        answer, collection = _run_pipeline(body.message.strip())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        logger.exception("Pipeline error: %s", e)
        detail = "Chat service temporarily unavailable."
        if "nodename nor servname" in str(e) or "ConnectError" in type(e).__name__:
            detail = "RAG Backend unreachable. For local dev set RAG_BACKEND_URL (e.g. http://localhost:8000)."
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
    latency_ms = int((time.perf_counter() - t0) * 1000)

    conversation_id = body.conversation_id or str(uuid.uuid4())
    message_id = f"local-{uuid.uuid4().hex[:12]}"

    try:
        row = ConversationMapping(
            system_id=ident.system_id,
            user_id=ident.user_id,
            dify_user=ident.dify_user,
            conversation_id=conversation_id,
        )
        db.add(row)
        await record_chat_to_db(
            db,
            ident.system_id,
            ident.user_id,
            ident.dify_user,
            conversation_id,
            message_id,
            body.message,
            answer,
        )
    except Exception as e:
        logger.warning("Failed to record chat: %s", e)
        await db.rollback()

    # RAG quality log to MinIO (fire-and-forget; same schema as chat-gateway)
    asyncio.create_task(
        record_chat_to_minio(
            question=body.message,
            answer=answer,
            conversation_id=conversation_id,
            message_id=message_id,
            system_id=ident.system_id,
            collection=collection,
            top_k=settings.rag_top_k,
            latency_ms=latency_ms,
            model_name=settings.llm_model,
        )
    )

    return ChatResponse(
        conversation_id=conversation_id,
        message_id=message_id,
        answer=answer,
        metadata=None,
    )


@router.get("/conversations", response_model=list[ConversationItem])
async def list_conversations(
    system_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    identity: ChatIdentity | None = Depends(get_identity_optional),
    api_key: str = Security(API_KEY_HEADER),
):
    ident = _resolve_identity(identity, None, api_key, system_id=system_id, user_id=user_id)
    q = select(ConversationCache).where(
        ConversationCache.system_id == ident.system_id,
        ConversationCache.user_id == ident.user_id,
    ).order_by(ConversationCache.created_at.desc().nullslast())
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        ConversationItem(
            id=r.conversation_id,
            name=r.name,
            created_at=int(r.created_at.timestamp()) if r.created_at else None,
        )
        for r in rows
    ]


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageItem])
async def list_messages(
    conversation_id: str,
    system_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    identity: ChatIdentity | None = Depends(get_identity_optional),
    api_key: str = Security(API_KEY_HEADER),
):
    ident = _resolve_identity(identity, None, api_key, system_id=system_id, user_id=user_id)
    q = select(ConversationCache).where(
        ConversationCache.conversation_id == conversation_id,
        ConversationCache.system_id == ident.system_id,
        ConversationCache.user_id == ident.user_id,
    )
    r = (await db.execute(q)).scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    q2 = select(MessageCache).where(MessageCache.conversation_id == conversation_id).order_by(
        MessageCache.created_at.asc().nullslast(), MessageCache.id.asc()
    )
    result = await db.execute(q2)
    rows = result.scalars().all()
    return [
        MessageItem(
            id=r2.message_id,
            role=r2.role,
            content=r2.content,
            created_at=int(r2.created_at.timestamp()) if r2.created_at else None,
        )
        for r2 in rows
    ]


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_route(
    conversation_id: str,
    system_id: str = Query(...),
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    identity: ChatIdentity | None = Depends(get_identity_optional),
    api_key: str = Security(API_KEY_HEADER),
):
    from sqlalchemy import delete
    ident = _resolve_identity(identity, None, api_key, system_id=system_id, user_id=user_id)
    await db.execute(delete(MessageCache).where(MessageCache.conversation_id == conversation_id))
    await db.execute(delete(ConversationCache).where(
        ConversationCache.conversation_id == conversation_id,
        ConversationCache.system_id == ident.system_id,
        ConversationCache.user_id == ident.user_id,
    ))
    await db.execute(delete(ConversationMapping).where(
        ConversationMapping.conversation_id == conversation_id,
        ConversationMapping.system_id == ident.system_id,
        ConversationMapping.user_id == ident.user_id,
    ))


@router.get("/chat-token", response_model=dict)
async def get_chat_token(
    request: Request,
    system_id: str = Query(...),
    user_id: str = Query("12345"),
    api_key: str = Security(API_KEY_HEADER),
):
    """Issue JWT for chat page. X-API-Key required."""
    valid_keys = get_valid_chat_token_api_keys()
    if not api_key or (valid_keys and api_key not in valid_keys):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")
    origins = get_settings().allowed_chat_token_origins_list or CHAT_TOKEN_ORIGINS_DEFAULT
    if origins:
        origin = request.headers.get("origin") or request.headers.get("referer") or ""
        origin_base = origin.split("?")[0].rstrip("/")
        if not any(origin_base == o or origin_base.startswith(o + "/") for o in origins):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Origin not allowed")
    get_identity_from_body(system_id, user_id)
    secret = get_settings().jwt_secret
    if not secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="JWT secret not configured")
    payload = {"system_id": system_id, "user_id": user_id, "exp": int(time.time()) + 86400}
    token = jwt.encode(payload, secret, algorithm="HS256")
    if hasattr(token, "decode"):
        token = token.decode("utf-8")
    return {"token": token}
