import os
from unittest.mock import patch

from ankicard.config.cache import is_cached, mark_cached, clear_cache


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "test_apkg")


class TestCache:
    """Tests for processed file caching."""

    def _fixture(self):
        return os.path.join(FIXTURES_DIR, "anime_durarara___000000097.apkg")

    @patch("ankicard.config.cache.CACHE_FILE")
    @patch("ankicard.config.cache.CACHE_DIR")
    def test_uncached_file_returns_false(self, mock_dir, mock_file, tmp_path):
        mock_dir.__truediv__ = lambda self, x: tmp_path / x
        mock_file.__class__ = type(tmp_path / "cache.json")
        # Use a real tmp file that doesn't exist
        with patch("ankicard.config.cache.CACHE_FILE", tmp_path / "cache.json"):
            with patch("ankicard.config.cache.CACHE_DIR", tmp_path):
                assert is_cached(self._fixture()) is False

    @patch("ankicard.config.cache.CACHE_FILE")
    @patch("ankicard.config.cache.CACHE_DIR")
    def test_mark_and_check_cached(self, mock_dir, mock_file, tmp_path):
        cache_file = tmp_path / "cache.json"
        with patch("ankicard.config.cache.CACHE_FILE", cache_file):
            with patch("ankicard.config.cache.CACHE_DIR", tmp_path):
                fixture = self._fixture()
                assert is_cached(fixture) is False

                mark_cached(fixture)
                assert is_cached(fixture) is True

    @patch("ankicard.config.cache.CACHE_FILE")
    @patch("ankicard.config.cache.CACHE_DIR")
    def test_clear_cache(self, mock_dir, mock_file, tmp_path):
        cache_file = tmp_path / "cache.json"
        with patch("ankicard.config.cache.CACHE_FILE", cache_file):
            with patch("ankicard.config.cache.CACHE_DIR", tmp_path):
                mark_cached(self._fixture())
                assert cache_file.exists()

                clear_cache()
                assert not cache_file.exists()
                assert is_cached(self._fixture()) is False

    @patch("ankicard.config.cache.CACHE_FILE")
    @patch("ankicard.config.cache.CACHE_DIR")
    def test_cache_detects_file_change(self, mock_dir, mock_file, tmp_path):
        cache_file = tmp_path / "cache.json"
        test_file = tmp_path / "test.apkg"
        test_file.write_bytes(b"original")

        with patch("ankicard.config.cache.CACHE_FILE", cache_file):
            with patch("ankicard.config.cache.CACHE_DIR", tmp_path):
                mark_cached(str(test_file))
                assert is_cached(str(test_file)) is True

                # Modify the file (different size)
                test_file.write_bytes(b"modified content")
                assert is_cached(str(test_file)) is False
