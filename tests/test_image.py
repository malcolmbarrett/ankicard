import pytest
from unittest.mock import Mock, patch, MagicMock
from ankicard.core.image import generate_image


class TestGenerateImage:
    """Tests for DALL-E image generation."""

    def test_generate_image_no_api_key(self, test_image_path):
        """Test that None is returned when no API key is provided."""
        result = generate_image("A cat", test_image_path, api_key=None)
        assert result is None

    @patch("ankicard.core.image.OpenAI")
    @patch("ankicard.core.image.requests.get")
    @patch("builtins.open", create=True)
    @patch("ankicard.core.image.os.makedirs")
    def test_generate_image_success(
        self, mock_makedirs, mock_open, mock_requests_get, mock_openai, test_image_path
    ):
        """Test successful image generation."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Mock API response
        mock_response = Mock()
        mock_response.data = [Mock(url="https://example.com/image.jpg")]
        mock_client.images.generate.return_value = mock_response

        # Mock image download
        mock_requests_get.return_value.content = b"fake_image_data"

        # Mock file writing
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = generate_image("A cute cat", test_image_path, api_key="test-key")

        assert result == test_image_path
        mock_client.images.generate.assert_called_once()
        mock_requests_get.assert_called_once_with("https://example.com/image.jpg")
        mock_file.write.assert_called_once_with(b"fake_image_data")

    @patch("ankicard.core.image.OpenAI")
    @patch("ankicard.core.image.requests.get")
    @patch("builtins.open", create=True)
    @patch("ankicard.core.image.os.makedirs")
    def test_generate_image_prompt_enhancement(
        self, mock_makedirs, mock_open, mock_requests_get, mock_openai, test_image_path
    ):
        """Test that prompts are enhanced with minimalist instruction."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [Mock(url="https://example.com/image.jpg")]
        mock_client.images.generate.return_value = mock_response

        mock_requests_get.return_value.content = b"fake_image_data"

        generate_image("mountain", test_image_path, api_key="test-key")

        # Check that the prompt was enhanced
        call_kwargs = mock_client.images.generate.call_args[1]
        assert "A simple, minimalist illustration representing: mountain" in call_kwargs["prompt"]

    @patch("ankicard.core.image.OpenAI")
    @patch("ankicard.core.image.requests.get")
    @patch("builtins.open", create=True)
    @patch("ankicard.core.image.os.makedirs")
    def test_generate_image_parameters(
        self, mock_makedirs, mock_open, mock_requests_get, mock_openai, test_image_path
    ):
        """Test that correct parameters are passed to DALL-E."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [Mock(url="https://example.com/image.jpg")]
        mock_client.images.generate.return_value = mock_response

        mock_requests_get.return_value.content = b"fake_image_data"

        generate_image("test prompt", test_image_path, api_key="test-key")

        call_kwargs = mock_client.images.generate.call_args[1]
        assert call_kwargs["model"] == "dall-e-3"
        assert call_kwargs["size"] == "1024x1024"
        assert call_kwargs["quality"] == "standard"
        assert call_kwargs["n"] == 1

    @patch("ankicard.core.image.OpenAI")
    @patch("ankicard.core.image.print")
    def test_generate_image_api_error(self, mock_print, mock_openai, test_image_path):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.images.generate.side_effect = Exception("API Error")

        result = generate_image("test", test_image_path, api_key="test-key")

        assert result is None
        mock_print.assert_called_once()
        assert "Image generation failed" in str(mock_print.call_args)

    @patch("ankicard.core.image.OpenAI")
    @patch("ankicard.core.image.requests.get")
    @patch("ankicard.core.image.print")
    def test_generate_image_download_error(
        self, mock_print, mock_requests_get, mock_openai, test_image_path
    ):
        """Test error handling when image download fails."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        mock_response = Mock()
        mock_response.data = [Mock(url="https://example.com/image.jpg")]
        mock_client.images.generate.return_value = mock_response

        mock_requests_get.side_effect = Exception("Download Error")

        result = generate_image("test", test_image_path, api_key="test-key")

        assert result is None
        mock_print.assert_called_once()
