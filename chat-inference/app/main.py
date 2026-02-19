import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import CHAT_TOKEN_ORIGINS_DEFAULT, get_settings
from app.database import init_db
from app.routers import cache_view, chat, chat_page, index

# Ensure app logs appear in terminal even with uvicorn --reload (force=True overrides existing config)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
    force=True,
)
logger = logging.getLogger("chat_inference")


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        client = request.client.host if request.client else "-"
        line = f"{request.method} {request.url.path} {response.status_code} {client}"
        logger.info("%s %s %s %s", request.method, request.url.path, response.status_code, client)
        print(f"[request] {line}", file=sys.stderr, flush=True)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Chat Inference ready (Dify-free, uses RAG Backend -> Qdrant)")
    yield


app = FastAPI(title="Chat Inference", description="Dify-free chat pipeline", lifespan=lifespan)

# CORS: required for frontends (e.g. DrillQuiz) calling /v1/chat-token. OPTIONS preflight + X-API-Key allowed.
CORS_ALLOW_METHODS = ["GET", "POST", "DELETE", "OPTIONS"]
CORS_ALLOW_HEADERS = ["X-API-Key", "Content-Type", "Authorization", "Accept"]

# Merge default domains with env extra list (same default as /v1/chat-token origin check).
_origins_extra = get_settings().allowed_chat_token_origins_list
cors_origins = list(CHAT_TOKEN_ORIGINS_DEFAULT)
for o in _origins_extra:
    if o and o not in cors_origins:
        cors_origins.append(o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
    expose_headers=[],
)
app.add_middleware(RequestLogMiddleware)
app.include_router(index.router)
app.include_router(chat.router)
app.include_router(chat_page.router)
app.include_router(cache_view.router)


@app.get("/health")
def health():
    return {"status": "ok"}
