"""Config for chat-inference. Same Qdrant (Dify's DB) via RAG Backend API."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field, AliasChoices


# Default origins for CORS and /v1/chat-token. Same as chat-gateway.
CHAT_TOKEN_ORIGINS_DEFAULT = [
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:8088",
    "http://localhost:8090",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8088",
    "http://127.0.0.1:8090",
]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Auth (same as chat-gateway)
    jwt_secret: str = Field("", validation_alias="CHAT_GATEWAY_JWT_SECRET")
    api_keys: str = Field("", validation_alias="CHAT_GATEWAY_API_KEY")
    allowed_system_ids: str = Field("", validation_alias="ALLOWED_SYSTEM_IDS")
    allowed_chat_token_origins: str = Field("", validation_alias="ALLOWED_CHAT_TOKEN_ORIGINS")

    # DB (same as chat-gateway)
    database_url: str = Field("", validation_alias="DATABASE_URL")
    postgres_host: str = Field("", validation_alias="POSTGRES_HOST")
    postgres_port: str = Field("5432", validation_alias="POSTGRES_PORT")
    postgres_db: str = Field("chat_admin", validation_alias="POSTGRES_DB")
    postgres_user: str = Field("postgres", validation_alias="POSTGRES_USER")
    postgres_password: str = Field("", validation_alias="POSTGRES_PASSWORD")
    chat_admin_url: str = Field("http://localhost:8080", validation_alias="CHAT_ADMIN_URL")

    # MinIO: RAG quality logs (same bucket/schema as chat-gateway). Empty = skip.
    minio_endpoint: str = Field("", validation_alias="MINIO_ENDPOINT")
    minio_access_key: str = Field("", validation_alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field("", validation_alias="MINIO_SECRET_KEY")
    minio_rag_quality_bucket: str = Field("rag-quality-data", validation_alias="MINIO_RAG_QUALITY_BUCKET")

    @computed_field
    @property
    def effective_database_url(self) -> str:
        if self.database_url.strip():
            return self.database_url.strip()
        if self.postgres_host.strip():
            from urllib.parse import quote_plus
            pw = quote_plus(self.postgres_password) if self.postgres_password else ""
            return f"postgresql+asyncpg://{self.postgres_user}:{pw}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        return "sqlite+aiosqlite:///./chat_inference.db"

    @property
    def api_keys_list(self) -> list[str]:
        if not self.api_keys.strip():
            return []
        return [k.strip() for k in self.api_keys.split(",") if k.strip()]

    @property
    def allowed_system_ids_list(self) -> list[str]:
        if not self.allowed_system_ids.strip():
            return []
        return [s.strip() for s in self.allowed_system_ids.split(",") if s.strip()]

    @property
    def allowed_chat_token_origins_list(self) -> list[str]:
        if not self.allowed_chat_token_origins.strip():
            return []
        return [o.strip() for o in self.allowed_chat_token_origins.split(",") if o.strip()]

    # LLM (Gemini, same as Dify)
    gemini_api_key: str = Field("", validation_alias=AliasChoices("GEMINI_API_KEY", "GOOGLE_API_KEY"))
    llm_model: str = "gemini-2.5-flash"
    temperature: float = 0.7
    max_tokens: int = 512

    # RAG Backend (Dify's DB via Qdrant; RAG Backend queries it)
    # Default: same RAG Backend URL used by Dify as tool
    rag_backend_url: str = "http://rag-backend.rag.svc.cluster.local:8000"
    rag_collection_after_sales: str = "rag_docs_cointutor"
    rag_collection_products: str = "rag_docs_cointutor"
    rag_top_k: int = 5

    # Classifier labels (must match Dify workflow)
    class_after_sales: str = "after_sales"
    class_products: str = "products"
    class_other: str = "other"

    # Fixed answer for "other" branch
    other_answer: str = "Sorry, I can't help you with these questions."


@lru_cache
def get_settings() -> Settings:
    return Settings()
