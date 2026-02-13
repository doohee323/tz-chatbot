"""Store chat quality data to MinIO for MLflow RAG quality pipelines.

See docs/mlflow/chat-quality-data-minio-plan.md for schema and bucket structure.
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any

logger = logging.getLogger("chat_gateway")


def _get_minio_client():
    """Lazy import to avoid dependency when MinIO is not configured."""
    try:
        from minio import Minio
        return Minio
    except ImportError:
        return None


def _derive_topic_from_collection(collection: str | None) -> str:
    """Extract topic from collection name, e.g. rag_docs_cointutor -> cointutor."""
    if not collection:
        return "default"
    # rag_docs_cointutor -> cointutor, rag_docs_drillquiz -> drillquiz
    if "_" in collection:
        return collection.rsplit("_", 1)[-1].lower()
    return collection.lower()


async def record_chat_to_minio(
    *,
    question: str,
    answer: str,
    timestamp: datetime | None = None,
    conversation_id: str | None = None,
    message_id: str | None = None,
    system_id: str = "default",
    topic: str | None = None,
    retrieved: list[dict] | None = None,
    top_k: int | None = None,
    collection: str | None = None,
    latency_ms: int | None = None,
    model_name: str | None = None,
    dify_metadata: dict | None = None,
) -> str | None:
    """Store one chat turn to MinIO. Path: {project}/{topic}/raw/{date}/{log_id}.json

    Best-effort, non-blocking. Bucket is created if missing.
    """
    from app.config import get_settings
    settings = get_settings()
    endpoint = (settings.minio_endpoint or "").strip()
    bucket = (settings.minio_rag_quality_bucket or "rag-quality-data").strip() or "rag-quality-data"
    access_key = (settings.minio_access_key or "").strip()
    secret_key = (settings.minio_secret_key or "").strip()

    if not endpoint or not access_key or not secret_key:
        logger.debug(
            "Chat quality MinIO: skipped (MINIO_ENDPOINT/ACCESS_KEY/SECRET_KEY not configured)"
        )
        return None

    if not question and not answer:
        return None

    MinioCls = _get_minio_client()
    if MinioCls is None:
        logger.warning("Chat quality MinIO: minio package not installed. pip install minio")
        return None

    log_id = str(uuid.uuid4())
    ts = timestamp or datetime.utcnow()
    ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ") if ts else datetime.utcnow().isoformat() + "Z"
    date_path = ts.strftime("%Y-%m-%d") if ts else datetime.utcnow().strftime("%Y-%m-%d")

    payload: dict[str, Any] = {
        "log_id": log_id,
        "log_type": "chat_quality",
        "timestamp": ts_str,
        "question": question or "",
        "answer": answer or "",
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    if message_id:
        payload["message_id"] = message_id
    if system_id and system_id != "default":
        payload["system_id"] = system_id
    if retrieved is not None:
        payload["retrieved"] = retrieved
    if top_k is not None:
        payload["top_k"] = top_k
    if collection:
        payload["collection"] = collection
    if latency_ms is not None:
        payload["latency_ms"] = latency_ms
    if model_name:
        payload["model_name"] = model_name
    # Full Dify metadata (usage, retriever_resources, annotation_reply, workflow extras)
    if dify_metadata:
        payload["dify_metadata"] = dify_metadata

    project = (system_id or "default").lower()
    topic_val = (topic or _derive_topic_from_collection(collection) or "default").lower()
    object_path = f"{project}/{topic_val}/raw/{date_path}/{log_id}.json"
    if topic_val:
        payload["topic"] = topic_val
    payload["project"] = project

    def _upload():
        # Parse endpoint: "host:port", "http://host:port", or "https://host:port"
        ep = (endpoint or "").strip()
        secure = ep.startswith("https")
        if ep.startswith("http://"):
            ep = ep[7:]
        elif ep.startswith("https://"):
            ep = ep[8:]
        host, _, port_part = ep.partition(":")
        port = int(port_part) if port_part else (443 if secure else 9000)
        if not host:
            raise ValueError("Invalid MINIO_ENDPOINT for chat quality")

        client = MinioCls(
            f"{host}:{port}",
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        from io import BytesIO
        client.put_object(
            bucket,
            object_path,
            BytesIO(data),
            length=len(data),
            content_type="application/json",
        )
        logger.info("Chat quality stored to MinIO: %s/%s", bucket, object_path)
        return object_path

    try:
        # Run blocking MinIO call in thread pool to avoid blocking chat response
        return await asyncio.to_thread(_upload)
    except Exception as e:
        logger.warning(
            "Failed to store chat quality to MinIO: %s (path=%s)",
            e,
            object_path,
            exc_info=False,
        )
        return None
