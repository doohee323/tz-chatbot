#!/usr/bin/env python3
"""
RAG indexer: MinIO raw/ -> LangChain Loader/Splitter/Embedding/VectorStore -> Qdrant
- Loader: PyPDFLoader, TextLoader (langchain_community)
- Splitter: RecursiveCharacterTextSplitter (langchain_text_splitters)
- Embedding: OpenAIEmbeddings, GoogleGenerativeAIEmbeddings (langchain-openai, langchain-google-genai)
- VectorStore: QdrantVectorStore (langchain-qdrant), payload: page_content, metadata{source, path, doc_id, ...}

Incremental: Only re-index new/changed files, delete vectors for removed files.
  Set INCREMENTAL=false for full sync (delete collection, rebuild all).

env: EMBEDDING_PROVIDER=openai|gemini,
     OpenAI: OPENAI_API_KEY, EMBEDDING_MODEL
     Gemini: GEMINI_API_KEY (or GOOGLE_API_KEY), EMBEDDING_MODEL=gemini-embedding-001
     Common: MINIO_*, QDRANT_*, CHUNK_SIZE, CHUNK_OVERLAP, INCREMENTAL
"""
import os
import sys
import hashlib
import tempfile

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from minio import Minio
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels


def get_env(name: str, default: str = "") -> str:
    v = os.environ.get(name, default).strip()
    return v


def require_env(name: str) -> str:
    v = get_env(name)
    if not v:
        print(f"Missing env: {name}", file=sys.stderr)
        sys.exit(1)
    return v


def load_document(data: bytes, key: str, temp_dir: str) -> list[Document]:
    """Load document using LangChain loaders (Loader abstraction)."""
    ext = (key.split(".")[-1] or "").lower()
    suffix = f".{ext}" if ext else ".txt"
    fd, path = tempfile.mkstemp(suffix=suffix, dir=temp_dir)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        if ext == "pdf":
            loader = PyPDFLoader(path)
            return loader.load()
        if ext in ("txt", "md", "text"):
            loader = TextLoader(path, encoding="utf-8", autodetect_encoding=True)
            return loader.load()
        try:
            loader = TextLoader(path, encoding="utf-8", autodetect_encoding=True)
            return loader.load()
        except Exception:
            return []
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def get_existing_doc_states(qdrant_client: QdrantClient, collection: str) -> dict[str, str]:
    """Scroll Qdrant to get doc_id -> created_at (last_modified) for incremental comparison."""
    result: dict[str, str] = {}
    offset = None
    limit = 100
    while True:
        points, offset = qdrant_client.scroll(
            collection_name=collection,
            scroll_filter=None,
            limit=limit,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        for pt in points or []:
            payload = getattr(pt, "payload", None) or {}
            meta = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else payload
            doc_id = (meta or {}).get("doc_id")
            created = (meta or {}).get("created_at", "")
            if doc_id:
                result[doc_id] = created
        if offset is None:
            break
    return result


def delete_points_by_doc_id(qdrant_client: QdrantClient, collection: str, doc_id: str) -> None:
    """Delete all points with payload.metadata.doc_id == doc_id."""
    qdrant_client.delete(
        collection_name=collection,
        points_selector=qmodels.FilterSelector(
            filter=qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="metadata.doc_id",
                        match=qmodels.MatchValue(value=doc_id),
                    ),
                ],
            ),
        ),
    )


