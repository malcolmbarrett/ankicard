from unittest.mock import Mock, patch
import pytest
from ankicard.core.audio import (
    generate_audio,
    generate_audio_openai,
    enhance_text_for_speech,
)


class TestGenerateAudio:
    """Tests for audio generation."""

    @patch("ankicard.core.audio.gTTS")
    def test_generate_audio_basic(self, mock_gtts, test_audio_path):
        """Test basic audio generation."""
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance

        result = generate_audio("こんにちは", test_audio_path)

        mock_gtts.assert_called_once_with(text="こんにちは", lang="ja", slow=False)
        mock_tts_instance.save.assert_called_once_with(test_audio_path)
        assert result == test_audio_path

    @patch("ankicard.core.audio.gTTS")
    def test_generate_audio_slow_mode(self, mock_gtts, test_audio_path):
        """Test audio generation with slow flag."""
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance

        result = generate_audio("難しい文章", test_audio_path, slow=True)

        mock_gtts.assert_called_once_with(text="難しい文章", lang="ja", slow=True)
        assert result == test_audio_path

    @patch("ankicard.core.audio.gTTS")
    def test_generate_audio_custom_language(self, mock_gtts, test_audio_path):
        """Test audio generation with custom language."""
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance

        result = generate_audio("Hello", test_audio_path, lang="en")

        mock_gtts.assert_called_once_with(text="Hello", lang="en", slow=False)
        assert result == test_audio_path

    @patch("ankicard.core.audio.gTTS")
    @patch("ankicard.core.audio.os.makedirs")
    def test_generate_audio_creates_directory(self, mock_makedirs, mock_gtts, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        nested_path = tmp_path / "nested" / "dir" / "audio.mp3"
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance

        generate_audio("テスト", str(nested_path))

        mock_makedirs.assert_called()

    @patch("ankicard.core.audio.gTTS")
    def test_generate_audio_with_japanese_sentence(self, mock_gtts, test_audio_path):
        """Test audio generation with a full Japanese sentence."""
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance

        sentence = "私は学生です"
        result = generate_audio(sentence, test_audio_path)

        mock_gtts.assert_called_once_with(text=sentence, lang="ja", slow=False)
        assert result == test_audio_path


class TestGenerateAudioOpenAI:
    """Tests for OpenAI TTS audio generation."""

    def test_generate_audio_openai_no_api_key(self, test_audio_path):
        """Test that ValueError is raised when no API key is provided."""
        with pytest.raises(ValueError, match="OpenAI API key required"):
            generate_audio_openai("こんにちは", test_audio_path, api_key=None)

    @patch("ankicard.core.audio.OpenAI")
    def test_generate_audio_openai_success(self, mock_openai, test_audio_path):
        """Test successful OpenAI TTS generation."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock streaming response with context manager
        mock_response = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_response)
        mock_context_manager.__exit__ = Mock(return_value=False)
        mock_client.audio.speech.with_streaming_response.create.return_value = (
            mock_context_manager
        )

        result = generate_audio_openai(
            "こんにちは", test_audio_path, api_key="test-key"
        )

        assert result == test_audio_path
        mock_client.audio.speech.with_streaming_response.create.assert_called_once()
        mock_response.stream_to_file.assert_called_once_with(test_audio_path)

    @patch("ankicard.core.audio.OpenAI")
    def test_generate_audio_openai_with_options(self, mock_openai, test_audio_path):
        """Test OpenAI TTS with custom voice, model, and speed."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock streaming response with context manager
        mock_response = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_response)
        mock_context_manager.__exit__ = Mock(return_value=False)
        mock_client.audio.speech.with_streaming_response.create.return_value = (
            mock_context_manager
        )

        result = generate_audio_openai(
            "テスト",
            test_audio_path,
            api_key="test-key",
            model="tts-1-hd",
            voice="nova",
            speed=1.5,
        )

        assert result == test_audio_path
        call_kwargs = mock_client.audio.speech.with_streaming_response.create.call_args[
            1
        ]
        assert call_kwargs["model"] == "tts-1-hd"
        assert call_kwargs["voice"] == "nova"
        assert call_kwargs["speed"] == 1.5
        assert call_kwargs["input"] == "テスト"

    @patch("ankicard.core.audio.OpenAI")
    def test_generate_audio_openai_api_error(self, mock_openai, test_audio_path):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.audio.speech.with_streaming_response.create.side_effect = Exception(
            "API Error"
        )

        with pytest.raises(Exception, match="OpenAI TTS failed"):
            generate_audio_openai("test", test_audio_path, api_key="test-key")

    @patch("ankicard.core.audio.OpenAI")
    def test_generate_audio_openai_default_params(self, mock_openai, test_audio_path):
        """Test that default parameters are used correctly."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock streaming response with context manager
        mock_response = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_response)
        mock_context_manager.__exit__ = Mock(return_value=False)
        mock_client.audio.speech.with_streaming_response.create.return_value = (
            mock_context_manager
        )

        generate_audio_openai("日本語", test_audio_path, api_key="test-key")

        call_kwargs = mock_client.audio.speech.with_streaming_response.create.call_args[
            1
        ]
        assert call_kwargs["model"] == "tts-1"  # default
        assert call_kwargs["voice"] == "alloy"  # default
        assert call_kwargs["speed"] == 1.0  # default


class TestEnhanceTextForSpeech:
    """Tests for text enhancement for TTS."""

    @patch("ankicard.core.audio.OpenAI")
    def test_enhance_text_adds_pauses(self, mock_openai):
        """Test that enhancement adds natural pauses."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_message = Mock()
        mock_message.content = "中国でも、戦国時代の墳墓から、ガラスが出土している。"
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        result = enhance_text_for_speech(
            "中国でも戦国時代の墳墓からガラスが出土している", "test-key"
        )

        assert "、" in result or "。" in result
        mock_client.chat.completions.create.assert_called_once()

    @patch("ankicard.core.audio.OpenAI")
    def test_enhance_text_fallback_on_error(self, mock_openai):
        """Test that original text is returned if enhancement fails."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        original_text = "こんにちは"
        result = enhance_text_for_speech(original_text, "test-key")

        assert result == original_text

    @patch("ankicard.core.audio.OpenAI")
    def test_enhance_text_system_prompt(self, mock_openai):
        """Test that correct prompt is used."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_message = Mock()
        mock_message.content = "テスト"
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        enhance_text_for_speech("テスト", "test-key")

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        messages = call_kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "punctuation" in messages[0]["content"].lower()
        assert "、。" in messages[0]["content"]
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "テスト"

    @patch("ankicard.core.audio.OpenAI")
    def test_enhance_text_none_response(self, mock_openai):
        """Test that original text is returned if API returns None."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_message = Mock()
        mock_message.content = None
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        original_text = "日本語"
        result = enhance_text_for_speech(original_text, "test-key")

        assert result == original_text


class TestGenerateAudioOpenAIWithEnhancement:
    """Tests for OpenAI TTS with text enhancement."""

    @patch("ankicard.core.audio.enhance_text_for_speech")
    @patch("ankicard.core.audio.OpenAI")
    def test_generate_audio_openai_with_enhancement(
        self, mock_openai, mock_enhance, test_audio_path
    ):
        """Test that enhancement is called when enabled."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock enhancement
        mock_enhance.return_value = "こんにちは、世界。"

        # Mock streaming response
        mock_response = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_response)
        mock_context_manager.__exit__ = Mock(return_value=False)
        mock_client.audio.speech.with_streaming_response.create.return_value = (
            mock_context_manager
        )

        result = generate_audio_openai(
            "こんにちは世界", test_audio_path, api_key="test-key", enhance=True
        )

        assert result == test_audio_path
        mock_enhance.assert_called_once_with("こんにちは世界", "test-key")

        # Verify enhanced text was passed to TTS
        call_kwargs = mock_client.audio.speech.with_streaming_response.create.call_args[
            1
        ]
        assert call_kwargs["input"] == "こんにちは、世界。"

    @patch("ankicard.core.audio.enhance_text_for_speech")
    @patch("ankicard.core.audio.OpenAI")
    def test_generate_audio_openai_without_enhancement(
        self, mock_openai, mock_enhance, test_audio_path
    ):
        """Test that enhancement is not called when disabled."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock streaming response
        mock_response = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_response)
        mock_context_manager.__exit__ = Mock(return_value=False)
        mock_client.audio.speech.with_streaming_response.create.return_value = (
            mock_context_manager
        )

        generate_audio_openai(
            "こんにちは", test_audio_path, api_key="test-key", enhance=False
        )

        mock_enhance.assert_not_called()

        # Verify original text was passed to TTS
        call_kwargs = mock_client.audio.speech.with_streaming_response.create.call_args[
            1
        ]
        assert call_kwargs["input"] == "こんにちは"
