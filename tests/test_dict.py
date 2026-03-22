"""Tests for utils/dict.py — deep merge utility."""

from utils.dict import copyDict


class TestCopyDict:
	def test_flat_copy(self):
		source = {"a": 1, "b": 2}
		target = {}
		copyDict(source, target)
		assert target == {"a": 1, "b": 2}

	def test_overwrites_existing_flat_key(self):
		source = {"a": 99}
		target = {"a": 1, "b": 2}
		copyDict(source, target)
		assert target["a"] == 99
		assert target["b"] == 2  # untouched

	def test_deep_merge_does_not_clobber_sibling_keys(self):
		source = {"display": {"duration": False}}
		target = {"display": {"duration": True, "year": True}}
		copyDict(source, target)
		assert target["display"]["duration"] is False
		assert target["display"]["year"] is True  # sibling preserved

	def test_deep_nested_merge(self):
		source = {"a": {"b": {"c": 42}}}
		target = {"a": {"b": {"c": 0, "d": 99}}}
		copyDict(source, target)
		assert target["a"]["b"]["c"] == 42
		assert target["a"]["b"]["d"] == 99

	def test_new_keys_added(self):
		source = {"new_key": "new_value"}
		target = {"existing": "value"}
		copyDict(source, target)
		assert target["new_key"] == "new_value"
		assert target["existing"] == "value"

	def test_list_value_overwritten_not_merged(self):
		# Lists are not deep-merged — they are replaced wholesale
		source = {"items": [3, 4]}
		target = {"items": [1, 2]}
		copyDict(source, target)
		assert target["items"] == [3, 4]

	def test_empty_source_leaves_target_unchanged(self):
		target = {"a": 1}
		copyDict({}, target)
		assert target == {"a": 1}

	def test_none_value_overwrites(self):
		source = {"key": None}
		target = {"key": "original"}
		copyDict(source, target)
		assert target["key"] is None
