"""Tests for utils/cache.py — TTL-aware in-memory + disk cache."""

import json
import time
import pytest

from utils import cache as cache_module
from utils.cache import (
	CACHE_TTL_SECONDS,
	_is_entry_valid,
	_prune_expired,
	getCacheKey,
	setCacheKey,
)


@pytest.fixture(autouse=True)
def reset_cache(tmp_path, monkeypatch):
	"""Clear the in-memory cache and redirect disk writes to a temp file before each test."""
	cache_module.cache.clear()
	tmp_file = tmp_path / "cache.json"
	monkeypatch.setattr(cache_module, "cacheFilePath", str(tmp_file))
	yield
	cache_module.cache.clear()


class TestIsEntryValid:
	def test_valid_entry(self):
		entry = {"value": "https://i.imgur.com/abc.jpg", "expires": time.time() + 100}
		assert _is_entry_valid(entry) is True

	def test_expired_entry(self):
		entry = {"value": "url", "expires": time.time() - 1}
		assert _is_entry_valid(entry) is False

	def test_missing_value_key(self):
		entry = {"expires": time.time() + 100}
		assert _is_entry_valid(entry) is False

	def test_missing_expires_key(self):
		entry = {"value": "url"}
		assert _is_entry_valid(entry) is False

	def test_old_format_plain_string(self):
		# Pre-TTL cache entries were bare strings — must be treated as invalid
		assert _is_entry_valid("https://i.imgur.com/old.jpg") is False

	def test_none_is_invalid(self):
		assert _is_entry_valid(None) is False

	def test_non_numeric_expires(self):
		entry = {"value": "url", "expires": "not-a-number"}
		assert _is_entry_valid(entry) is False


class TestGetSetCacheKey:
	def test_set_and_get_roundtrip(self):
		setCacheKey("thumb/abc", "https://i.imgur.com/abc.jpg")
		assert getCacheKey("thumb/abc") == "https://i.imgur.com/abc.jpg"

	def test_missing_key_returns_none(self):
		assert getCacheKey("thumb/missing") is None

	def test_expired_entry_returns_none(self):
		# Inject an expired entry directly
		cache_module.cache["thumb/expired"] = {
			"value": "https://i.imgur.com/old.jpg",
			"expires": time.time() - 1,
		}
		assert getCacheKey("thumb/expired") is None

	def test_old_format_string_entry_returns_none(self):
		# Backwards-compat: old plain-string entries should be treated as missing
		cache_module.cache["thumb/old"] = "https://i.imgur.com/old.jpg"
		assert getCacheKey("thumb/old") is None

	def test_set_writes_to_disk(self, tmp_path, monkeypatch):
		cache_file = tmp_path / "cache.json"
		monkeypatch.setattr(cache_module, "cacheFilePath", str(cache_file))
		setCacheKey("key", "value")
		assert cache_file.exists()
		data = json.loads(cache_file.read_text())
		assert "key" in data
		assert data["key"]["value"] == "value"

	def test_set_prunes_expired_entries(self):
		# Plant an expired entry, then set a new one — expired should be gone
		cache_module.cache["stale"] = {"value": "old", "expires": time.time() - 1}
		setCacheKey("fresh", "new_value")
		assert "stale" not in cache_module.cache

	def test_ttl_is_roughly_30_days(self):
		setCacheKey("key", "value")
		entry = cache_module.cache["key"]
		expected_expiry = time.time() + CACHE_TTL_SECONDS
		# Allow 2 seconds of tolerance
		assert abs(entry["expires"] - expected_expiry) < 2


class TestPruneExpired:
	def test_removes_expired(self):
		cache_module.cache["old"] = {"value": "x", "expires": time.time() - 1}
		cache_module.cache["new"] = {"value": "y", "expires": time.time() + 100}
		_prune_expired()
		assert "old" not in cache_module.cache
		assert "new" in cache_module.cache

	def test_removes_old_format_strings(self):
		cache_module.cache["legacy"] = "https://i.imgur.com/legacy.jpg"
		_prune_expired()
		assert "legacy" not in cache_module.cache

	def test_empty_cache_no_error(self):
		_prune_expired()  # should not raise
