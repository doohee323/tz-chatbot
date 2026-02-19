"""System config (env only). No chat_systems DB."""
from app.config import get_settings


def get_valid_chat_token_api_keys() -> list[str]:
    """API keys accepted for GET /v1/chat-token."""
    return get_settings().api_keys_list


def get_allowed_system_ids_list() -> list[str]:
    """Allowed system_ids. Empty = allow all."""
    return get_settings().allowed_system_ids_list
