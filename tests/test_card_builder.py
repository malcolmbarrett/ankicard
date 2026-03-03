from unittest.mock import Mock, patch
import genanki
from ankicard.anki.card_builder import (
    create_note,
    create_deck,
    create_all_decks,
    export_package,
)
from ankicard.anki.models import (
    IMMERSION_KIT_MODEL,
    DECK_ID_SENTENCES,
    DECK_ID_VOCAB,
    DECK_ID_KANJI,
    DECK_ID_GRAMMAR,
)


class TestCreateNote:
    """Tests for Anki note creation."""

    def test_create_note_with_all_fields(self):
        """Test creating a note with all fields populated."""
        note = create_note(
            expression="日本語",
            english="Japanese",
            reading="日本語[にほんご]",
            image_filename="test.jpg",
            audio_filename="test.mp3",
            unique_id="abc123",
        )

        assert isinstance(note, genanki.Note)
        assert note.model == IMMERSION_KIT_MODEL
        assert note.fields[0] == "日本語"  # Expression
        assert note.fields[1] == "Japanese"  # English
        assert note.fields[2] == "日本語[にほんご]"  # Reading
        assert note.fields[3] == '<img src="test.jpg">'  # Screenshot
        assert note.fields[4] == "[sound:test.mp3]"  # Audio Sentence
        assert note.fields[5] == "abc123"  # ID

    def test_create_note_without_image(self):
        """Test creating a note without an image."""
        note = create_note(
            expression="こんにちは",
            english="Hello",
            reading="こんにちは",
            image_filename=None,
            audio_filename="test.mp3",
            unique_id="xyz789",
        )

        assert note.fields[3] == ""  # Screenshot field should be empty
        assert note.fields[4] == "[sound:test.mp3]"

    def test_create_note_field_count(self):
        """Test that note has correct number of fields."""
        note = create_note(
            expression="テスト",
            english="Test",
            reading="テスト",
            image_filename="img.jpg",
            audio_filename="audio.mp3",
            unique_id="123",
        )

        assert len(note.fields) == 39
        # First 6 fields are populated, remaining 33 are empty padding
        assert all(f == "" for f in note.fields[6:])


class TestCreateDeck:
    """Tests for Anki deck creation."""

    def test_create_deck_default_values(self):
        """Test creating a deck with default values."""
        deck = create_deck()

        assert isinstance(deck, genanki.Deck)
        assert deck.deck_id == 1770225251447
        assert deck.name == "Immersion Kit::Sentences"

    def test_create_deck_custom_name(self):
        """Test creating a deck with custom name."""
        deck = create_deck(deck_name="My Custom Deck")

        assert deck.name == "My Custom Deck"
        assert deck.deck_id == 1770225251447

    def test_create_deck_custom_id(self):
        """Test creating a deck with custom ID."""
        custom_id = 9876543210
        deck = create_deck(deck_id=custom_id)

        assert deck.deck_id == custom_id

    def test_create_deck_custom_name_and_id(self):
        """Test creating a deck with both custom name and ID."""
        custom_id = 1111111111
        custom_name = "Test Deck"
        deck = create_deck(deck_name=custom_name, deck_id=custom_id)

        assert deck.deck_id == custom_id
        assert deck.name == custom_name


class TestCreateAllDecks:
    """Tests for creating all subdecks."""

    def test_creates_four_decks(self):
        """Test that create_all_decks returns 4 decks."""
        decks = create_all_decks()
        assert len(decks) == 4

    def test_deck_ids(self):
        """Test that decks have correct IDs."""
        decks = create_all_decks()
        assert decks[0].deck_id == DECK_ID_SENTENCES
        assert decks[1].deck_id == DECK_ID_VOCAB
        assert decks[2].deck_id == DECK_ID_KANJI
        assert decks[3].deck_id == DECK_ID_GRAMMAR

    def test_deck_names(self):
        """Test that decks have correct names."""
        decks = create_all_decks()
        assert decks[0].name == "Immersion Kit::Sentences"
        assert decks[1].name == "Immersion Kit::Components::Vocab"
        assert decks[2].name == "Immersion Kit::Components::Kanji"
        assert decks[3].name == "Immersion Kit::Components::Grammar"


class TestExportPackage:
    """Tests for Anki package export."""

    @patch("ankicard.anki.card_builder.genanki.Package")
    def test_export_package_with_media(self, mock_package_class, tmp_path):
        """Test exporting package with media files."""
        mock_package = Mock()
        mock_package_class.return_value = mock_package

        deck = create_deck()
        media_files = ["audio.mp3", "image.jpg"]
        output_path = str(tmp_path / "test.apkg")

        export_package(deck, media_files, output_path)

        mock_package_class.assert_called_once_with(deck)
        assert mock_package.media_files == media_files
        mock_package.write_to_file.assert_called_once_with(output_path)

    @patch("ankicard.anki.card_builder.genanki.Package")
    def test_export_package_without_media(self, mock_package_class, tmp_path):
        """Test exporting package without media files."""
        mock_package = Mock()
        mock_package_class.return_value = mock_package

        deck = create_deck()
        output_path = str(tmp_path / "test.apkg")

        export_package(deck, [], output_path)

        assert mock_package.media_files == []
        mock_package.write_to_file.assert_called_once_with(output_path)

    @patch("ankicard.anki.card_builder.genanki.Package")
    def test_export_package_with_single_media(self, mock_package_class, tmp_path):
        """Test exporting package with single media file."""
        mock_package = Mock()
        mock_package_class.return_value = mock_package

        deck = create_deck()
        media_files = ["audio.mp3"]
        output_path = str(tmp_path / "test.apkg")

        export_package(deck, media_files, output_path)

        assert mock_package.media_files == media_files

    @patch("ankicard.anki.card_builder.genanki.Package")
    def test_export_package_with_deck_list(self, mock_package_class, tmp_path):
        """Test exporting package with a list of decks."""
        mock_package = Mock()
        mock_package_class.return_value = mock_package

        decks = create_all_decks()
        output_path = str(tmp_path / "test.apkg")

        export_package(decks, [], output_path)

        mock_package_class.assert_called_once_with(decks)
        mock_package.write_to_file.assert_called_once_with(output_path)
