from .logging import logger
from config.constants import cacheFilePath
from typing import Any
import json
import os
import time

# Imgur links can expire or be deleted. Entries older than this are re-uploaded.
CACHE_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days

cache: dict[str, Any] = {}

def _is_entry_valid(entry: Any) -> bool:
	"""Return True if a cache entry is a well-formed, non-expired TTL wrapper."""
	return (
		isinstance(entry, dict)
		and "value" in entry
		and "expires" in entry
		and isinstance(entry["expires"], (int, float))
		and entry["expires"] > time.time()
	)

def _prune_expired() -> None:
	"""Remove all expired entries from the in-memory cache (does not save to disk)."""
	expired_keys = [k for k, v in cache.items() if not _is_entry_valid(v)]
	for key in expired_keys:
		del cache[key]

def loadCache() -> None:
	if not os.path.isfile(cacheFilePath):
		return
	try:
		with open(cacheFilePath, "r", encoding = "UTF-8") as cacheFile:
			cache.update(json.load(cacheFile))
	except:
		root, ext = os.path.splitext(cacheFilePath)
		os.rename(cacheFilePath, f"{root}-{time.time():.0f}.{ext}")
		logger.exception("Failed to parse the cache file. A new one will be created.")
		return
	_prune_expired()
	logger.debug("Cache loaded: %d valid entries", len(cache))

def getCacheKey(key: str) -> Any:
	entry = cache.get(key)
	if not _is_entry_valid(entry):
		return None
	return entry["value"]

def setCacheKey(key: str, value: Any) -> None:
	cache[key] = {
		"value": value,
		"expires": time.time() + CACHE_TTL_SECONDS,
	}
	_prune_expired()
	try:
		with open(cacheFilePath, "w", encoding = "UTF-8") as cacheFile:
			json.dump(cache, cacheFile, separators = (",", ":"))
	except:
		logger.exception("Failed to write to the cache file")
