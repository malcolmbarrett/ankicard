from unittest.mock import Mock, patch
import pytest
from ankicard.core.translation import (
    translate_to_english,
    get_translator,
    translate_to_english_openai,
)


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

        result = translate_to_english(
            "中国でも戦国時代の墳墓からガラスが出土している。"
        )

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


class TestTranslateToEnglishOpenAI:
    """Tests for OpenAI Chat translation."""

    def test_translate_openai_no_api_key(self):
        """Test that ValueError is raised when no API key is provided."""
        with pytest.raises(ValueError, match="OpenAI API key required"):
            translate_to_english_openai("こんにちは", api_key=None)

    @patch("ankicard.core.translation.OpenAI")
    def test_translate_openai_success(self, mock_openai):
        """Test successful OpenAI translation."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock API response
        mock_message = Mock()
        mock_message.content = "Hello"
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        result = translate_to_english_openai("こんにちは", api_key="test-key")

        assert result == "Hello"
        mock_client.chat.completions.create.assert_called_once()

    @patch("ankicard.core.translation.OpenAI")
    def test_translate_openai_with_custom_model(self, mock_openai):
        """Test OpenAI translation with custom model."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_message = Mock()
        mock_message.content = "I am a student"
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        result = translate_to_english_openai(
            "私は学生です", api_key="test-key", model="gpt-4o"
        )

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"
        assert result == "I am a student"

    @patch("ankicard.core.translation.OpenAI")
    def test_translate_openai_api_error(self, mock_openai):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="OpenAI translation failed"):
            translate_to_english_openai("test", api_key="test-key")

    @patch("ankicard.core.translation.OpenAI")
    def test_translate_openai_empty_response(self, mock_openai):
        """Test error handling when API returns None content."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_message = Mock()
        mock_message.content = None
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        with pytest.raises(Exception, match="OpenAI returned empty translation"):
            translate_to_english_openai("test", api_key="test-key")

    @patch("ankicard.core.translation.OpenAI")
    def test_translate_openai_default_model(self, mock_openai):
        """Test that default model is used correctly."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_message = Mock()
        mock_message.content = "Good morning"
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        translate_to_english_openai("おはよう", api_key="test-key")

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-4o-mini"  # default
        assert call_kwargs["temperature"] == 0.3

    @patch("ankicard.core.translation.OpenAI")
    def test_translate_openai_system_prompt(self, mock_openai):
        """Test that correct system prompt is used."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_message = Mock()
        mock_message.content = "Test"
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        translate_to_english_openai("テスト", api_key="test-key")

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        messages = call_kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "translator" in messages[0]["content"].lower()
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "テスト"
