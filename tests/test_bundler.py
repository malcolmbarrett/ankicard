import zipfile
from pathlib import Path
from ankicard.media.bundler import extract_from_zip, copy_media_file


class TestExtractFromZip:
    """Tests for ZIP extraction functionality."""

    def test_extract_image_and_audio(self, tmp_path):
        """Test extracting both image and audio from ZIP."""
        # Create a test ZIP file
        zip_path = tmp_path / "test.zip"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("image.jpg", b"fake_image_data")
            zf.writestr("audio.mp3", b"fake_audio_data")

        result = extract_from_zip(str(zip_path), str(output_dir))

        assert result["image"] is not None
        assert result["audio"] is not None
        assert Path(result["image"]).exists()
        assert Path(result["audio"]).exists()

    def test_extract_only_image(self, tmp_path):
        """Test extracting only image from ZIP."""
        zip_path = tmp_path / "test.zip"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("photo.png", b"fake_image_data")

        result = extract_from_zip(str(zip_path), str(output_dir))

        assert result["image"] is not None
        assert result["audio"] is None
        assert Path(result["image"]).exists()

    def test_extract_only_audio(self, tmp_path):
        """Test extracting only audio from ZIP."""
        zip_path = tmp_path / "test.zip"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("sound.mp3", b"fake_audio_data")

        result = extract_from_zip(str(zip_path), str(output_dir))

        assert result["image"] is None
        assert result["audio"] is not None
        assert Path(result["audio"]).exists()

    def test_extract_multiple_images_takes_first(self, tmp_path):
        """Test that only first image is extracted when multiple exist."""
        zip_path = tmp_path / "test.zip"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("image1.jpg", b"fake_image_1")
            zf.writestr("image2.png", b"fake_image_2")

        result = extract_from_zip(str(zip_path), str(output_dir))

        assert result["image"] is not None
        # Should only extract one
        extracted_images = list(output_dir.glob("*.jpg")) + list(
            output_dir.glob("*.png")
        )
        assert len(extracted_images) == 1

    def test_extract_empty_zip(self, tmp_path):
        """Test extracting from empty ZIP."""
        zip_path = tmp_path / "empty.zip"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with zipfile.ZipFile(zip_path, "w"):
            pass  # Empty ZIP

        result = extract_from_zip(str(zip_path), str(output_dir))

        assert result["image"] is None
        assert result["audio"] is None

    def test_extract_jpeg_extension(self, tmp_path):
        """Test that .jpeg extension is recognized."""
        zip_path = tmp_path / "test.zip"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("photo.jpeg", b"fake_image_data")

        result = extract_from_zip(str(zip_path), str(output_dir))

        assert result["image"] is not None

    def test_extract_mixed_files(self, tmp_path):
        """Test extracting from ZIP with mixed file types."""
        zip_path = tmp_path / "test.zip"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("document.txt", b"text data")
            zf.writestr("image.jpg", b"image data")
            zf.writestr("audio.mp3", b"audio data")
            zf.writestr("video.mp4", b"video data")

        result = extract_from_zip(str(zip_path), str(output_dir))

        assert result["image"] is not None
        assert result["audio"] is not None


class TestCopyMediaFile:
    """Tests for media file copying."""

    def test_copy_media_file_basic(self, tmp_path):
        """Test basic file copying with new filename."""
        source_file = tmp_path / "source.mp3"
        source_file.write_bytes(b"test audio data")

        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        result = copy_media_file(str(source_file), str(dest_dir), "new_name.mp3")

        result_path = Path(result)
        assert result_path.exists()
        assert result_path.name == "new_name.mp3"
        assert result_path.read_bytes() == b"test audio data"

    def test_copy_media_file_preserves_content(self, tmp_path):
        """Test that file content is preserved during copy."""
        source_file = tmp_path / "source.jpg"
        test_data = b"fake image data with special chars \x00\xff"
        source_file.write_bytes(test_data)

        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        result = copy_media_file(str(source_file), str(dest_dir), "copy.jpg")

        assert Path(result).read_bytes() == test_data

    def test_copy_media_file_different_extension(self, tmp_path):
        """Test copying file with different extension in new name."""
        source_file = tmp_path / "audio.mp3"
        source_file.write_bytes(b"audio data")

        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        result = copy_media_file(str(source_file), str(dest_dir), "renamed.mp3")

        assert Path(result).suffix == ".mp3"

    def test_copy_media_file_returns_path(self, tmp_path):
        """Test that copy returns the destination path as string."""
        source_file = tmp_path / "source.jpg"
        source_file.write_bytes(b"data")

        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()

        result = copy_media_file(str(source_file), str(dest_dir), "new.jpg")

        assert isinstance(result, str)
        assert "new.jpg" in result
