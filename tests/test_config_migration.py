"""
Tests for config migration logic in core/config.py.

These tests exercise the key-renaming and value-clamping that runs when an
old config file is loaded, without touching the filesystem.
"""

import pytest
from utils.dict import copyDict


# ---------------------------------------------------------------------------
# Helpers: replicate the migration logic from core/config.py loadConfig()
# so these tests have no side-effects and no external dependencies.
# ---------------------------------------------------------------------------

def _apply_migrations(display: dict) -> dict:
	"""
	Apply the same migrations that loadConfig() performs on the 'display' section.
	Returns the mutated display dict for convenience.
	"""
	if "hideTotalTime" in display:
		display["duration"] = not display["hideTotalTime"]
		del display["hideTotalTime"]
	if "useRemainingTime" in display:
		del display["useRemainingTime"]
	if "remainingTime" in display:
		del display["remainingTime"]
	if display.get("progressMode") not in ["off", "elapsed", "remaining", "bar"]:
		display["progressMode"] = "bar"
	return display


class TestKeyMigrations:
	def test_hideTotalTime_true_sets_duration_false(self):
		display = {"hideTotalTime": True, "progressMode": "bar"}
		_apply_migrations(display)
		assert display["duration"] is False
		assert "hideTotalTime" not in display

	def test_hideTotalTime_false_sets_duration_true(self):
		display = {"hideTotalTime": False, "progressMode": "bar"}
		_apply_migrations(display)
		assert display["duration"] is True
		assert "hideTotalTime" not in display

	def test_useRemainingTime_key_removed(self):
		display = {"useRemainingTime": True, "progressMode": "bar"}
		_apply_migrations(display)
		assert "useRemainingTime" not in display

	def test_remainingTime_key_removed(self):
		display = {"remainingTime": True, "progressMode": "bar"}
		_apply_migrations(display)
		assert "remainingTime" not in display

	def test_all_legacy_keys_removed_together(self):
		display = {
			"hideTotalTime": True,
			"useRemainingTime": True,
			"remainingTime": False,
			"progressMode": "bar",
		}
		_apply_migrations(display)
		assert "hideTotalTime" not in display
		assert "useRemainingTime" not in display
		assert "remainingTime" not in display

	def test_no_legacy_keys_leaves_display_unchanged(self):
		display = {"duration": True, "progressMode": "elapsed"}
		_apply_migrations(display)
		assert display["duration"] is True
		assert display["progressMode"] == "elapsed"


class TestProgressModeClamping:
	@pytest.mark.parametrize("valid_mode", ["off", "elapsed", "remaining", "bar"])
	def test_valid_modes_preserved(self, valid_mode):
		display = {"progressMode": valid_mode}
		_apply_migrations(display)
		assert display["progressMode"] == valid_mode

	@pytest.mark.parametrize("invalid_mode", ["unknown", "", "TRUE", "false", None, 42])
	def test_invalid_mode_clamped_to_bar(self, invalid_mode):
		display = {"progressMode": invalid_mode}
		_apply_migrations(display)
		assert display["progressMode"] == "bar"


class TestCopyDictWithDefaults:
	"""Verify that copyDict correctly merges a loaded config over the defaults."""

	def _defaults(self) -> dict:
		return {
			"logging": {"debug": False, "writeToFile": False},
			"display": {
				"duration": True,
				"progressMode": "bar",
				"paused": False,
				"posters": {"enabled": False, "imgurClientID": "", "maxSize": 256},
			},
			"users": [],
		}

	def test_user_value_overrides_default(self):
		defaults = self._defaults()
		loaded = {"display": {"duration": False}}
		copyDict(loaded, defaults)
		assert defaults["display"]["duration"] is False

	def test_sibling_default_preserved(self):
		defaults = self._defaults()
		loaded = {"display": {"duration": False}}
		copyDict(loaded, defaults)
		assert defaults["display"]["progressMode"] == "bar"

	def test_nested_poster_override(self):
		defaults = self._defaults()
		loaded = {"display": {"posters": {"enabled": True, "imgurClientID": "abc123"}}}
		copyDict(loaded, defaults)
		assert defaults["display"]["posters"]["enabled"] is True
		assert defaults["display"]["posters"]["imgurClientID"] == "abc123"
		assert defaults["display"]["posters"]["maxSize"] == 256  # default preserved

	def test_users_replaced(self):
		defaults = self._defaults()
		loaded = {"users": [{"token": "tok", "servers": [{"name": "MyServer"}]}]}
		copyDict(loaded, defaults)
		assert len(defaults["users"]) == 1
		assert defaults["users"][0]["token"] == "tok"
