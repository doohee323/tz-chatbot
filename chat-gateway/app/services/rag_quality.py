"""RAG quality enrichment for MinIO chat logs.

Resolve ground_truth/keywords from expected_questions YAML by question text.
"""
import logging
from typing import Any

logger = logging.getLogger("chat_gateway")


def _load_expected_questions_cached(path: str) -> list[dict] | None:
    """Load expected_questions YAML once per path (module-level cache by path)."""
    if not path or not path.strip():
        return None
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return (data or {}).get("questions") or []
    except FileNotFoundError:
        logger.debug("Expected questions file not found: %s", path)
        return None
    except Exception as e:
        logger.warning("Failed to load expected_questions %s: %s", path, e, exc_info=False)
        return None


# Cache: path -> list of question items (no TTL; restart to reload)
_expected_questions_cache: dict[str, list[dict]] = {}


def get_expected_for_question(question: str, expected_questions_path: str) -> dict[str, Any] | None:
    """If question matches an expected_questions entry, return question_id, ground_truth, keywords.

    Match is by normalized question string (strip, optional case-insensitive).
    Returns None if path empty, file missing, or no match.
    """
    if not (expected_questions_path or (question or "").strip()):
        return None
    qnorm = (question or "").strip()
    if not qnorm:
        return None
    if expected_questions_path not in _expected_questions_cache:
        loaded = _load_expected_questions_cached(expected_questions_path)
        _expected_questions_cache[expected_questions_path] = loaded if loaded is not None else []
    items = _expected_questions_cache.get(expected_questions_path) or []
    for item in items:
        if not isinstance(item, dict):
            continue
        eq = (item.get("question") or "").strip()
        if eq and eq == qnorm:
            return {
                "question_id": item.get("id") or "",
                "ground_truth": item.get("ground_truth") or "",
                "keywords": item.get("keywords") or [],
            }
    return None
