from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from functools import lru_cache

# Default origins for CORS and /v1/chat-token (when ALLOWED_CHAT_TOKEN_ORIGINS is empty). Keep in sync with main.py CORS.
CHAT_TOKEN_ORIGINS_DEFAULT = [
    "https://chat-admin.drillquiz.com",
    "https://chat-admin-qa.drillquiz.com",
    "https://chat-admin-dev.drillquiz.com",
    "https://us-dev.drillquiz.com",
    "https://us.drillquiz.com",
    "https://us-qa.drillquiz.com",
    "https://devops.drillquiz.com",
    "https://leetcode.drillquiz.com",
    "https://cointutor.net",
    "https://www.cointutor.net",
    "https://dev.cointutor.net",
    "https://qa.cointutor.net",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:8088",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8088",
]


class Settings(BaseSettings):
    # Shared Dify (can leave empty if using only per-system)
    dify_base_url: str = Field("", validation_alias="DIFY_BASE_URL")
    dify_api_key: str = Field("", validation_alias="DIFY_API_KEY")
    # Per-system (env fallback when chat_systems DB is empty)
    dify_drillquiz_base_url: str = Field("", validation_alias="DIFY_DRILLQUIZ_BASE_URL")
    dify_drillquiz_api_key: str = Field("", validation_alias="DIFY_DRILLQUIZ_API_KEY")
    dify_cointutor_base_url: str = Field("", validation_alias="DIFY_COINTUTOR_BASE_URL")
    dify_cointutor_api_key: str = Field("", validation_alias="DIFY_COINTUTOR_API_KEY")
    jwt_secret: str = Field(..., validation_alias="CHAT_GATEWAY_JWT_SECRET")
    api_keys: str = Field("", validation_alias="CHAT_GATEWAY_API_KEY")
    allowed_system_ids: str = ""
    # Allowed origins for /v1/chat-token (comma-separated). Empty = no check.
    allowed_chat_token_origins: str = ""
    # Explicit DATABASE_URL overrides. Otherwise: SQLite locally, PostgreSQL when POSTGRES_HOST is set (K8s).
    database_url: str = Field("", validation_alias="DATABASE_URL")
    postgres_host: str = Field("", validation_alias="POSTGRES_HOST")
    postgres_port: str = Field("5432", validation_alias="POSTGRES_PORT")
    postgres_db: str = Field("chat_admin", validation_alias="POSTGRES_DB")
    postgres_user: str = Field("postgres", validation_alias="POSTGRES_USER")
    postgres_password: str = Field("", validation_alias="POSTGRES_PASSWORD")
    dify_chatbot_token: str = ""

    # MinIO for chat quality data (rag-quality-data bucket). Empty = skip MinIO upload.
    minio_endpoint: str = Field("", validation_alias="MINIO_ENDPOINT", description="e.g. http://minio.devops.svc.cluster.local:9000")
    minio_access_key: str = Field("", validation_alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field("", validation_alias="MINIO_SECRET_KEY")
    minio_rag_quality_bucket: str = Field("rag-quality-data", validation_alias="MINIO_RAG_QUALITY_BUCKET")

    # Path to expected_questions YAML for ground_truth/keywords enrichment in MinIO logs. Empty = skip.
    expected_questions_path: str = Field("", validation_alias="EXPECTED_QUESTIONS_PATH")

    @computed_field
    @property
    def effective_database_url(self) -> str:
        """SQLite locally, PostgreSQL on K8s (when POSTGRES_HOST is set). Same DB as chat-admin."""
        if self.database_url.strip():
            return self.database_url.strip()
        if self.postgres_host.strip():
            from urllib.parse import quote_plus
            pw = quote_plus(self.postgres_password) if self.postgres_password else ""
            return f"postgresql+asyncpg://{self.postgres_user}:{pw}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        return "sqlite+aiosqlite:///./chat_gateway.db"
    # Per-system Dify: use env DIFY_<system_id>_BASE_URL / DIFY_<system_id>_API_KEY when set (no hardcoded system names).
    # Redirect root URL to chat-admin (default: http://localhost:8080)
    chat_admin_url: str = Field("http://localhost:8080", validation_alias="CHAT_ADMIN_URL")

    def get_dify_base_url(self, system_id: str | None) -> str:
        if system_id:
            key = f"dify_{system_id.lower()}_base_url"
            url = getattr(self, key, None) or ""
            if url.strip():
                return url.rstrip("/")
        return self.dify_base_url.rstrip("/")

    def get_dify_api_key(self, system_id: str | None) -> str:
        if system_id:
            key = f"dify_{system_id.lower()}_api_key"
            api_key = getattr(self, key, None) or ""
            if api_key.strip():
                return api_key.strip()
        return self.dify_api_key or ""

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
        return [s.strip() for s in self.allowed_chat_token_origins.split(",") if s.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
