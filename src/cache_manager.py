import sys

# Simple In-Memory Cache
_CACHE_STORE = {}
MAX_CACHE_SIZE = 1000

def get_from_cache(key: str):
    return _CACHE_STORE.get(key)

def set_to_cache(key: str, value: str):
    if len(_CACHE_STORE) > MAX_CACHE_SIZE:
        _CACHE_STORE.clear()
        print("🧹 Cache Manager: Cleared cache (Limit reached)", file=sys.stderr)
    _CACHE_STORE[key] = value

def clear_cache():
    _CACHE_STORE.clear()
