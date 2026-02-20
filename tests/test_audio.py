from unittest.mock import Mock, patch
import pytest
import requests
from ankicard.core.audio import (
    generate_audio,
    generate_audio_voicevox,
    is_docker_running,
    is_ffmpeg_available,
    is_voicevox_available,
    start_voicevox_docker,
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


class TestIsVoicevoxAvailable:
    """Tests for VOICEVOX availability check."""

    @patch("ankicard.core.audio.requests.get")
    def test_voicevox_available(self, mock_get):
        """Test returns True when VOICEVOX is running."""
        mock_get.return_value = Mock(status_code=200)
        assert is_voicevox_available() is True
        mock_get.assert_called_once_with(
            "http://127.0.0.1:50021/version", timeout=2
        )

    @patch("ankicard.core.audio.requests.get")
    def test_voicevox_available_custom_url(self, mock_get):
        """Test with custom base URL."""
        mock_get.return_value = Mock(status_code=200)
        assert is_voicevox_available("http://localhost:50121") is True
        mock_get.assert_called_once_with(
            "http://localhost:50121/version", timeout=2
        )

    @patch("ankicard.core.audio.requests.get")
    def test_voicevox_not_available_connection_error(self, mock_get):
        """Test returns False when VOICEVOX is not reachable."""
        mock_get.side_effect = requests.ConnectionError()
        assert is_voicevox_available() is False

    @patch("ankicard.core.audio.requests.get")
    def test_voicevox_not_available_timeout(self, mock_get):
        """Test returns False when VOICEVOX times out."""
        mock_get.side_effect = requests.Timeout()
        assert is_voicevox_available() is False


class TestIsDockerRunning:
    """Tests for Docker daemon check."""

    @patch("ankicard.core.audio.subprocess.run")
    def test_docker_running(self, mock_run):
        """Test returns True when Docker daemon is running."""
        mock_run.return_value = Mock(returncode=0)
        assert is_docker_running() is True
        mock_run.assert_called_once_with(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5,
        )

    @patch("ankicard.core.audio.subprocess.run")
    def test_docker_not_running(self, mock_run):
        """Test returns False when Docker daemon is not running."""
        mock_run.return_value = Mock(returncode=1)
        assert is_docker_running() is False

    @patch("ankicard.core.audio.subprocess.run")
    def test_docker_not_installed(self, mock_run):
        """Test returns False when Docker is not installed."""
        mock_run.side_effect = FileNotFoundError()
        assert is_docker_running() is False

    @patch("ankicard.core.audio.subprocess.run")
    def test_docker_timeout(self, mock_run):
        """Test returns False when Docker command times out."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("docker", 5)
        assert is_docker_running() is False


class TestIsFfmpegAvailable:
    """Tests for ffmpeg availability check."""

    @patch("ankicard.core.audio.shutil.which")
    def test_ffmpeg_available(self, mock_which):
        """Test returns True when ffmpeg is on PATH."""
        mock_which.return_value = "/usr/local/bin/ffmpeg"
        assert is_ffmpeg_available() is True
        mock_which.assert_called_once_with("ffmpeg")

    @patch("ankicard.core.audio.shutil.which")
    def test_ffmpeg_not_available(self, mock_which):
        """Test returns False when ffmpeg is not on PATH."""
        mock_which.return_value = None
        assert is_ffmpeg_available() is False


class TestStartVoicevoxDocker:
    """Tests for Docker container management."""

    @patch("ankicard.core.audio.is_docker_running")
    @patch("ankicard.core.audio.is_voicevox_available")
    @patch("ankicard.core.audio.time.sleep")
    @patch("ankicard.core.audio.subprocess.run")
    def test_docker_not_running_returns_false(
        self, _mock_run, _mock_sleep, _mock_available, mock_docker
    ):
        """Test returns False when Docker daemon is not running."""
        mock_docker.return_value = False
        assert start_voicevox_docker() is False

    @patch("ankicard.core.audio.is_docker_running", return_value=True)
    @patch("ankicard.core.audio.is_voicevox_available")
    @patch("ankicard.core.audio.time.sleep")
    @patch("ankicard.core.audio.subprocess.run")
    def test_start_existing_container(
        self, mock_run, _mock_sleep, mock_available, _mock_docker
    ):
        """Test starting an existing stopped container."""
        mock_run.return_value = Mock(returncode=0)
        mock_available.return_value = True

        assert start_voicevox_docker() is True
        mock_run.assert_called_once_with(
            ["docker", "start", "voicevox"],
            capture_output=True,
            text=True,
        )

    @patch("ankicard.core.audio.is_docker_running", return_value=True)
    @patch("ankicard.core.audio.is_voicevox_available")
    @patch("ankicard.core.audio.time.sleep")
    @patch("ankicard.core.audio.subprocess.run")
    def test_create_new_container(
        self, mock_run, _mock_sleep, mock_available, _mock_docker
    ):
        """Test creating a new container when none exists."""
        # First call (docker start) fails, second (docker run) succeeds
        mock_run.side_effect = [
            Mock(returncode=1),
            Mock(returncode=0),
        ]
        mock_available.return_value = True

        assert start_voicevox_docker() is True
        assert mock_run.call_count == 2

    @patch("ankicard.core.audio.is_docker_running", return_value=True)
    @patch("ankicard.core.audio.is_voicevox_available")
    @patch("ankicard.core.audio.time.sleep")
    @patch("ankicard.core.audio.subprocess.run")
    def test_docker_run_fails(
        self, mock_run, _mock_sleep, _mock_available, _mock_docker
    ):
        """Test when both docker start and docker run fail."""
        mock_run.side_effect = [
            Mock(returncode=1),
            Mock(returncode=1),
        ]

        assert start_voicevox_docker() is False

    @patch("ankicard.core.audio.is_docker_running", return_value=True)
    @patch("ankicard.core.audio.is_voicevox_available")
    @patch("ankicard.core.audio.time.sleep")
    @patch("ankicard.core.audio.time.monotonic")
    @patch("ankicard.core.audio.subprocess.run")
    def test_polls_until_ready(
        self, mock_run, mock_monotonic, _mock_sleep, mock_available, _mock_docker
    ):
        """Test that it polls the health endpoint until ready."""
        mock_run.return_value = Mock(returncode=0)
        # Simulate: not ready, not ready, ready
        mock_available.side_effect = [False, False, True]
        # Simulate time progression within timeout
        mock_monotonic.side_effect = [0, 0, 2, 4]

        assert start_voicevox_docker(timeout=60) is True
        assert mock_available.call_count == 3

    @patch("ankicard.core.audio.is_docker_running", return_value=True)
    @patch("ankicard.core.audio.is_voicevox_available")
    @patch("ankicard.core.audio.time.sleep")
    @patch("ankicard.core.audio.time.monotonic")
    @patch("ankicard.core.audio.subprocess.run")
    def test_timeout_exceeded(
        self, mock_run, mock_monotonic, _mock_sleep, mock_available, _mock_docker
    ):
        """Test that it returns False when timeout is exceeded."""
        mock_run.return_value = Mock(returncode=0)
        mock_available.return_value = False
        # Time jumps past the deadline
        mock_monotonic.side_effect = [0, 0, 61]

        assert start_voicevox_docker(timeout=60) is False


class TestGenerateAudioVoicevox:
    """Tests for VOICEVOX TTS audio generation."""

    @patch("ankicard.core.audio.is_ffmpeg_available", return_value=False)
    def test_generate_audio_voicevox_no_ffmpeg(self, _mock_ffmpeg, test_audio_path):
        """Test error when ffmpeg is not installed."""
        with pytest.raises(Exception, match="ffmpeg is not installed"):
            generate_audio_voicevox("test", test_audio_path)

    @patch("ankicard.core.audio.is_ffmpeg_available", return_value=True)
    @patch("ankicard.core.audio.os.unlink")
    @patch("ankicard.core.audio.subprocess.run")
    @patch("ankicard.core.audio.requests.post")
    @patch("ankicard.core.audio.tempfile.NamedTemporaryFile")
    def test_generate_audio_voicevox_success(
        self, mock_tmpfile, mock_post, mock_subproc_run, mock_unlink,
        _mock_ffmpeg, test_audio_path
    ):
        """Test successful VOICEVOX TTS generation."""
        # Mock tempfile
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/fake.wav"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=False)
        mock_tmpfile.return_value = mock_tmp

        # Mock audio_query response
        mock_query_response = Mock()
        mock_query_response.json.return_value = {
            "speedScale": 1.0,
            "intonationScale": 1.0,
            "prePhonemeLength": 0.1,
            "postPhonemeLength": 0.1,
        }
        # Mock synthesis response
        mock_synth_response = Mock()
        mock_synth_response.content = b"fake wav data"

        mock_post.side_effect = [mock_query_response, mock_synth_response]

        # Mock ffmpeg subprocess
        mock_subproc_run.return_value = Mock(returncode=0)

        result = generate_audio_voicevox("こんにちは", test_audio_path)

        assert result == test_audio_path
        assert mock_post.call_count == 2
        mock_tmp.write.assert_called_once_with(b"fake wav data")
        mock_subproc_run.assert_called_once()
        mock_unlink.assert_called_once_with("/tmp/fake.wav")

    @patch("ankicard.core.audio.is_ffmpeg_available", return_value=True)
    @patch("ankicard.core.audio.os.unlink")
    @patch("ankicard.core.audio.subprocess.run")
    @patch("ankicard.core.audio.requests.post")
    @patch("ankicard.core.audio.tempfile.NamedTemporaryFile")
    def test_generate_audio_voicevox_custom_params(
        self, mock_tmpfile, mock_post, mock_subproc_run, mock_unlink,
        _mock_ffmpeg, test_audio_path
    ):
        """Test VOICEVOX with custom speaker and speed."""
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/fake.wav"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=False)
        mock_tmpfile.return_value = mock_tmp

        mock_query_response = Mock()
        mock_query_response.json.return_value = {
            "speedScale": 1.0,
            "intonationScale": 1.0,
            "prePhonemeLength": 0.1,
            "postPhonemeLength": 0.1,
        }
        mock_synth_response = Mock()
        mock_synth_response.content = b"fake wav"
        mock_post.side_effect = [mock_query_response, mock_synth_response]
        mock_subproc_run.return_value = Mock(returncode=0)

        generate_audio_voicevox(
            "テスト", test_audio_path, speaker_id=2, speed=1.0
        )

        # Verify audio_query call used correct speaker
        query_call = mock_post.call_args_list[0]
        assert query_call[1]["params"]["speaker"] == 2
        # Verify synthesis call used correct speaker
        synth_call = mock_post.call_args_list[1]
        assert synth_call[1]["params"]["speaker"] == 2

    @patch("ankicard.core.audio.is_ffmpeg_available", return_value=True)
    @patch("ankicard.core.audio.requests.post")
    def test_generate_audio_voicevox_query_fails(
        self, mock_post, _mock_ffmpeg, test_audio_path
    ):
        """Test error handling when audio_query fails."""
        mock_post.side_effect = Exception("Connection refused")
        with pytest.raises(Exception, match="VOICEVOX TTS failed"):
            generate_audio_voicevox("test", test_audio_path)

    @patch("ankicard.core.audio.is_ffmpeg_available", return_value=True)
    @patch("ankicard.core.audio.os.unlink")
    @patch("ankicard.core.audio.subprocess.run")
    @patch("ankicard.core.audio.requests.post")
    @patch("ankicard.core.audio.tempfile.NamedTemporaryFile")
    def test_generate_audio_voicevox_applies_learner_settings(
        self, mock_tmpfile, mock_post, mock_subproc_run, mock_unlink,
        _mock_ffmpeg, test_audio_path
    ):
        """Test that learner-friendly audio query settings are applied."""
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/fake.wav"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=False)
        mock_tmpfile.return_value = mock_tmp

        audio_query = {
            "speedScale": 1.0,
            "intonationScale": 1.0,
            "prePhonemeLength": 0.1,
            "postPhonemeLength": 0.1,
        }
        mock_query_response = Mock()
        mock_query_response.json.return_value = audio_query
        mock_synth_response = Mock()
        mock_synth_response.content = b"fake wav"
        mock_post.side_effect = [mock_query_response, mock_synth_response]
        mock_subproc_run.return_value = Mock(returncode=0)

        generate_audio_voicevox("テスト", test_audio_path, speed=0.85)

        # Verify the synthesis call used modified audio_query
        synth_call = mock_post.call_args_list[1]
        sent_query = synth_call[1]["json"]
        assert sent_query["speedScale"] == 0.85
        assert sent_query["intonationScale"] == 1.2
        assert sent_query["prePhonemeLength"] == 0.3
        assert sent_query["postPhonemeLength"] == 0.5

    @patch("ankicard.core.audio.is_ffmpeg_available", return_value=True)
    @patch("ankicard.core.audio.os.unlink")
    @patch("ankicard.core.audio.subprocess.run")
    @patch("ankicard.core.audio.requests.post")
    @patch("ankicard.core.audio.tempfile.NamedTemporaryFile")
    @patch("ankicard.core.audio.os.makedirs")
    def test_generate_audio_voicevox_creates_directory(
        self, mock_makedirs, mock_tmpfile, mock_post, mock_subproc_run, mock_unlink,
        _mock_ffmpeg, tmp_path,
    ):
        """Test that output directory is created if it doesn't exist."""
        nested_path = tmp_path / "nested" / "dir" / "audio.mp3"

        mock_tmp = Mock()
        mock_tmp.name = "/tmp/fake.wav"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=False)
        mock_tmpfile.return_value = mock_tmp

        mock_query_response = Mock()
        mock_query_response.json.return_value = {
            "speedScale": 1.0,
            "intonationScale": 1.0,
            "prePhonemeLength": 0.1,
            "postPhonemeLength": 0.1,
        }
        mock_synth_response = Mock()
        mock_synth_response.content = b"fake wav"
        mock_post.side_effect = [mock_query_response, mock_synth_response]
        mock_subproc_run.return_value = Mock(returncode=0)

        generate_audio_voicevox("テスト", str(nested_path))
        mock_makedirs.assert_called()

    @patch("ankicard.core.audio.is_ffmpeg_available", return_value=True)
    @patch("ankicard.core.audio.os.unlink")
    @patch("ankicard.core.audio.subprocess.run")
    @patch("ankicard.core.audio.requests.post")
    @patch("ankicard.core.audio.tempfile.NamedTemporaryFile")
    def test_generate_audio_voicevox_ffmpeg_fails(
        self, mock_tmpfile, mock_post, mock_subproc_run, mock_unlink,
        _mock_ffmpeg, test_audio_path
    ):
        """Test error handling when ffmpeg conversion fails."""
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/fake.wav"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=False)
        mock_tmpfile.return_value = mock_tmp

        mock_query_response = Mock()
        mock_query_response.json.return_value = {
            "speedScale": 1.0,
            "intonationScale": 1.0,
            "prePhonemeLength": 0.1,
            "postPhonemeLength": 0.1,
        }
        mock_synth_response = Mock()
        mock_synth_response.content = b"fake wav"
        mock_post.side_effect = [mock_query_response, mock_synth_response]
        mock_subproc_run.return_value = Mock(returncode=1, stderr="codec error")

        with pytest.raises(Exception, match="VOICEVOX TTS failed"):
            generate_audio_voicevox("test", test_audio_path)

        # Temp file should still be cleaned up
        mock_unlink.assert_called_once_with("/tmp/fake.wav")
