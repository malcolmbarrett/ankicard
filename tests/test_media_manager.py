from ankicard.media.manager import generate_unique_id, generate_media_filenames


class TestGenerateUniqueId:
    """Tests for unique ID generation."""

    def test_generate_unique_id_length(self):
        """Test that unique ID is 8 characters long."""
        unique_id = generate_unique_id()
        assert len(unique_id) == 8

    def test_generate_unique_id_is_string(self):
        """Test that unique ID is a string."""
        unique_id = generate_unique_id()
        assert isinstance(unique_id, str)

    def test_generate_unique_id_is_unique(self):
        """Test that multiple calls generate different IDs."""
        id1 = generate_unique_id()
        id2 = generate_unique_id()
        id3 = generate_unique_id()

        # IDs should be different (very high probability)
        assert id1 != id2
        assert id2 != id3
        assert id1 != id3

    def test_generate_unique_id_hex_characters(self):
        """Test that unique ID contains valid hex characters."""
        unique_id = generate_unique_id()
        # UUID4 hex representation should only contain 0-9, a-f, and hyphens
        # Our substring should only have hex chars (no hyphens in first 8 chars)
        assert all(c in "0123456789abcdef-" for c in unique_id)


class TestGenerateMediaFilenames:
    """Tests for media filename generation."""

    def test_generate_media_filenames_structure(self):
        """Test that filenames dict has correct structure."""
        filenames = generate_media_filenames("abc123")

        assert isinstance(filenames, dict)
        assert "audio" in filenames
        assert "image" in filenames

    def test_generate_media_filenames_audio(self):
        """Test audio filename format."""
        unique_id = "test123"
        filenames = generate_media_filenames(unique_id)

        assert filenames["audio"] == "anki_test123.mp3"

    def test_generate_media_filenames_image(self):
        """Test image filename format."""
        unique_id = "xyz789"
        filenames = generate_media_filenames(unique_id)

        assert filenames["image"] == "anki_xyz789.jpg"

    def test_generate_media_filenames_consistency(self):
        """Test that same ID produces same filenames."""
        unique_id = "same123"
        filenames1 = generate_media_filenames(unique_id)
        filenames2 = generate_media_filenames(unique_id)

        assert filenames1 == filenames2

    def test_generate_media_filenames_different_ids(self):
        """Test that different IDs produce different filenames."""
        filenames1 = generate_media_filenames("id1")
        filenames2 = generate_media_filenames("id2")

        assert filenames1["audio"] != filenames2["audio"]
        assert filenames1["image"] != filenames2["image"]

    def test_generate_media_filenames_extensions(self):
        """Test that extensions are correct."""
        filenames = generate_media_filenames("test")

        assert filenames["audio"].endswith(".mp3")
        assert filenames["image"].endswith(".jpg")

    def test_generate_media_filenames_prefix(self):
        """Test that filenames have correct prefix."""
        filenames = generate_media_filenames("test")

        assert filenames["audio"].startswith("anki_")
        assert filenames["image"].startswith("anki_")
