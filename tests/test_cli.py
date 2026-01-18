from click.testing import CliRunner
from unittest.mock import patch, Mock
from ankicard.cli import cli


class TestCLI:
    """Tests for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_version(self):
        """Test --version flag."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output

    def test_cli_help(self):
        """Test --help flag."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Anki card generator" in result.output
        assert "Commands:" in result.output


class TestFuriganaCommand:
    """Tests for furigana command."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("ankicard.cli.furigana.get_furigana")
    def test_furigana_basic(self, mock_get_furigana):
        """Test basic furigana command."""
        mock_get_furigana.return_value = "日本語[にほんご]"

        result = self.runner.invoke(cli, ["furigana", "日本語"])

        assert result.exit_code == 0
        assert "日本語[にほんご]" in result.output
        mock_get_furigana.assert_called_once_with("日本語")

    def test_furigana_help(self):
        """Test furigana command help."""
        result = self.runner.invoke(cli, ["furigana", "--help"])
        assert result.exit_code == 0
        assert "furigana" in result.output.lower()


class TestTranslateCommand:
    """Tests for translate command."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("ankicard.cli.translation.translate_to_english")
    def test_translate_basic(self, mock_translate):
        """Test basic translate command."""
        mock_translate.return_value = "Hello"

        result = self.runner.invoke(cli, ["translate", "こんにちは"])

        assert result.exit_code == 0
        assert "Hello" in result.output
        mock_translate.assert_called_once_with("こんにちは")

    def test_translate_help(self):
        """Test translate command help."""
        result = self.runner.invoke(cli, ["translate", "--help"])
        assert result.exit_code == 0
        assert "translation" in result.output.lower()


class TestAudioCommand:
    """Tests for audio command."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.audio.generate_audio")
    def test_audio_basic(self, mock_generate_audio, mock_settings):
        """Test basic audio command with gTTS."""
        mock_settings_instance = Mock()
        mock_settings_instance.media_dir = "anki_media"
        mock_settings_instance.openai_api_key = None  # No API key, use gTTS
        mock_settings.load.return_value = mock_settings_instance
        mock_generate_audio.return_value = "anki_media/test.mp3"

        result = self.runner.invoke(cli, ["audio", "こんにちは"])

        assert result.exit_code == 0
        assert "Generated audio:" in result.output
        mock_generate_audio.assert_called_once()

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.audio.generate_audio")
    def test_audio_with_output_option(self, mock_generate_audio, mock_settings):
        """Test audio command with custom output."""
        mock_settings_instance = Mock()
        mock_settings_instance.media_dir = "anki_media"
        mock_settings_instance.openai_api_key = None  # No API key, use gTTS
        mock_settings.load.return_value = mock_settings_instance
        mock_generate_audio.return_value = "custom.mp3"

        result = self.runner.invoke(cli, ["audio", "テスト", "--output", "custom.mp3"])

        assert result.exit_code == 0

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.audio.generate_audio")
    def test_audio_with_slow_flag(self, mock_generate_audio, mock_settings):
        """Test audio command with slow flag."""
        mock_settings_instance = Mock()
        mock_settings_instance.media_dir = "anki_media"
        mock_settings_instance.openai_api_key = None  # No API key, use gTTS
        mock_settings.load.return_value = mock_settings_instance
        mock_generate_audio.return_value = "test.mp3"

        result = self.runner.invoke(cli, ["audio", "難しい", "--slow"])

        assert result.exit_code == 0
        # Check that slow=True was passed
        call_kwargs = mock_generate_audio.call_args[1]
        assert call_kwargs.get("slow") is True


