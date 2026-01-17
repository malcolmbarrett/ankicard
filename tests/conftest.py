import pytest
from pathlib import Path
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
