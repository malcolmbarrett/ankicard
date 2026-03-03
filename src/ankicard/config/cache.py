"""Cache for tracking processed .apkg files."""

import json
import os
from pathlib import Path


CACHE_DIR = Path.home() / ".ankicard"
CACHE_FILE = CACHE_DIR / "processed_cache.json"


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def _file_key(path: str) -> str:
    """Generate a cache key from the absolute file path."""
    return str(Path(path).resolve())


def _file_signature(path: str) -> dict:
    """Get mtime and size for change detection."""
    stat = os.stat(path)
    return {"mtime": stat.st_mtime, "size": stat.st_size}


def is_cached(path: str) -> bool:
    """Check if a file has already been processed and hasn't changed."""
    key = _file_key(path)
    cache = _load_cache()
    if key not in cache:
        return False
    return cache[key] == _file_signature(path)


def mark_cached(path: str) -> None:
    """Mark a file as processed."""
    cache = _load_cache()
    cache[_file_key(path)] = _file_signature(path)
    _save_cache(cache)


def clear_cache() -> None:
    """Remove all cache entries."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
