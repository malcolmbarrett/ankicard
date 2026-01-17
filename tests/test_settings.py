import pytest
import os
from unittest.mock import patch
from ankicard.config.settings import Settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_default_values(self):
        """Test that Settings has correct default values."""
        settings = Settings()

        assert settings.media_dir == "anki_media"
        assert settings.output_dir == "anki_cards"
        assert settings.openai_api_key is None
        assert settings.deck_id == 2059400110
        assert settings.deck_name == "Immersion Kit"

    def test_settings_custom_values(self):
        """Test creating Settings with custom values."""
        settings = Settings(
            media_dir="custom_media",
            output_dir="custom_output",
            openai_api_key="sk-test123",
            deck_id=9999,
            deck_name="Custom Deck",
        )

        assert settings.media_dir == "custom_media"
        assert settings.output_dir == "custom_output"
        assert settings.openai_api_key == "sk-test123"
        assert settings.deck_id == 9999
        assert settings.deck_name == "Custom Deck"

    @patch.dict(os.environ, {}, clear=True)
    @patch("ankicard.config.settings.load_dotenv")
    def test_settings_load_no_env_vars(self, mock_load_dotenv):
        """Test loading settings with no environment variables."""
        settings = Settings.load()

        mock_load_dotenv.assert_called_once()
        assert settings.media_dir == "anki_media"
        assert settings.output_dir == "anki_cards"
        assert settings.openai_api_key is None

    @patch.dict(
        os.environ,
        {
            "MEDIA_DIR": "env_media",
            "OUTPUT_DIR": "env_output",
            "OPENAI_API_KEY": "env-key-123",
        },
    )
    @patch("ankicard.config.settings.load_dotenv")
    def test_settings_load_with_env_vars(self, mock_load_dotenv):
        """Test loading settings from environment variables."""
        settings = Settings.load()

        assert settings.media_dir == "env_media"
        assert settings.output_dir == "env_output"
        assert settings.openai_api_key == "env-key-123"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "only-api-key"}, clear=True)
    @patch("ankicard.config.settings.load_dotenv")
    def test_settings_load_partial_env_vars(self, mock_load_dotenv):
        """Test loading with only some env vars set."""
        settings = Settings.load()

        # Should use env var for API key
        assert settings.openai_api_key == "only-api-key"
        # Should use defaults for others
        assert settings.media_dir == "anki_media"
        assert settings.output_dir == "anki_cards"

    @patch("ankicard.config.settings.os.makedirs")
    def test_ensure_directories_creates_dirs(self, mock_makedirs):
        """Test that ensure_directories creates both directories."""
        settings = Settings(media_dir="test_media", output_dir="test_output")

        settings.ensure_directories()

        assert mock_makedirs.call_count == 2
        calls = [call[0][0] for call in mock_makedirs.call_args_list]
        assert "test_media" in calls
        assert "test_output" in calls

    @patch("ankicard.config.settings.os.makedirs")
    def test_ensure_directories_exist_ok(self, mock_makedirs):
        """Test that ensure_directories uses exist_ok=True."""
        settings = Settings()

        settings.ensure_directories()

        for call in mock_makedirs.call_args_list:
            assert call[1]["exist_ok"] is True

    def test_settings_is_dataclass(self):
        """Test that Settings is a dataclass."""
        from dataclasses import is_dataclass

        assert is_dataclass(Settings)

    def test_settings_immutability_after_creation(self):
        """Test that settings can be modified after creation."""
        settings = Settings()
        settings.media_dir = "new_dir"
        assert settings.media_dir == "new_dir"
