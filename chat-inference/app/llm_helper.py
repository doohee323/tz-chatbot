"""LLM helper: Gemini primary (Dify parity), OpenAI fallback. Uses config for model names and keys."""
from langchain_core.language_models.chat_models import BaseChatModel

from app.config import Settings


def get_llm(settings: Settings) -> BaseChatModel:
    """Return a LangChain chat model: Gemini if key set, else OpenAI. Raises if neither key set."""
    if (settings.gemini_api_key or "").strip():
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.gemini_api_key,
            temperature=settings.temperature,
            max_output_tokens=settings.max_tokens,
        )
    if (settings.openai_api_key or "").strip():
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.openai_llm_model,
            api_key=settings.openai_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
    raise ValueError("At least one of GEMINI_API_KEY (or GOOGLE_API_KEY) or OPENAI_API_KEY is required")