class TestImageCommand:
    """Tests for image command."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.translation.translate_to_english")
    @patch("ankicard.cli.image.generate_image")
    def test_image_basic(self, mock_generate_image, mock_translate, mock_settings):
        """Test basic image command."""
        mock_settings_instance = Mock()
        mock_settings_instance.media_dir = "anki_media"
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings.load.return_value = mock_settings_instance

        mock_translate.return_value = "cat"
        mock_generate_image.return_value = "test.jpg"

        result = self.runner.invoke(cli, ["image", "猫"])

        assert result.exit_code == 0
        assert "Generated image:" in result.output

    @patch("ankicard.cli.Settings")
    def test_image_no_api_key(self, mock_settings):
        """Test image command without API key."""
        mock_settings_instance = Mock()
        mock_settings_instance.openai_api_key = None
        mock_settings.load.return_value = mock_settings_instance

        result = self.runner.invoke(cli, ["image", "猫"])

        assert result.exit_code != 0
        assert "OPENAI_API_KEY" in result.output


class TestGenerateCommand:
    """Tests for generate command."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.translation.translate_to_english")
    @patch("ankicard.cli.furigana.get_furigana")
    @patch("ankicard.cli.audio.generate_audio")
    @patch("ankicard.cli.create_deck")
    @patch("ankicard.cli.create_note")
    @patch("ankicard.cli.export_package")
    @patch("ankicard.cli.generate_unique_id")
    @patch("ankicard.cli.generate_media_filenames")
    def test_generate_basic(
        self,
        mock_gen_filenames,
        mock_gen_id,
        mock_export,
        mock_create_note,
        mock_create_deck,
        mock_gen_audio,
        mock_get_furigana,
        mock_translate,
        mock_settings,
    ):
        """Test basic generate command."""
        # Setup mocks
        mock_settings_instance = Mock()
        mock_settings_instance.media_dir = "anki_media"
        mock_settings_instance.output_dir = "anki_cards"
        mock_settings_instance.openai_api_key = None
        mock_settings_instance.deck_name = "Test Deck"
        mock_settings_instance.deck_id = 123
        mock_settings.load.return_value = mock_settings_instance

        mock_gen_id.return_value = "abc123"
        mock_gen_filenames.return_value = {"audio": "test.mp3", "image": "test.jpg"}
        mock_translate.return_value = "test"
        mock_get_furigana.return_value = "テスト"
        mock_gen_audio.return_value = "test.mp3"

        mock_deck = Mock()
        mock_create_deck.return_value = mock_deck
        mock_note = Mock()
        mock_create_note.return_value = mock_note

        result = self.runner.invoke(cli, ["generate", "テスト", "--no-image"])

        assert result.exit_code == 0
        assert "Processing:" in result.output
        assert "Translation:" in result.output
        assert "Success!" in result.output

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.translation.translate_to_english")
    @patch("ankicard.cli.furigana.get_furigana")
    @patch("ankicard.cli.audio.generate_audio")
    @patch("ankicard.cli.create_deck")
    @patch("ankicard.cli.create_note")
    @patch("ankicard.cli.export_package")
    @patch("ankicard.cli.generate_unique_id")
    @patch("ankicard.cli.generate_media_filenames")
    def test_generate_with_no_audio_flag(
        self,
        mock_gen_filenames,
        mock_gen_id,
        mock_export,
        mock_create_note,
        mock_create_deck,
        mock_gen_audio,
        mock_get_furigana,
        mock_translate,
        mock_settings,
    ):
        """Test generate command with --no-audio flag."""
        mock_settings_instance = Mock()
        mock_settings_instance.media_dir = "anki_media"
        mock_settings_instance.output_dir = "anki_cards"
        mock_settings_instance.openai_api_key = None
        mock_settings_instance.deck_name = "Test"
        mock_settings_instance.deck_id = 123
        mock_settings.load.return_value = mock_settings_instance

        mock_gen_id.return_value = "abc123"
        mock_gen_filenames.return_value = {"audio": "test.mp3", "image": "test.jpg"}
        mock_translate.return_value = "test"
        mock_get_furigana.return_value = "テスト"

        mock_deck = Mock()
        mock_create_deck.return_value = mock_deck
        mock_note = Mock()
        mock_create_note.return_value = mock_note

        result = self.runner.invoke(
            cli, ["generate", "テスト", "--no-audio", "--no-image"]
        )

        assert result.exit_code == 0
        # Audio generation should not be called
        mock_gen_audio.assert_not_called()


