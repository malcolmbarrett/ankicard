"""Tests for audio transcription module."""

import pytest
from unittest.mock import patch, Mock, mock_open
from ankicard.core.transcription import transcribe_audio, validate_audio_file


class TestTranscribeAudio:
    """Tests for transcribe_audio function."""

    @patch("ankicard.core.transcription.OpenAI")
    @patch("ankicard.core.transcription.Path.exists")
    def test_transcribe_audio_success(self, mock_exists, mock_openai_class):
        """Test successful transcription."""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_transcript = Mock()
        mock_transcript.strip.return_value = "こんにちは世界"
        mock_client.audio.transcriptions.create.return_value = mock_transcript

        with patch("builtins.open", mock_open(read_data=b"fake audio data")):
            result = transcribe_audio("test.mp3", "test-api-key")

        assert result == "こんにちは世界"
        mock_client.audio.transcriptions.create.assert_called_once()
        call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
        assert call_kwargs["model"] == "whisper-1"
        assert call_kwargs["language"] == "ja"
        assert call_kwargs["response_format"] == "text"

    def test_transcribe_audio_no_api_key(self):
        """Test transcription without API key."""
        with pytest.raises(ValueError, match="API key required"):
            transcribe_audio("test.mp3", None)

    @patch("ankicard.core.transcription.Path.exists")
    def test_transcribe_audio_file_not_found(self, mock_exists):
        """Test transcription with missing file."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            transcribe_audio("missing.mp3", "test-key")

    @patch("ankicard.core.transcription.OpenAI")
    @patch("ankicard.core.transcription.Path.exists")
    def test_transcribe_audio_api_error(self, mock_exists, mock_openai_class):
        """Test transcription API failure."""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")

        with patch("builtins.open", mock_open(read_data=b"fake audio")):
            with pytest.raises(Exception, match="Transcription failed"):
                transcribe_audio("test.mp3", "test-key")

    @patch("ankicard.core.transcription.OpenAI")
    @patch("ankicard.core.transcription.Path.exists")
    def test_transcribe_audio_with_language(self, mock_exists, mock_openai_class):
        """Test transcription with custom language."""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_transcript = Mock()
        mock_transcript.strip.return_value = "Hello world"
        mock_client.audio.transcriptions.create.return_value = mock_transcript

        with patch("builtins.open", mock_open(read_data=b"fake audio")):
            transcribe_audio("test.mp3", "test-key", language="en")

        call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
        assert call_kwargs["language"] == "en"

    @patch("ankicard.core.transcription.OpenAI")
    @patch("ankicard.core.transcription.Path.exists")
    def test_transcribe_audio_json_format(self, mock_exists, mock_openai_class):
        """Test transcription with JSON response format."""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_transcript = Mock()
        mock_text = Mock()
        mock_text.strip.return_value = "こんにちは"
        mock_transcript.text = mock_text
        mock_client.audio.transcriptions.create.return_value = mock_transcript

        with patch("builtins.open", mock_open(read_data=b"fake audio")):
            result = transcribe_audio("test.mp3", "test-key", response_format="json")

        assert result == "こんにちは"
        call_kwargs = mock_client.audio.transcriptions.create.call_args[1]
        assert call_kwargs["response_format"] == "json"


class TestValidateAudioFile:
    """Tests for validate_audio_file function."""

    @patch("ankicard.core.transcription.Path.exists")
    def test_validate_audio_file_mp3(self, mock_exists):
        """Test validation of MP3 file."""
        mock_exists.return_value = True
        assert validate_audio_file("test.mp3") is True

    @patch("ankicard.core.transcription.Path.exists")
    def test_validate_audio_file_wav(self, mock_exists):
        """Test validation of WAV file."""
        mock_exists.return_value = True
        assert validate_audio_file("test.wav") is True

    @patch("ankicard.core.transcription.Path.exists")
    def test_validate_audio_file_m4a(self, mock_exists):
        """Test validation of M4A file."""
        mock_exists.return_value = True
        assert validate_audio_file("test.m4a") is True

    @patch("ankicard.core.transcription.Path.exists")
    def test_validate_audio_file_webm(self, mock_exists):
        """Test validation of WEBM file."""
        mock_exists.return_value = True
        assert validate_audio_file("test.webm") is True

    @patch("ankicard.core.transcription.Path.exists")
    def test_validate_audio_file_case_insensitive(self, mock_exists):
        """Test validation is case insensitive."""
        mock_exists.return_value = True
        assert validate_audio_file("test.MP3") is True
        assert validate_audio_file("test.WaV") is True

    @patch("ankicard.core.transcription.Path.exists")
    def test_validate_audio_file_unsupported(self, mock_exists):
        """Test validation of unsupported format."""
        mock_exists.return_value = True
        assert validate_audio_file("test.txt") is False
        assert validate_audio_file("test.pdf") is False

    @patch("ankicard.core.transcription.Path.exists")
    def test_validate_audio_file_missing(self, mock_exists):
        """Test validation of missing file."""
        mock_exists.return_value = False
        assert validate_audio_file("missing.mp3") is False
