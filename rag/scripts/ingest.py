#!/usr/bin/env python3
"""
RAG indexer: MinIO raw/ -> LangChain Loader/Splitter/Embedding/VectorStore -> Qdrant
- Loader: PyPDFLoader, TextLoader (langchain_community)
- Splitter: RecursiveCharacterTextSplitter (langchain_text_splitters)
- Embedding: OpenAIEmbeddings, GoogleGenerativeAIEmbeddings (langchain-openai, langchain-google-genai)
- VectorStore: QdrantVectorStore (langchain-qdrant), payload: page_content, metadata{source, path, ...}

env: EMBEDDING_PROVIDER=openai|gemini,
     OpenAI: OPENAI_API_KEY, EMBEDDING_MODEL
     Gemini: GEMINI_API_KEY (or GOOGLE_API_KEY), EMBEDDING_MODEL=gemini-embedding-001
     Common: MINIO_*, QDRANT_*, CHUNK_SIZE, CHUNK_OVERLAP
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


def main():
    provider = get_env("EMBEDDING_PROVIDER", "openai").lower()
    if provider not in ("openai", "gemini"):
        print(f"EMBEDDING_PROVIDER must be openai or gemini, got: {provider}", file=sys.stderr)
        sys.exit(1)

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

    try:
        qdrant_client.delete_collection(collection_name=collection)
        print(f"Deleted collection {collection}.")
    except Exception as e:
        print(f"Delete collection (may not exist): {e}")

    objects = list(minio_client.list_objects(bucket, prefix=prefix, recursive=True))
    if not objects:
        print(f"No objects under {bucket}/{prefix}. Collection is empty. Upload PDF/txt then re-run.")
        sys.exit(0)

    all_chunk_docs: list[Document] = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for obj in objects:
            key = obj.object_name
            if key.endswith("/"):
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

            base_id = hashlib.sha256(key.encode()).hexdigest()[:16]
            last_modified = obj.last_modified.isoformat() if obj.last_modified else ""
            for i, doc in enumerate(chunk_docs):
                doc.metadata = {
                    "doc_id": base_id,
                    "source": os.path.basename(key),
                    "path": key,
                    "chunk_index": i,
                    "created_at": last_modified,
                }
                all_chunk_docs.append(doc)
            print(f"  {key}: {len(chunk_docs)} chunks")

    if not all_chunk_docs:
        print("No documents to index.")
        sys.exit(0)

    vector_store = QdrantVectorStore.from_documents(
        all_chunk_docs,
        embeddings,
        url=qdrant_url,
        collection_name=collection,
        prefer_grpc=False,
    )
    info = qdrant_client.get_collection(collection)
    print(f"Done. {collection} points_count={info.points_count}")


if __name__ == "__main__":
    main()
