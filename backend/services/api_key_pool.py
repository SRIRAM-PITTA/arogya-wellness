import time
import threading
from typing import Dict, List

from config.settings import GROQ_API_KEY

# Keys and their cooldown state are loaded lazily after dotenv has initialized.
_keys: List[str] = []
_key_state: Dict[str, float] = {}

# Lock to keep operations thread-safe
_lock = threading.Lock()

# How long to disable a key after quota error (seconds)
COOLDOWN_SECONDS = 3600  # 1 hour


def _refresh_keys() -> None:
    configured_keys = [
        key.strip() for key in (GROQ_API_KEY or "").split(",") if key.strip()
    ]
    if set(configured_keys) == set(_keys):
        return
    for key in configured_keys:
        _key_state.setdefault(key, 0.0)
    _keys[:] = configured_keys


def get_next_key() -> str:
    """Return the next available Grok/xAI API key, skipping keys in cooldown."""
    with _lock:
        _refresh_keys()
        if not _keys:
            raise RuntimeError("No GROQ_API_KEY configured")

        now = time.time()
        available = [k for k in _keys if _key_state.get(k, 0) <= now]
        if not available:
            raise RuntimeError(
                "All Groq API keys are currently in cooldown due to quota limits."
            )

        # Simple round-robin: take first available, move it to the end
        key = available[0]
        _keys.remove(key)
        _keys.append(key)
        return key


def mark_key_quota_exceeded(key: str) -> None:
    """Mark a key as temporarily disabled because quota was exceeded."""
    with _lock:
        if key in _key_state:
            _key_state[key] = time.time() + COOLDOWN_SECONDS

