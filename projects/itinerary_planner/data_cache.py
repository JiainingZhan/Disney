"""TTL-based in-memory cache to minimise repeated API calls."""

import time
from typing import Any, Dict, Optional, Tuple


class DataCache:
    """Simple time-to-live (TTL) key/value cache.

    Entries are stored as ``(value, expiry_timestamp)`` pairs.
    Expired entries are evicted lazily on the next access.
    """

    def __init__(self, default_ttl_seconds: float = 300.0) -> None:
        self._default_ttl = default_ttl_seconds
        self._store: Dict[str, Tuple[Any, float]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[Any]:
        """Return cached value or *None* if absent / expired."""
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if time.monotonic() > expiry:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Store *value* under *key* with an optional custom TTL."""
        ttl = ttl if ttl is not None else self._default_ttl
        self._store[key] = (value, time.monotonic() + ttl)

    def invalidate(self, key: str) -> None:
        """Remove a specific key from the cache."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Purge the entire cache."""
        self._store.clear()

    def purge_expired(self) -> int:
        """Remove all expired entries; return count of entries removed."""
        now = time.monotonic()
        expired = [k for k, (_, exp) in self._store.items() if now > exp]
        for key in expired:
            del self._store[key]
        return len(expired)

    def __len__(self) -> int:
        return len(self._store)


# Module-level shared cache instance (5-minute TTL by default)
_shared_cache = DataCache(default_ttl_seconds=300.0)


def get_shared_cache() -> DataCache:
    """Return the module-level shared cache singleton."""
    return _shared_cache
