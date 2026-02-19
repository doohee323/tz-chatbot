"""RAG API wrapper: call RAG Backend (same Qdrant as Dify) and return LangChain Documents."""
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import Field
from typing import List
import httpx


class RagApiRetriever(BaseRetriever):
    """Retriever that calls RAG Backend POST /query (uses same Qdrant as Dify)."""

    rag_url: str = Field(description="RAG Backend base URL (e.g. http://rag-backend:8000)")
    collection: str = Field(default="rag_docs_cointutor", description="Qdrant collection name")
    top_k: int = Field(default=5, description="Number of chunks to retrieve")

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun | None = None,
    ) -> List[Document]:
        url = self.rag_url.rstrip("/") + "/query"
        try:
            with httpx.Client(timeout=30.0) as client:
                r = client.post(
                    url,
                    json={"question": query.strip(), "top_k": self.top_k, "collection": self.collection},
                )
                r.raise_for_status()
                data = r.json()
        except Exception as e:
            raise RuntimeError(f"RAG Backend query failed: {e}") from e

        results = data.get("results") or []
        docs = []
        for item in results:
            text = item.get("text") or item.get("content") or ""
            metadata = {
                "chunk_id": item.get("chunk_id", ""),
                "source": item.get("source", ""),
                "path": item.get("path", ""),
                "score": item.get("score"),
            }
            if text:
                docs.append(Document(page_content=text, metadata=metadata))
        return docs
