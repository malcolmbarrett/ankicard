import pytest
from ankicard.config.settings import Settings


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test outputs."""
    return tmp_path


@pytest.fixture
def sample_japanese_text():
    """Standard test sentence."""
    return "日本語のテスト"


@pytest.fixture
def sample_japanese_with_kanji():
    """Japanese text with kanji for furigana testing."""
    return "私は学生です"


@pytest.fixture
def sample_katakana():
    """Sample katakana text."""
    return "カタカナ"


@pytest.fixture
def sample_hiragana():
    """Expected hiragana conversion."""
    return "かたかな"


@pytest.fixture
def mock_settings(tmp_path):
    """Settings object with temp directories."""
    return Settings(
        media_dir=str(tmp_path / "media"),
        output_dir=str(tmp_path / "cards"),
        openai_api_key="test-key-123",
    )


@pytest.fixture
def test_audio_path(tmp_path):
    """Path for test audio file."""
    return str(tmp_path / "test.mp3")


@pytest.fixture
def test_image_path(tmp_path):
    """Path for test image file."""
    return str(tmp_path / "test.jpg")


@pytest.fixture
def test_zip_path(tmp_path):
    """Path for test ZIP file."""
    return str(tmp_path / "test.zip")


@pytest.fixture
def sample_audio_file(tmp_path):
    """Create a fake audio file for testing."""
    audio_path = tmp_path / "test_audio.mp3"
    audio_path.write_bytes(b"fake mp3 data")
    return str(audio_path)


@pytest.fixture
def sample_audio_zip(tmp_path):
    """Create a ZIP with audio and image for testing."""
    import zipfile

    zip_path = tmp_path / "test_bundle.zip"
    audio_file = tmp_path / "audio.mp3"
    image_file = tmp_path / "image.jpg"

    audio_file.write_bytes(b"fake audio")
    image_file.write_bytes(b"fake image")

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(audio_file, "audio.mp3")
        zf.write(image_file, "image.jpg")

    return str(zip_path)


@pytest.fixture
def mock_transcription_response():
    """Mock OpenAI transcription response."""
    return "中国でも戦国時代の墳墓からガラスが出土している。"