class TestTranscribeCommand:
    """Tests for transcribe command."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.transcription.transcribe_audio")
    @patch("ankicard.cli.transcription.validate_audio_file")
    def test_transcribe_basic(self, mock_validate, mock_transcribe, mock_settings):
        """Test basic transcribe command."""
        mock_settings_instance = Mock()
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings.load.return_value = mock_settings_instance
        mock_validate.return_value = True
        mock_transcribe.return_value = "こんにちは"

        with self.runner.isolated_filesystem():
            # Create fake audio file
            from pathlib import Path

            Path("test.mp3").touch()
            result = self.runner.invoke(cli, ["transcribe", "test.mp3"])

        assert result.exit_code == 0
        assert "こんにちは" in result.output
        mock_transcribe.assert_called_once_with("test.mp3", "test-key", "ja")

    @patch("ankicard.cli.Settings")
    def test_transcribe_no_api_key(self, mock_settings):
        """Test transcribe without API key."""
        mock_settings_instance = Mock()
        mock_settings_instance.openai_api_key = None
        mock_settings.load.return_value = mock_settings_instance

        with self.runner.isolated_filesystem():
            from pathlib import Path

            Path("test.mp3").touch()
            result = self.runner.invoke(cli, ["transcribe", "test.mp3"])

        assert result.exit_code != 0
        assert "OPENAI_API_KEY" in result.output

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.transcription.validate_audio_file")
    def test_transcribe_invalid_file(self, mock_validate, mock_settings):
        """Test transcribe with invalid audio file."""
        mock_settings_instance = Mock()
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings.load.return_value = mock_settings_instance
        mock_validate.return_value = False

        with self.runner.isolated_filesystem():
            from pathlib import Path

            Path("test.txt").touch()
            result = self.runner.invoke(cli, ["transcribe", "test.txt"])

        assert result.exit_code != 0
        assert "Invalid or unsupported audio file" in result.output

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.transcription.transcribe_audio")
    @patch("ankicard.cli.transcription.validate_audio_file")
    def test_transcribe_with_output(
        self, mock_validate, mock_transcribe, mock_settings
    ):
        """Test transcribe command with output file."""
        mock_settings_instance = Mock()
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings.load.return_value = mock_settings_instance
        mock_validate.return_value = True
        mock_transcribe.return_value = "日本語のテスト"

        with self.runner.isolated_filesystem():
            from pathlib import Path

            Path("test.mp3").touch()
            result = self.runner.invoke(
                cli, ["transcribe", "test.mp3", "--output", "out.txt"]
            )

            assert result.exit_code == 0
            assert "Saved transcription to: out.txt" in result.output
            # Check file was created
            assert Path("out.txt").exists()


class TestGenerateWithAudio:
    """Tests for generate command with audio transcription."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.transcription.transcribe_audio")
    @patch("ankicard.cli.translation.translate_to_english")
    @patch("ankicard.cli.furigana.get_furigana")
    @patch("ankicard.cli.create_deck")
    @patch("ankicard.cli.create_note")
    @patch("ankicard.cli.export_package")
    @patch("ankicard.cli.audio.generate_audio")
    @patch("ankicard.cli.generate_unique_id")
    @patch("ankicard.cli.generate_media_filenames")
    def test_generate_from_audio(
        self,
        mock_gen_filenames,
        mock_gen_id,
        mock_gen_audio,
        mock_export,
        mock_create_note,
        mock_create_deck,
        mock_get_furigana,
        mock_translate,
        mock_transcribe,
        mock_settings,
    ):
        """Test generate command with --from-audio flag."""
        mock_settings_instance = Mock()
        mock_settings_instance.media_dir = "anki_media"
        mock_settings_instance.output_dir = "anki_cards"
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings_instance.deck_name = "Test Deck"
        mock_settings_instance.deck_id = 123
        mock_settings.load.return_value = mock_settings_instance

        mock_gen_id.return_value = "abc123"
        mock_gen_filenames.return_value = {"audio": "test.mp3", "image": "test.jpg"}
        mock_transcribe.return_value = "日本語のテスト"
        mock_translate.return_value = "Japanese test"
        mock_get_furigana.return_value = "日本語[にほんご]のテスト"
        mock_gen_audio.return_value = "anki_media/test.mp3"

        mock_deck = Mock()
        mock_create_deck.return_value = mock_deck
        mock_note = Mock()
        mock_create_note.return_value = mock_note

        with self.runner.isolated_filesystem():
            from pathlib import Path

            Path("test.mp3").write_bytes(b"fake audio")
            result = self.runner.invoke(
                cli,
                ["generate", "--from-audio", "test.mp3", "--no-image", "--no-ai-audio"],
            )

        assert result.exit_code == 0
        assert "Transcribing: test.mp3" in result.output
        assert "Transcribed: 日本語のテスト" in result.output
        mock_transcribe.assert_called_once_with("test.mp3", "test-key")

    @patch("ankicard.cli.Settings")
    @patch("ankicard.cli.transcription.transcribe_audio")
    @patch("ankicard.cli.translation.translate_to_english")
    @patch("ankicard.cli.furigana.get_furigana")
    @patch("ankicard.cli.create_deck")
    @patch("ankicard.cli.create_note")
    @patch("ankicard.cli.export_package")
    @patch("ankicard.cli.copy_media_file")
    @patch("ankicard.cli.generate_unique_id")
    @patch("ankicard.cli.generate_media_filenames")
    def test_generate_from_audio_use_original(
        self,
        mock_gen_filenames,
        mock_gen_id,
        mock_copy_media,
        mock_export,
        mock_create_note,
        mock_create_deck,
        mock_get_furigana,
        mock_translate,
        mock_transcribe,
        mock_settings,
    ):
        """Test generate with --use-original-audio flag."""
        mock_settings_instance = Mock()
        mock_settings_instance.media_dir = "anki_media"
        mock_settings_instance.output_dir = "anki_cards"
        mock_settings_instance.openai_api_key = "test-key"
        mock_settings_instance.deck_name = "Test Deck"
        mock_settings_instance.deck_id = 123
        mock_settings.load.return_value = mock_settings_instance

        mock_gen_id.return_value = "abc123"
        mock_gen_filenames.return_value = {"audio": "test.mp3", "image": "test.jpg"}
        mock_transcribe.return_value = "日本語のテスト"
        mock_translate.return_value = "Japanese test"
        mock_get_furigana.return_value = "日本語[にほんご]のテスト"
        mock_copy_media.return_value = "anki_media/test.mp3"

        mock_deck = Mock()
        mock_create_deck.return_value = mock_deck
        mock_note = Mock()
        mock_create_note.return_value = mock_note

        with self.runner.isolated_filesystem():
            from pathlib import Path

            Path("test.mp3").write_bytes(b"fake audio")
            result = self.runner.invoke(
                cli,
                [
                    "generate",
                    "--from-audio",
                    "test.mp3",
                    "--use-original-audio",
                    "--no-image",
                ],
            )

        assert result.exit_code == 0
        assert "Using original audio: test.mp3" in result.output
        mock_copy_media.assert_called_once()

    def test_generate_no_input(self):
        """Test generate without sentence or audio."""
        result = self.runner.invoke(cli, ["generate"])

        assert result.exit_code != 0
        assert "Provide <sentence>, --from-audio, or --from-audio-zip" in result.output
