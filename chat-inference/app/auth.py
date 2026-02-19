"""Auth: JWT decode, API key. Same as chat-gateway."""
import logging
import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings

logger = logging.getLogger("chat_inference")

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
BEARER = HTTPBearer(auto_error=False)


class ChatIdentity:
    def __init__(self, system_id: str, user_id: str):
        self.system_id = system_id
        self.user_id = user_id

    @property
    def dify_user(self) -> str:
        return f"{self.system_id}_{self.user_id}"


def _check_system_id(system_id: str) -> None:
    from app.services.system_config import get_allowed_system_ids_list
    allowed = get_allowed_system_ids_list()
    if not allowed:
        return
    if system_id not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="system_id not allowed")


def decode_jwt(token: str) -> ChatIdentity:
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="JWT secret not configured")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    system_id = payload.get("system_id")
    user_id = payload.get("user_id")
    if not system_id or not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token must contain system_id and user_id")
    _check_system_id(system_id)
    return ChatIdentity(system_id=system_id, user_id=str(user_id))


async def get_identity_optional(
    api_key: str = Security(API_KEY_HEADER),
    bearer: HTTPAuthorizationCredentials | None = Security(BEARER),
) -> ChatIdentity | None:
    if bearer:
        return decode_jwt(bearer.credentials)
    if api_key:
        settings = get_settings()
        if settings.api_keys_list and api_key in settings.api_keys_list:
            return None
        if settings.api_keys_list:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return None


def get_identity_from_body(system_id: str, user_id: str) -> ChatIdentity:
    _check_system_id(system_id)
    return ChatIdentity(system_id=system_id, user_id=user_id)
