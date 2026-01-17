import pytest
from unittest.mock import Mock, patch
from ankicard.core.translation import translate_to_english, get_translator


class TestTranslateToEnglish:
    """Tests for translation functionality."""

    @patch("ankicard.core.translation.get_translator")
    def test_translate_simple_text(self, mock_get_translator):
        """Test basic translation."""
        mock_translator = Mock()
        mock_translator.translate.return_value = "Hello"
        mock_get_translator.return_value = mock_translator

        result = translate_to_english("こんにちは")

        assert result == "Hello"
        mock_translator.translate.assert_called_once_with("こんにちは")

    @patch("ankicard.core.translation.get_translator")
    def test_translate_sentence(self, mock_get_translator):
        """Test translating a full sentence."""
        mock_translator = Mock()
        mock_translator.translate.return_value = "I am a student"
        mock_get_translator.return_value = mock_translator

        result = translate_to_english("私は学生です")

        assert result == "I am a student"

    @patch("ankicard.core.translation.get_translator")
    def test_translate_empty_string(self, mock_get_translator):
        """Test translating empty string."""
        mock_translator = Mock()
        mock_translator.translate.return_value = ""
        mock_get_translator.return_value = mock_translator

        result = translate_to_english("")

        assert result == ""

    @patch("ankicard.core.translation.get_translator")
    def test_translate_long_text(self, mock_get_translator):
        """Test translating longer text."""
        mock_translator = Mock()
        mock_translator.translate.return_value = "Glass has also been excavated from tombs of the Warring States period in China."
        mock_get_translator.return_value = mock_translator

        result = translate_to_english("中国でも戦国時代の墳墓からガラスが出土している。")

        assert "Glass" in result
        assert "China" in result


class TestGetTranslator:
    """Tests for translator singleton."""

    def test_translator_singleton(self):
        """Test that get_translator returns the same instance."""
        # Reset the global translator
        import ankicard.core.translation as translation_module
        translation_module._translator = None

        translator1 = get_translator()
        translator2 = get_translator()
        assert translator1 is translator2

    def test_translator_configuration(self):
        """Test that translator is configured for Japanese to English."""
        translator = get_translator()
        assert translator.source == "ja"
        assert translator.target == "en"
