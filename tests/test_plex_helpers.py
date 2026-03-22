"""
Tests for pure helper logic in core/plex.py:
- buttonTypeGuidTypeMap correctness
- _resolveDynamicButtonUrl URL construction
- initiateAuth / getAuthToken validation logic (without network calls)
"""

import pytest
from unittest.mock import patch, MagicMock

from core.plex import buttonTypeGuidTypeMap


# ---------------------------------------------------------------------------
# We test _resolveDynamicButtonUrl by extracting its logic rather than
# instantiating PlexAlertListener (which connects to Plex in __init__).
# We do this by importing the method and calling it on a minimal namespace.
# ---------------------------------------------------------------------------

def _resolve(buttonType: str, mediaType: str, guids: dict) -> str:
	"""Thin wrapper around PlexAlertListener._resolveDynamicButtonUrl for testing."""
	from core.plex import PlexAlertListener
	return PlexAlertListener._resolveDynamicButtonUrl(None, buttonType, mediaType, guids)  # type: ignore[arg-type]


class TestButtonTypeGuidTypeMap:
	def test_all_expected_keys_present(self):
		expected = {"imdb", "tmdb", "thetvdb", "trakt", "letterboxd", "musicbrainz"}
		assert set(buttonTypeGuidTypeMap.keys()) == expected

	def test_trakt_and_letterboxd_use_tmdb_guid(self):
		# Both resolve via TMDB IDs
		assert buttonTypeGuidTypeMap["trakt"] == "tmdb"
		assert buttonTypeGuidTypeMap["letterboxd"] == "tmdb"

	def test_thetvdb_maps_to_tvdb(self):
		assert buttonTypeGuidTypeMap["thetvdb"] == "tvdb"

	def test_musicbrainz_maps_to_mbid(self):
		assert buttonTypeGuidTypeMap["musicbrainz"] == "mbid"


class TestResolveDynamicButtonUrl:
	def test_imdb_url(self):
		url = _resolve("imdb", "movie", {"imdb": "tt1234567"})
		assert url == "https://www.imdb.com/title/tt1234567"

	def test_tmdb_movie_url(self):
		url = _resolve("tmdb", "movie", {"tmdb": "12345"})
		assert url == "https://www.themoviedb.org/movie/12345"

	def test_tmdb_tv_url(self):
		url = _resolve("tmdb", "episode", {"tmdb": "67890"})
		assert url == "https://www.themoviedb.org/tv/67890"

	def test_thetvdb_movie(self):
		url = _resolve("thetvdb", "movie", {"tvdb": "999"})
		assert url == "https://www.thetvdb.com/dereferrer/movie/999"

	def test_thetvdb_series(self):
		url = _resolve("thetvdb", "episode", {"tvdb": "999"})
		assert url == "https://www.thetvdb.com/dereferrer/series/999"

	def test_trakt_movie(self):
		url = _resolve("trakt", "movie", {"tmdb": "555"})
		assert url == "https://trakt.tv/search/tmdb/555?id_type=movie"

	def test_trakt_show(self):
		url = _resolve("trakt", "episode", {"tmdb": "555"})
		assert url == "https://trakt.tv/search/tmdb/555?id_type=show"

	def test_letterboxd_movie(self):
		url = _resolve("letterboxd", "movie", {"tmdb": "777"})
		assert url == "https://letterboxd.com/tmdb/777"

	def test_letterboxd_not_shown_for_non_movie(self):
		# Letterboxd only makes sense for movies
		url = _resolve("letterboxd", "episode", {"tmdb": "777"})
		assert url == ""

	def test_musicbrainz_url(self):
		url = _resolve("musicbrainz", "track", {"mbid": "abc-123"})
		assert url == "https://musicbrainz.org/track/abc-123"

	def test_missing_guid_returns_empty(self):
		url = _resolve("imdb", "movie", {})  # no imdb guid
		assert url == ""

	def test_unknown_button_type_returns_empty(self):
		url = _resolve("rottentomatoes", "movie", {"tmdb": "123"})
		assert url == ""


class TestAuthValidation:
	"""Test that initiateAuth and getAuthToken validate API responses correctly."""

	def test_initiateAuth_raises_on_missing_id(self):
		mock_response = MagicMock()
		mock_response.raise_for_status = MagicMock()
		mock_response.json.return_value = {"code": "abc123"}  # missing 'id'

		with patch("core.plex.requests.post", return_value=mock_response):
			from core.plex import initiateAuth
			with pytest.raises(ValueError, match="missing 'id' or 'code'"):
				initiateAuth()

	def test_initiateAuth_raises_on_missing_code(self):
		mock_response = MagicMock()
		mock_response.raise_for_status = MagicMock()
		mock_response.json.return_value = {"id": 42}  # missing 'code'

		with patch("core.plex.requests.post", return_value=mock_response):
			from core.plex import initiateAuth
			with pytest.raises(ValueError, match="missing 'id' or 'code'"):
				initiateAuth()

	def test_initiateAuth_returns_tuple_on_success(self):
		mock_response = MagicMock()
		mock_response.raise_for_status = MagicMock()
		mock_response.json.return_value = {"id": 99, "code": "xyz"}

		with patch("core.plex.requests.post", return_value=mock_response):
			from core.plex import initiateAuth
			pin_id, code, auth_url = initiateAuth()
			assert pin_id == "99"
			assert code == "xyz"
			assert "xyz" in auth_url

	def test_getAuthToken_returns_none_for_null_token(self):
		mock_response = MagicMock()
		mock_response.raise_for_status = MagicMock()
		mock_response.json.return_value = {"authToken": None}

		with patch("core.plex.requests.get", return_value=mock_response):
			from core.plex import getAuthToken
			assert getAuthToken("1", "abc") is None

	def test_getAuthToken_returns_none_for_missing_key(self):
		mock_response = MagicMock()
		mock_response.raise_for_status = MagicMock()
		mock_response.json.return_value = {}

		with patch("core.plex.requests.get", return_value=mock_response):
			from core.plex import getAuthToken
			assert getAuthToken("1", "abc") is None

	def test_getAuthToken_returns_token_string(self):
		mock_response = MagicMock()
		mock_response.raise_for_status = MagicMock()
		mock_response.json.return_value = {"authToken": "HPbrz2NhfLRjU888Rrdt"}

		with patch("core.plex.requests.get", return_value=mock_response):
			from core.plex import getAuthToken
			assert getAuthToken("1", "abc") == "HPbrz2NhfLRjU888Rrdt"