def main():
    provider = get_env("EMBEDDING_PROVIDER", "openai").lower()
    if provider not in ("openai", "gemini"):
        print(f"EMBEDDING_PROVIDER must be openai or gemini, got: {provider}", file=sys.stderr)
        sys.exit(1)

    incremental = get_env("INCREMENTAL", "true").lower() in ("true", "1", "yes")
    print(f"Mode: {'incremental' if incremental else 'full sync'}")

    endpoint = get_env("MINIO_ENDPOINT", "minio.devops.svc.cluster.local")
    port = int(get_env("MINIO_PORT", "9000"))
    access_key = require_env("MINIO_ACCESS_KEY")
    secret_key = require_env("MINIO_SECRET_KEY")
    bucket = get_env("MINIO_BUCKET", "rag-docs")
    prefix = get_env("MINIO_PREFIX", "raw/").rstrip("/") + "/"

    qdrant_host = get_env("QDRANT_HOST", "qdrant")
    qdrant_port = int(get_env("QDRANT_PORT", "6333"))
    collection = get_env("QDRANT_COLLECTION", "rag_docs")
    qdrant_url = f"http://{qdrant_host}:{qdrant_port}"

    chunk_size = int(get_env("CHUNK_SIZE", "500"))
    chunk_overlap = int(get_env("CHUNK_OVERLAP", "50"))

    # LangChain Embedding
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        api_key = require_env("OPENAI_API_KEY")
        embedding_model = get_env("EMBEDDING_MODEL", "text-embedding-3-small")
        embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=api_key)
        print(f"Embedding: OpenAI {embedding_model}")
    else:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        api_key = get_env("GEMINI_API_KEY") or get_env("GOOGLE_API_KEY")
        if not api_key:
            print("Missing env: GEMINI_API_KEY or GOOGLE_API_KEY", file=sys.stderr)
            sys.exit(1)
        embedding_model = get_env("EMBEDDING_MODEL", "gemini-embedding-001")
        output_dim = int(get_env("EMBEDDING_DIM", "1536"))
        embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=api_key,
            task_type="retrieval_document",
            output_dimensionality=output_dim,
        )
        print(f"Embedding: Gemini {embedding_model} (dim={output_dim})")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    minio_client = Minio(
        f"{endpoint}:{port}",
        access_key=access_key,
        secret_key=secret_key,
        secure=get_env("MINIO_USE_SSL", "false").lower() == "true",
    )
    qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port, check_compatibility=False)

    if not minio_client.bucket_exists(bucket):
        minio_client.make_bucket(bucket)
        print(f"Created bucket {bucket}.")

    objects = list(minio_client.list_objects(bucket, prefix=prefix, recursive=True))
    objects = [o for o in objects if not (o.object_name or "").endswith("/")]

    if not objects:
        if incremental:
            try:
                existing = get_existing_doc_states(qdrant_client, collection)
                for doc_id in existing:
                    delete_points_by_doc_id(qdrant_client, collection, doc_id)
                    print(f"  Deleted doc_id={doc_id} (file removed from MinIO)")
            except Exception as e:
                print(f"Collection may not exist: {e}")
            print("No objects under prefix. Cleared removed docs. Done.")
        else:
            try:
                qdrant_client.delete_collection(collection_name=collection)
                print(f"Deleted collection {collection}.")
            except Exception:
                pass
            print("No objects under prefix. Collection empty. Done.")
        sys.exit(0)

    # Current MinIO state: path -> (doc_id, last_modified)
    current: dict[str, tuple[str, str]] = {}
    for obj in objects:
        key = obj.object_name
        base_id = hashlib.sha256(key.encode()).hexdigest()[:16]
        last_modified = obj.last_modified.isoformat() if obj.last_modified else ""
        current[key] = (base_id, last_modified)

    collection_exists = False
    try:
        qdrant_client.get_collection(collection_name=collection)
        collection_exists = True
    except Exception:
        pass

    if not incremental or not collection_exists:
        # Full sync
        try:
            qdrant_client.delete_collection(collection_name=collection)
            print("Deleted collection (full sync).")
        except Exception:
            pass
        qdrant_client.create_collection(
            collection_name=collection,
            vectors_config=qmodels.VectorParams(size=1536, distance=qmodels.Distance.COSINE),
        )
        print("Created collection.")
        existing_doc_states: dict[str, str] = {}
    else:
        existing_doc_states = get_existing_doc_states(qdrant_client, collection)
        # Delete docs removed from MinIO
        current_doc_ids = {v[0] for v in current.values()}
        for doc_id in list(existing_doc_states.keys()):
            if doc_id not in current_doc_ids:
                delete_points_by_doc_id(qdrant_client, collection, doc_id)
                print(f"  Deleted doc_id={doc_id} (file removed)")
                del existing_doc_states[doc_id]

    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=qdrant_url,
        collection_name=collection,
        prefer_grpc=False,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        for obj in objects:
            key = obj.object_name
            base_id, last_modified = current[key]
            if incremental and base_id in existing_doc_states:
                if existing_doc_states[base_id] == last_modified:
                    print(f"  {key}: skip (unchanged)")
                    continue

            data = minio_client.get_object(bucket, key).read()
            docs = load_document(data, key, temp_dir)
            if not docs:
                continue
            combined_text = "\n".join(d.page_content for d in docs if d.page_content and d.page_content.strip())
            if not combined_text.strip():
                continue
            chunk_docs = splitter.split_documents(
                [Document(page_content=combined_text, metadata={"source_path": key})]
            )
            if not chunk_docs:
                continue

            if incremental and collection_exists:
                delete_points_by_doc_id(qdrant_client, collection, base_id)

            for i, doc in enumerate(chunk_docs):
                doc.metadata = {
                    "doc_id": base_id,
                    "source": os.path.basename(key),
                    "path": key,
                    "chunk_index": i,
                    "created_at": last_modified,
                }

            vector_store.add_documents(chunk_docs)
            action = "updated" if base_id in (existing_doc_states or {}) else "added"
            print(f"  {key}: {len(chunk_docs)} chunks ({action})")

    info = qdrant_client.get_collection(collection)
    print(f"Done. {collection} points_count={info.points_count}")


if __name__ == "__main__":
    main()
