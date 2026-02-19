"""Chat Inference client. Calls chat-inference POST /chat instead of Dify."""
import logging

import httpx

logger = logging.getLogger("chat_gateway")


async def send_chat_message(
    user: str,
    query: str,
    conversation_id: str | None = None,
    inputs: dict | None = None,
    base_url: str = "",
) -> dict:
    """Call chat-inference POST /chat. Returns { answer, conversation_id?, message_id? }."""
    url = (base_url.rstrip("/") + "/chat").strip()
    body = {
        "query": query,
        "user": user,
        "conversation_id": conversation_id,
        "inputs": inputs or {},
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(url, json=body)
        if r.status_code >= 400:
            logger.warning("Chat Inference error: %s %s -> %s", "POST", url, r.status_code)
        r.raise_for_status()
        data = r.json()
    return {
        "conversation_id": data.get("conversation_id") or conversation_id or "",
        "message_id": data.get("message_id"),
        "answer": data.get("answer", ""),
    }
