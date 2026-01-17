from unittest.mock import Mock, patch
from ankicard.core.audio import generate_audio


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
