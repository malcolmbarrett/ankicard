from unittest.mock import Mock, patch
from ankicard.core.image import generate_image


class TestGenerateImage:
    """Tests for Gemini image generation."""

    def test_generate_image_no_api_key(self, test_image_path):
        """Test that None is returned when no API key is provided."""
        result = generate_image("A cat", test_image_path, api_key=None)
        assert result is None

    @patch("ankicard.core.image.genai.Client")
    @patch("ankicard.core.image.os.makedirs")
    def test_generate_image_success(
        self, mock_makedirs, mock_client_cls, test_image_path
    ):
        """Test successful image generation."""
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        mock_image = Mock()
        mock_part = Mock()
        mock_part.inline_data = b"fake_image_data"
        mock_part.as_image.return_value = mock_image

        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        result = generate_image("A cute cat", test_image_path, api_key="test-key")

        assert result == test_image_path
        mock_client.models.generate_content.assert_called_once()
        mock_image.save.assert_called_once_with(test_image_path)

    @patch("ankicard.core.image.genai.Client")
    @patch("ankicard.core.image.os.makedirs")
    def test_generate_image_prompt_enhancement(
        self, mock_makedirs, mock_client_cls, test_image_path
    ):
        """Test that prompts are enhanced with minimalist instruction."""
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        mock_part = Mock()
        mock_part.inline_data = b"fake_image_data"
        mock_part.as_image.return_value = Mock()

        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        generate_image("mountain", test_image_path, api_key="test-key")

        call_kwargs = mock_client.models.generate_content.call_args[1]
        assert "mountain" in call_kwargs["contents"]
        assert "do not write out the full sentence" in call_kwargs["contents"]

    @patch("ankicard.core.image.genai.Client")
    @patch("ankicard.core.image.os.makedirs")
    def test_generate_image_parameters(
        self, mock_makedirs, mock_client_cls, test_image_path
    ):
        """Test that correct parameters are passed to Gemini."""
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        mock_part = Mock()
        mock_part.inline_data = b"fake_image_data"
        mock_part.as_image.return_value = Mock()

        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        generate_image("test prompt", test_image_path, api_key="test-key")

        call_kwargs = mock_client.models.generate_content.call_args[1]
        assert call_kwargs["model"] == "gemini-2.5-flash-image"
        assert call_kwargs["config"].response_modalities == ["IMAGE"]

    @patch("ankicard.core.image.genai.Client")
    @patch("ankicard.core.image.print")
    def test_generate_image_api_error(self, mock_print, mock_client_cls, test_image_path):
        """Test error handling when API call fails."""
        mock_client = Mock()
        mock_client_cls.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API Error")

        result = generate_image("test", test_image_path, api_key="test-key")

        assert result is None
        mock_print.assert_called_once()
        assert "Image generation failed" in str(mock_print.call_args)

    @patch("ankicard.core.image.genai.Client")
    @patch("ankicard.core.image.os.makedirs")
    @patch("ankicard.core.image.print")
    def test_generate_image_save_error(
        self, mock_print, mock_makedirs, mock_client_cls, test_image_path
    ):
        """Test error handling when image save fails."""
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        mock_image = Mock()
        mock_image.save.side_effect = Exception("Save Error")
        mock_part = Mock()
        mock_part.inline_data = b"fake_image_data"
        mock_part.as_image.return_value = mock_image

        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        result = generate_image("test", test_image_path, api_key="test-key")

        assert result is None
        mock_print.assert_called_once()

    @patch("ankicard.core.image.genai.Client")
    @patch("ankicard.core.image.print")
    def test_generate_image_no_image_in_response(
        self, mock_print, mock_client_cls, test_image_path
    ):
        """Test handling when response contains no image parts."""
        mock_client = Mock()
        mock_client_cls.return_value = mock_client

        mock_part = Mock()
        mock_part.inline_data = None

        mock_response = Mock()
        mock_response.parts = [mock_part]
        mock_client.models.generate_content.return_value = mock_response

        result = generate_image("test", test_image_path, api_key="test-key")

        assert result is None
        mock_print.assert_called_once()
        assert "no image in response" in str(mock_print.call_args)
