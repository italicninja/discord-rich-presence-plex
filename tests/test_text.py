"""Tests for utils/text.py — pure string utilities with no external I/O."""

import pytest
from utils.text import formatSeconds, truncate, transliterate, stripNonAscii


class TestFormatSeconds:
	def test_seconds_only(self):
		assert formatSeconds(45) == "45s"

	def test_minutes_and_seconds(self):
		assert formatSeconds(125) == "2m5s"

	def test_hours_minutes_seconds(self):
		assert formatSeconds(3661) == "1h1m1s"

	def test_exactly_one_hour(self):
		assert formatSeconds(3600) == "1h"

	def test_zero(self):
		assert formatSeconds(0) == ""

	def test_float_rounds(self):
		assert formatSeconds(1.6) == "2s"

	def test_joiner_minutes_seconds(self):
		assert formatSeconds(125, ":") == "02:05"

	def test_joiner_hours_minutes_seconds(self):
		assert formatSeconds(3661, ":") == "01:01:01"

	def test_joiner_omits_hours_when_zero(self):
		assert formatSeconds(65, ":") == "01:05"

	def test_joiner_exactly_one_minute(self):
		assert formatSeconds(60, ":") == "01:00"


class TestTruncate:
	def test_short_string_unchanged(self):
		assert truncate("hello", 10) == "hello"

	def test_exact_length_unchanged(self):
		assert truncate("hello", 5) == "hello"

	def test_long_string_truncated_with_ellipsis(self):
		result = truncate("hello world", 8)
		assert result == "hello..."
		assert len(result) == 8

	def test_truncation_at_boundary(self):
		# maxLength=4: first 1 char + "..."
		result = truncate("abcde", 4)
		assert result.endswith("...")
		assert len(result) == 4

	def test_empty_string(self):
		assert truncate("", 10) == ""

	def test_discord_limit_120(self):
		long = "x" * 130
		result = truncate(long, 120)
		assert len(result) == 120
		assert result.endswith("...")


class TestTransliterate:
	def test_ascii_passthrough(self):
		assert transliterate("Hello World") == "Hello World"

	def test_accented_latin(self):
		# é → e, ñ → n, etc.
		assert transliterate("café") == "cafe"
		assert transliterate("Ñoño") == "Nono"

	def test_chinese_transliterated(self):
		result = transliterate("北京")
		assert result  # non-empty
		assert all(ord(c) < 128 for c in result)  # all ASCII

	def test_arabic_transliterated(self):
		result = transliterate("مرحبا")
		assert all(ord(c) < 128 for c in result)

	def test_empty_string(self):
		assert transliterate("") == ""

	def test_stripNonAscii_alias(self):
		# The old name must remain importable and behave identically
		assert stripNonAscii("café") == transliterate("café")
